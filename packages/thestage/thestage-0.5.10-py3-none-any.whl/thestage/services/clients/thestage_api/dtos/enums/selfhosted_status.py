from enum import Enum
from typing import List


class SelfHostedBusinessStatusEnumDto(str, Enum):

    AWAITING_CONFIGURATION: str = 'AWAITING_CONFIGURATION'
    RUNNING: str = 'RUNNING'
    TERMINATED: str = 'TERMINATED'
    DELETED: str = 'DELETED'
    UNKNOWN: str = 'UNKNOWN'
    ALL: str = 'ALL'

    @staticmethod
    def find_special_status(statuses: List['SelfHostedBusinessStatusEnumDto']) -> bool:
        q = list(filter(lambda x: True if x == SelfHostedBusinessStatusEnumDto.ALL else False, statuses))
        return True if q else False


class SelfHostedFrontendStatusEnumDto(str, Enum):
    terminated: str = 'terminated'
    awaiting_setup: str = 'awaiting_setup'
    online: str = 'online'
    deleted: str = 'deleted'
    unknown: str = 'unknown'
    all: str = 'all'

    @staticmethod
    def find_special_status(statuses: List['SelfHostedFrontendStatusEnumDto']) -> bool:
        q = list(filter(lambda x: True if x == SelfHostedFrontendStatusEnumDto.all else False, statuses))
        return True if q else False
