from typing import List, Optional

from pydantic import Field, ConfigDict, BaseModel

from thestage.services.clients.thestage_api.dtos.base_response import TheStageBaseResponse
from thestage.services.clients.thestage_api.dtos.pagination_data import PaginationData
from thestage.services.clients.thestage_api.dtos.task_response import TaskDto


class TaskListForProjectPaging(BaseModel):
    entities: List[TaskDto] = Field(default_factory=list, alias='entities')
    # current_page: Optional[int] = Field(None, alias='currentPage')
    # last_page: Optional[bool] = Field(None, alias='lastPage')
    # total_pages: Optional[int] = Field(None, alias='totalPages')
    pagination_data: Optional[PaginationData] = Field(None, alias='paginationData')


class TaskListForProjectResponse(TheStageBaseResponse):
    model_config = ConfigDict(use_enum_values=True)

    tasks: TaskListForProjectPaging = Field(None, alias='tasks')
