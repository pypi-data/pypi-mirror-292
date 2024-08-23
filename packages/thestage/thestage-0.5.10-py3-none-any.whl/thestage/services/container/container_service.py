import os
import uuid
from typing import List, Tuple, Optional, Dict

import typer
from thestage_core.entities.config_entity import ConfigEntity
from thestage_core.entities.file_item import FileItemEntity
from thestage_core.services.filesystem_service import FileSystemServiceCore

from thestage.helpers.logger.app_logger import app_logger
from thestage.services.clients.thestage_api.dtos.container_param_request import DockerContainerActionRequestDto
from thestage.services.clients.thestage_api.dtos.enums.container_pending_action import ContainerPendingActionEnumDto
from thestage.services.clients.thestage_api.dtos.enums.container_status import ContainerBussinessStatusEnumDto, \
    ContainerFrontendStatusEnumDto
from thestage.entities.enums.shell_type import ShellType
from thestage.services.clients.thestage_api.dtos.sftp_path_helper import SftpPathHelper, SftpFileItemEntity
from thestage.services.remote_server_service import RemoteServerService
from thestage.i18n.translation import __
from thestage.services.abstract_service import AbstractService
from thestage.services.clients.thestage_api.dtos.container_response import DockerContainerDto
from thestage.helpers.error_handler import error_handler
from thestage.services.clients.thestage_api.api_client import TheStageApiClient
from thestage.services.config_provider.config_provider import ConfigProvider


