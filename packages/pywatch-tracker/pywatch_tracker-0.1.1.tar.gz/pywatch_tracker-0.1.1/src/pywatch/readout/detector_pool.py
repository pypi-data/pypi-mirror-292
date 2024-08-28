import asyncio
from copy import deepcopy
from typing import Any, Callable, List, Optional, Union

import serial

from .detector import Detector
from .event_data_collection import EventData, EventDataCollection
from .pool_thread import PoolThread


# Type of callback function of DetectorPool.run() function
Callback = Union[Callable[[EventData, PoolThread, Any], Any], Callable[[EventData, PoolThread], Any]]


class DetectorPool:
    """Pool of multiple Detectors, which saves coincidence events, if multiple hits are registered in
    the threshold time."""

    def __init__(self, *ports: str, threshold: int = 10) -> None:
        self.threshold = threshold
        self._detectors = [Detector(port, False) for port in ports]
        self._index = -1

        self._thread = PoolThread()

        self._event_data: EventData = EventData()  # make this obsolete

        # stores all the events
        self._data = EventDataCollection()

        self._first_coincidence_hit_time = 0

    async def open(self) -> "DetectorPool":
        """Opens asynchronously all ports for data collection"""
        self._index = -1
        self._data.clear()
        self._first_coincidence_hit_time = 0
        await asyncio.gather(*[port.open() for port in self._detectors])

        return self

    async def close(self) -> None:
        await asyncio.gather(*[port.close() for port in self._detectors])

    @property
    def is_open(self) -> bool:
        return self._detectors[0].is_open

    @property
    def detector_count(self):
        return len(self._detectors)

    @property
    def get_ports(self) -> List[str]:
        """Get a list of ports from the used detectors. The index at which a port
        is returned corresponds to the index in the event list."""
        return [dt.port for dt in self._detectors]

    @property
    def event(self) -> int:
        return self._index + 1

    @property
    def data(self) -> EventDataCollection:
        return self._data

    def run(self, event_count: int, callback: Optional[Callback] = None, *args) -> (int, Optional[Exception]):
        try:
            asyncio.get_running_loop().run_until_complete(self.async_run(event_count, callback, *args))
            print("running loop")
        except RuntimeError:
            print("new loop")
            asyncio.run(self.async_run(event_count, callback, *args))

    async def async_run(self, event_count: int, callback: Optional[Callback] = None, *args) -> (
            int, Optional[Exception]):
        await self.open()
        if callback is not None:
            self._thread.start()
        finished = False
        counted_hits = 0
        lock = asyncio.Lock()

        async def run_detector(dt: Detector, dt_index: int) -> (int, Optional[Exception]):
            """reads hits asynchronously for the specified detector. if the hit time is not inside
            the threshold anymore, save the current event and begin a new one with the current hit time
            as first coincidence time."""
            nonlocal finished, counted_hits, lock
            exc = None

            while not finished:
                try:
                    await dt.measurement()
                except (asyncio.CancelledError, Exception, serial.SerialException) as e:
                    print(f"{e}")
                    finished = True
                    exc = e
                    break

                if dt[-1].comp_time - self._first_coincidence_hit_time <= self.threshold:
                    if dt_index in self._event_data.keys():
                        continue
                    self._event_data[dt_index] = dt[-1]
                else:
                    # print(self._event)
                    if len(self._event_data.keys()) > 1:
                        self._data.add_event(deepcopy(self._event_data))
                        if callback is not None:
                            coro = callback(self._event_data, self._thread, *args)
                            if asyncio.iscoroutinefunction(callback):
                                await coro

                        async with lock:
                            counted_hits += 1

                        # print(f"hit {counted_hits} / {hits}")
                    if counted_hits == event_count:
                        finished = True
                        break

                    self._first_coincidence_hit_time = dt[-1].comp_time
                    self._event_data.clear()
                    self._event_data[dt_index] = dt[-1]

            return counted_hits, exc

        async def measure_task() -> (int, Optional[Exception]):
            tasks = [
                asyncio.create_task(
                    run_detector(self._detectors[i], i)  # , name=self._detectors[i].port
                )
                for i in range(len(self._detectors))
            ]
            completed, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            for task in pending:
                task.cancel()

            return completed.pop().result()

        result = await measure_task()

        if callback is not None:
            self._thread.join()
        await self.close()
        return result

    def __len__(self) -> int:
        return len(self._data)

    async def __aenter__(self):
        if self.is_open:
            await self.close()
        await self.open()

        return self

    async def __aexit__(self, type_, value, traceback):
        await self.close()
