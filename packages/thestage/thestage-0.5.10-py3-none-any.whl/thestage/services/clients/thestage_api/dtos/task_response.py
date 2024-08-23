from typing import Optional, List

from pydantic import Field, BaseModel, ConfigDict

from thestage.services.clients.thestage_api.dtos.frontend_status import FrontendStatusDto
from thestage.services.clients.thestage_api.dtos.selfhosted_instance_response import SelfHostedInstanceDto
from thestage.services.clients.thestage_api.dtos.enums.task_execution_status import TaskExecutionStatusEnumDto
from thestage.services.clients.thestage_api.dtos.instance_rented_response import InstanceRentedDto
from thestage.services.clients.thestage_api.dtos.pagination_data import PaginationData
from thestage.services.clients.thestage_api.dtos.storage_rented_response import StorageRentedDto
from thestage.services.clients.thestage_api.dtos.base_response import TheStageBaseResponse


class TaskDto(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: Optional[int] = Field(None, alias='id')
    instance_rented_id: Optional[int] = Field(None, alias='instanceRentedId')
    selfhosted_instance_id: Optional[int] = Field(None, alias='selfhostedInstanceId')
    docker_container_id: Optional[int] = Field(None, alias='dockerContainerId')
    description: Optional[str] = Field(None, alias='description')
    title: Optional[str] = Field(None, alias='title')
    source_path: Optional[str] = Field(None, alias='sourcePath')
    source_target_path: Optional[str] = Field(None, alias='sourceTargetPath')
    data_path: Optional[str] = Field(None, alias='dataPath')
    result_destination_path: Optional[str] = Field(None, alias='resultDestinationPath')
    run_command: Optional[str] = Field(None, alias='runCommand')
    commit_hash: Optional[str] = Field(None, alias='commitHash')
    ordinal_number_for_sketch: Optional[int] = Field(None, alias='ordinalNumberForSketch')
    user_id: Optional[int] = Field(None, alias='userId')
    frontend_status: FrontendStatusDto = Field(None, alias='frontendStatus')
    created_at: Optional[str] = Field(None, alias='createdAt')
    updated_at: Optional[str] = Field(None, alias='updatedAt')
    started_at: Optional[str] = Field(None, alias='startedAt')
    finished_at: Optional[str] = Field(None, alias='finishedAt')
    client_id: Optional[int] = Field(None, alias='clientId')

    instance_rented: Optional[InstanceRentedDto] = Field(None, alias='instanceRented')
    selfhosted_instance: Optional[SelfHostedInstanceDto] = Field(None, alias='selfhostedInstance')
    storage_rented: Optional[StorageRentedDto] = Field(None, alias='storageRented')

    exit_code: Optional[int] = Field(None, alias='exitCode')
    failure_reason: Optional[str] = Field(None, alias='failureReason')


class TaskViewResponse(TheStageBaseResponse):
    task: Optional[TaskDto] = Field(None, alias='task')
    task_view_url: Optional[str] = Field(None, alias='websiteTaskViewUrl')
    task_output_url: Optional[str] = Field(None, alias='websiteTaskOutputUrl')


class TaskGetOutputResponse(TheStageBaseResponse):
    message: Optional[str] = Field(None, alias='message')
    stdout: Optional[str] = Field(None, alias='stdout')
    stderr: Optional[str] = Field(None, alias='stderr')