class ContainerService(AbstractService):

    __thestage_api_client: TheStageApiClient = None

    def __init__(
            self,
            thestage_api_client: TheStageApiClient,
            config_provider: ConfigProvider,
            remote_server_service: RemoteServerService,
            file_system_service: FileSystemServiceCore,
    ):
        super(ContainerService, self).__init__(
            config_provider=config_provider
        )
        self.__thestage_api_client = thestage_api_client
        self.__remote_server_service = remote_server_service
        self.__file_system_service = file_system_service

    @error_handler()
    def get_list(
            self,
            config: ConfigEntity,
            statuses: List[str],
            row: int = 5,
            page: int = 1,
    ) -> Tuple[List[DockerContainerDto], int]:

        data, total = self.__thestage_api_client.get_container_list(
            token=config.main.auth_token,
            statuses=statuses,
            page=page,
            limit=row,
        )

        return data, total

    @error_handler()
    def get_item(
            self,
            config: ConfigEntity,
            container_id: Optional[int] = None,
            container_slug: Optional[str] = None,
    ) -> Optional[DockerContainerDto]:
        return self.__thestage_api_client.get_container_item(
            token=config.main.auth_token,
            container_id=container_id,
            container_slug=container_slug,
        )

    @staticmethod
    def get_server_auth(
            container: DockerContainerDto,
            no_dialog: bool = False,
            username_param: Optional[str] = None,
    ) -> Tuple[str, str]:
        if container.instance_rented:
            username = container.instance_rented.host_username
            ip_address = container.instance_rented.ip_address
        elif container.selfhosted_instance:
            username = container.selfhosted_instance.host_username or 'root'
            ip_address = container.selfhosted_instance.ip_address
        else:
            typer.echo(__("Not found rented or selfhosted instance for connect"))
            raise typer.Exit(1)

        if not username_param:
            if not username:
                if no_dialog:
                    typer.echo(__('Please set up username as parameter on no-dialog mode'))
                    raise typer.Exit(1)

                username = typer.prompt(
                    default='ubuntu',
                    text=__('Please set up username to connect instance'),
                    show_choices=False,
                    type=str,
                    show_default=True,
                )
        else:
            username = username_param

        return username, ip_address

    @error_handler()
    def connect_container(
            self,
            config: ConfigEntity,
            container: DockerContainerDto,
            no_dialog: bool = False,
            username_param: Optional[str] = None,
    ):

        username, ip_address = self.get_server_auth(
            container=container,
            username_param=username_param,
            no_dialog=no_dialog,
        )

        if not container.system_name:
            typer.echo(__("Container name not present, can not connect to container"))
            raise typer.Exit(1)

        shell: Optional[ShellType] = self.__remote_server_service.get_shell_from_container(
            ip_address=ip_address,
            username=username,
            docker_name=container.system_name,
        )

        if not shell:
            typer.echo(__("We can not get shell on container (bash, shell), please use standard shell"))
            raise typer.Exit(1)

        self.__remote_server_service.connect_to_container(
            ip_address=ip_address,
            username=username,
            docker_name=container.system_name,
            shell=shell,
        )

    @error_handler()
    def check_container_status_for_start(
            self,
            container: DockerContainerDto,
    ) -> DockerContainerDto:
        if container:
            if container.frontend_status.status_key == ContainerBussinessStatusEnumDto.RUNNING:
                typer.echo(__('Container is running, can not start working server'))
                raise typer.Exit(1)
            elif container.frontend_status.status_key == ContainerBussinessStatusEnumDto.CREATING:
                typer.echo(__('Container creating, please check status later'))
                raise typer.Exit(1)
            elif container.frontend_status.status_key in [
                ContainerBussinessStatusEnumDto.STARTING,
                ContainerBussinessStatusEnumDto.RESTARTING,
            ]:
                typer.echo(__('The container starts now, you can be up and running in minutes'))
                raise typer.Exit(1)
            elif container.frontend_status.status_key in [
                ContainerBussinessStatusEnumDto.DELETING,
                ContainerBussinessStatusEnumDto.DELETED,
            ]:
                typer.echo(__('The container was deleted, create new'))
                raise typer.Exit(1)

        return container

    @error_handler()
    def check_container_status_for_stop(
            self,
            container: DockerContainerDto,
    ) -> DockerContainerDto:
        if container:
            if container.frontend_status.status_key in [
                ContainerBussinessStatusEnumDto.CREATING,
                ContainerBussinessStatusEnumDto.STARTING,
                ContainerBussinessStatusEnumDto.RESTARTING,
            ]:
                typer.echo(__('Container in rebooting or creating, please stop later'))
                raise typer.Exit(1)
            elif container.frontend_status.status_key in [
                ContainerBussinessStatusEnumDto.FAILED,
                ContainerBussinessStatusEnumDto.DEAD,
                ContainerBussinessStatusEnumDto.CREATING_FAILED,
                ContainerBussinessStatusEnumDto.STOPPING,
                ContainerBussinessStatusEnumDto.STOPPED,
            ]:
                typer.echo(__('Container is already stopped'))
                raise typer.Exit(1)
            elif container.frontend_status.status_key in [
                ContainerBussinessStatusEnumDto.DELETING,
                ContainerBussinessStatusEnumDto.DELETED,
            ]:
                typer.echo(__('The container was deleted, create new'))
                raise typer.Exit(1)

        return container

    @error_handler()
    def check_container_status_for_work(
            self,
            container: DockerContainerDto,
    ) -> DockerContainerDto:
        if container:
            if container.frontend_status.status_key in [
                ContainerBussinessStatusEnumDto.CREATING.value,
                ContainerBussinessStatusEnumDto.STARTING.value,
                ContainerBussinessStatusEnumDto.RESTARTING.value,
            ]:
                typer.echo(__('Container is rebooted, please connect late'))
                raise typer.Exit(1)
            elif container.frontend_status.status_key in [
                ContainerBussinessStatusEnumDto.FAILED.value,
                ContainerBussinessStatusEnumDto.DEAD.value,
                ContainerBussinessStatusEnumDto.CREATING_FAILED.value,
                ContainerBussinessStatusEnumDto.STOPPING.value,
                ContainerBussinessStatusEnumDto.STOPPED.value,
            ]:
                typer.echo(__('Container is failed, please start him'))
                raise typer.Exit(1)
            elif container.frontend_status.status_key in [
                ContainerBussinessStatusEnumDto.DELETING.value,
                ContainerBussinessStatusEnumDto.DELETED.value,
            ]:
                typer.echo(__('Container was deleted, create new'))
                raise typer.Exit(1)

        return container

    @staticmethod
    def _get_new_path_from_mapping(
            directory_mapping: Dict[str, str],
            destination_path: str,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:

        instance_path: Optional[str] = None
        container_path: Optional[str] = None
        public_container: Optional[str] = None
        public_instance: Optional[str] = None

        for key, value in directory_mapping.items():

            if value == '/public':
                public_container = value
                public_instance = key

            if destination_path.startswith(f"{value}/") or destination_path == value:
                instance_path = destination_path.replace(value, key)
                container_path = destination_path
                # dont break, check all mapping list

        if instance_path and container_path:
            return instance_path, container_path, None
        else:
            if public_container and public_instance:
                tmp_folder = f"{uuid.uuid4()}"
                return f"{public_instance}/{tmp_folder}", f"{public_container}/{tmp_folder}", f"{public_container}/{tmp_folder}"
            else:
                return None, None, None

    def __build_local_path_by_mapping(
            self,
            files: List[FileItemEntity],
            instance_path: str,
            container_path: str,
            destination_path: str,
            with_tmp: bool = False,
            has_parent: bool = False,
    ):
        result = []
        for item in files:
            elem = SftpFileItemEntity.model_validate(item.model_dump())
            if item.is_file:
                has_file_name = self.__remote_server_service._check_if_file_name_in_path(
                    path=instance_path,
                    file_template=item.name,
                )

                if not has_parent and not with_tmp and has_file_name:
                    elem.instance_path = instance_path
                    elem.container_path = container_path
                else:
                    elem.instance_path = f"{instance_path}/{item.name}"
                    elem.container_path = f"{container_path}/{item.name}"

                if with_tmp:
                    has_file_name = self.__remote_server_service._check_if_file_name_in_path(
                        path=destination_path,
                        file_template=item.name,
                    )
                    if has_file_name:
                        elem.dest_path = destination_path
                    else:
                        elem.dest_path = f"{destination_path}/{item.name}"
                else:
                    elem.dest_path = elem.instance_path

            else:
                if not has_parent and not with_tmp:
                    elem.instance_path = instance_path
                    elem.container_path = container_path
                else:
                    elem.instance_path = f"{instance_path}/{item.name}"
                    elem.container_path = f"{container_path}/{item.name}"

                if with_tmp:
                    elem.dest_path = destination_path
                else:
                    elem.dest_path = elem.instance_path

            if len(item.children) > 0:
                elem.children = []
                elem.children.extend(self.__build_local_path_by_mapping(
                    files=item.children,
                    instance_path=elem.instance_path,
                    container_path=elem.container_path,
                    destination_path=elem.dest_path,
                    with_tmp=with_tmp,
                    has_parent=True,
                ))

            result.append(elem)

        return result

    @error_handler()
    def put_file_to_container(
            self,
            container: DockerContainerDto,
            src_path: str,
            destination_path: Optional[str] = None,
            is_folder: bool = False,
            no_dialog: bool = False,
            username_param: Optional[str] = None,
    ):

        username, ip_address = self.get_server_auth(
            container=container,
            username_param=username_param,
            no_dialog=no_dialog,
        )

        if not self.__file_system_service.check_if_path_exist(file=src_path):
            typer.echo(__("Not found path with file"))
            raise typer.Exit(1)

        if (not is_folder) and self.__file_system_service.is_folder(folder=src_path, auto_create=False, with_exception=False):
            typer.echo(__("Path is folder, please set up recursive flag"))
            raise typer.Exit(1)

        if not container.mappings or not container.mappings.directory_mappings:
            typer.echo(__("Error, can not find mapping folders"))
            raise typer.Exit(1)

        instance_path, container_path, tmp_path = self._get_new_path_from_mapping(
            directory_mapping=container.mappings.directory_mappings,
            destination_path=destination_path,
        )

        if not instance_path and not container_path:
            typer.echo(__("Error, can not find mapping path to copy"))
            typer.Exit(1)

        self.__remote_server_service.upload_data_to_container_new(
            ip_address=ip_address,
            username=username,
            docker_name=container.system_name,
            src_path=src_path,
            dest_path=destination_path,
            instance_path=instance_path,
            container_path=container_path,
            is_folder=is_folder,
            tmp_path=tmp_path,
        )

    @error_handler()
    def get_file_from_container(
            self,
            container: DockerContainerDto,
            src_path: str,
            destination_path: Optional[str] = None,
            is_folder: bool = False,
            no_dialog: bool = False,
            username_param: Optional[str] = None,
    ):
        username, ip_address = self.get_server_auth(
            container=container,
            username_param=username_param,
            no_dialog=no_dialog,
        )

        if not container.mappings or not container.mappings.directory_mappings:
            typer.echo(__("Error, can not find mapping folders"))
            raise typer.Exit(1)

        instance_path, container_path, tmp_path = self._get_new_path_from_mapping(
            directory_mapping=container.mappings.directory_mappings,
            destination_path=src_path,
        )

        if not instance_path and not container_path:
            typer.echo(__("Error, can not find mapping path to copy"))
            typer.Exit(1)

        self.__remote_server_service.download_data_from_container_new(
            ip_address=ip_address,
            username=username,
            docker_name=container.system_name,
            src_path=src_path,
            dest_path=destination_path,
            instance_path=instance_path,
            container_path=container_path,
            tmp_path=tmp_path,
            is_folder=is_folder,
        )

    @error_handler()
    def change_container_status(
            self,
            config: ConfigEntity,
            container: DockerContainerDto,
            action: ContainerPendingActionEnumDto,
    ) -> bool:
        request_params = DockerContainerActionRequestDto(
            dockerContainerId=container.id,
            action=action,
        )
        result = self.__thestage_api_client.container_action(
            token=config.main.auth_token,
            request_param=request_params,
        )
        if not result:
            app_logger.error(f'Container dont change status - {result}')

        return result

    def map_container_statuses(self, config: ConfigEntity, frontend: List[ContainerFrontendStatusEnumDto]) -> Optional[List[str]]:
        statuses_mapper: Optional[Dict[str, str]] = self.__thestage_api_client.get_container_business_status_map(token=config.main.auth_token,)
        return self.map_frontend_statuses(statuses_mapper=statuses_mapper, frontend=[item.value for item in frontend])
