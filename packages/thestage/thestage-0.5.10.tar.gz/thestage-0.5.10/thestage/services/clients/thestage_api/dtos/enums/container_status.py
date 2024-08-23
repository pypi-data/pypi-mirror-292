from enum import Enum
from typing import List


class ContainerBussinessStatusEnumDto(str, Enum):
    FAILED: str = 'FAILED'
    BUSY: str = 'BUSY'
    DEAD: str = 'DEAD'
    CREATING: str = 'CREATING'
    CREATING_FAILED: str = 'CREATING_FAILED'
    STARTING: str = 'STARTING'
    RUNNING: str = 'RUNNING'
    STOPPING: str = 'STOPPING'
    STOPPED: str = 'STOPPED'
    RESTARTING: str = 'RESTARTING'
    DELETING: str = 'DELETING'
    DELETED: str = 'DELETED'
    UNKNOWN: str = 'UNKNOWN'
    ALL: str = 'ALL'

    @staticmethod
    def find_special_status(statuses: List['ContainerBussinessStatusEnumDto']) -> bool:
        q = list(filter(lambda x: True if x == ContainerBussinessStatusEnumDto.ALL else False, statuses))
        return True if q else False


class ContainerFrontendStatusEnumDto(str, Enum):
    terminated: str = 'terminated'
    unresponsive: str = 'unresponsive'
    creation_failed: str = 'creation_failed'
    exited: str = 'exited'
    starting: str = 'starting'
    running: str = 'running'
    terminating: str = 'terminating'
    stopped: str = 'stopped'
    stopping: str = 'stopping'
    unknown: str = 'unknown'
    all: str = 'all'

    @staticmethod
    def find_special_status(statuses: List['ContainerFrontendStatusEnumDto']) -> bool:
        q = list(filter(lambda x: True if x == ContainerFrontendStatusEnumDto.all else False, statuses))
        return True if q else False
