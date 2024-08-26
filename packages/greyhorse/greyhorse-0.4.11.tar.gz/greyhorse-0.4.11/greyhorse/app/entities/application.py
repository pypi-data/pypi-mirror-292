import asyncio
import signal
import threading
from asyncio import get_running_loop
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Collection, Optional, TYPE_CHECKING

from greyhorse.result import Result, Ok
from .module import Module
from ..abc.services import Service
from ...enum import Enum, Struct
from ...error import Error, ErrorCase
from ...i18n import tr
from ...logging import logger
from ...maybe import Maybe, Nothing
from ...utils.invoke import get_asyncio_loop, caller_path


class AppNotLoadedError(RuntimeError):
    pass


class ModuleInitError(Error):
    namespace = 'greyhorse.app.builder'

    Disabled = ErrorCase(msg='Module is disabled: "{path}"', path=str)
    NotLoaded = ErrorCase(msg='Module is not loaded: "{path}"', path=str)


class Application:
    def __init__(
        self, name: str, version: str = '', debug: bool = False,
    ):
        self._name = name
        self._version = version
        self._debug = debug
        self._path = self._inspect_cwd()
        self._services: dict[str, Service] = {}
        self._module: Maybe[Module] = Nothing

    @staticmethod
    def _inspect_cwd():
        import inspect

        for frame in reversed(inspect.stack()):
            path = Path(frame.filename).absolute()

            while path.parent != path:
                path = path.parent
                pyproject_toml_path = path / 'pyproject.toml'
                if pyproject_toml_path.exists():
                    return path

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def debug(self) -> bool:
        return self._debug

    def get_cwd(self) -> Path:
        return self._path.absolute()

    def register_service(self, name: str, instance: Service):
        self._services[name] = instance

    def unregister_service(self, name: str):
        self._services.pop(name, None)

    def get_module(self, name: str) -> Module | None:
        if value := self._modules.get(name):
            return value[0]
        return None

    def create(self) -> list[ModuleErrorsItem]:
        if self._module:
            return self._module.create()
        raise AppNotLoadedError()

    def destroy(self) -> list[ModuleErrorsItem]:
        if self._module:
            return self._module.destroy()
        raise AppNotLoadedError()

    def start(self):
        if self._module:
            return self._module.start()
        raise AppNotLoadedError()

    def stop(self):
        if self._module:
            return self._module.stop()
        raise AppNotLoadedError()

    def run_sync(self, callback: Callable[[], None] | None = None):
        sync_events: list[threading.Event] = []
        async_events: list[asyncio.Event] = []

        for name, srv in self._services.items():
            match srv.wait():
                case threading.Event() as event:
                    sync_events.append(event)
                case asyncio.Event() as event:
                    async_events.append(event)

        all_events = sync_events + async_events

        async def waiter():
            async with asyncio.TaskGroup() as tg:
                for e in async_events:
                    tg.create_task(e.wait())

        logger.info(tr('app.application.run-sync-start').format(name=self.name))

        while not all([e.is_set() for e in all_events]):
            if async_events:
                loop = get_running_loop()
                loop.run_until_complete(waiter())

            sync_events_bools = [e.wait(0.1) for e in sync_events]

            if callback and not all(sync_events_bools):
                callback()

        logger.info(tr('app.application.run-sync-stop').format(name=self.name))

    async def run_async(self):
        sync_events: list[threading.Event] = []
        async_events: list[asyncio.Event] = []

        for name, srv in self._services.items():
            match srv.wait():
                case threading.Event() as event:
                    sync_events.append(event)
                case asyncio.Event() as event:
                    async_events.append(event)

        all_events = sync_events + async_events

        logger.info(tr('app.application.run-async-start').format(name=self.name))

        while not all([e.is_set() for e in all_events]):
            async with asyncio.TaskGroup() as tg:
                for e in sync_events:
                    tg.create_task(asyncio.to_thread(e.wait, 0.1))
                for e in async_events:
                    tg.create_task(e.wait())

        logger.info(tr('app.application.run-async-stop').format(name=self.name))

    @contextmanager
    def graceful_exit(self, signals: Collection[int] = (signal.SIGINT, signal.SIGTERM)):
        signals = set(signals)
        flag: list[bool] = []

        if loop := get_asyncio_loop():
            for sig_num in signals:
                loop.add_signal_handler(sig_num, self._exit_handler, sig_num, flag)
            try:
                yield
            finally:
                for sig_num in signals:
                    loop.remove_signal_handler(sig_num)
        else:
            original_handlers = []

            for sig_num in signals:
                original_handlers.append(signal.getsignal(sig_num))
                signal.signal(sig_num, self._exit_handler)
            try:
                yield
            finally:
                for sig_num, handler in zip(signals, original_handlers):
                    signal.signal(sig_num, handler)

    def _exit_handler(self, sig_num: 'signal.Signals', flag: list[bool], *_) -> None:
        if flag:
            self._second_exit_stage(sig_num)
        else:
            self._first_exit_stage(sig_num)
            flag.append(True)

    def _first_exit_stage(self, sig_num: 'signal.Signals'):
        fail = False

        try:
            self.stop()
        except RuntimeError:
            fail = True

        if fail:
            self._second_exit_stage(sig_num)

    def _second_exit_stage(self, sig_num: 'signal.Signals'):
        raise SystemExit(128 + sig_num)
