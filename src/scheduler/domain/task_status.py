from dataclasses import dataclass
from typing import Literal

Status = Literal['new','scheduled', 'paused', 'cancelled', 'finished', 'failed']

@dataclass
class TaskStatus:
    _status: Status = "new"

    @property
    def status(self):
        return self._status

    def set_scheduled(self):
        if self._status in ('cancelled', 'finished', 'failed'):
            ...

    def set_paused(self):
        ...

    def set_cancelled(self):
        ...

    def set_finished(self):
        ...

    def set_failed(self):
        ...



