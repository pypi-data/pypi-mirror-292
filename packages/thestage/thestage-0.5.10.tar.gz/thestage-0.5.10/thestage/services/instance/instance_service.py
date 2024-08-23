from typing import Tuple, List, Optional, Any, Dict

import typer
from thestage_core.entities.config_entity import ConfigEntity

from thestage.helpers.logger.app_logger import app_logger
from thestage.i18n.translation import __
from thestage.services.clients.thestage_api.dtos.enums.selfhosted_status import SelfHostedBusinessStatusEnumDto, \
    SelfHostedFrontendStatusEnumDto
from thestage.services.clients.thestage_api.dtos.enums.rented_status import RentedBusinessStatusEnumDto, \
    RentedFrontendStatusEnumDto
from thestage.services.abstract_service import AbstractService
from thestage.helpers.error_handler import error_handler
from thestage.services.clients.thestage_api.api_client import TheStageApiClient
from thestage.services.clients.thestage_api.dtos.instance_rented_response import InstanceRentedDto, \
    InstanceRentedBusinessStatusMapperResponse
from thestage.services.clients.thestage_api.dtos.selfhosted_instance_response import SelfHostedInstanceDto, \
    SelfHostedRentedRentedBusinessStatusMapperResponse
from thestage.services.config_provider.config_provider import ConfigProvider
from thestage.services.remote_server_service import RemoteServerService


class InstanceService(AbstractService):

    __thestage_api_client: TheStageApiClient = None

    def __init__(
            self,
            thestage_api_client: TheStageApiClient,
            config_provider: ConfigProvider,
            remote_server_service: RemoteServerService,
    ):
        super(InstanceService, self).__init__(
            config_provider=config_provider
        )
        self.__thestage_api_client = thestage_api_client
        self.__remote_server_service = remote_server_service

    def get_rented_item(
            self,
            config: ConfigEntity,
            instance_slug: str,
    ) -> Optional[InstanceRentedDto]:
        return self.__thestage_api_client.get_rented_item(
            token=config.main.auth_token,
            instance_slug=instance_slug,
        )

    def get_self_hosted_item(
            self,
            config: ConfigEntity,
            instance_slug: str,
    ) -> Optional[SelfHostedInstanceDto]:
        return self.__thestage_api_client.get_selfhosted_item(
            token=config.main.auth_token,
            instance_slug=instance_slug,
        )

    @error_handler()
    def check_instance_status_to_connect(
            self,
            instance: InstanceRentedDto,
    ) -> InstanceRentedDto:
        if instance:
            if instance.frontend_status.status_key in [
                RentedBusinessStatusEnumDto.IN_QUEUE.name,
                RentedBusinessStatusEnumDto.CREATING.name,
                RentedBusinessStatusEnumDto.REBOOTING.name,
                RentedBusinessStatusEnumDto.STARTING.name,
            ]:
                typer.echo(__('Instance start renting or rebooting, please connect late'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                RentedBusinessStatusEnumDto.TERMINATING.name,
                RentedBusinessStatusEnumDto.RENTAL_ERROR.name,
            ]:
                typer.echo(__('Instance is failed, please start him'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                RentedBusinessStatusEnumDto.STOPPED.name,
                RentedBusinessStatusEnumDto.STOPPING.name,
                RentedBusinessStatusEnumDto.DELETED.name,
            ]:
                typer.echo(__('Instance is stopped or deleted, please create new'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                RentedBusinessStatusEnumDto.UNKNOWN.name,
                RentedBusinessStatusEnumDto.ALL.name,
            ]:
                typer.echo(__('Instance status unknown'))
                raise typer.Exit(1)

        return instance

    @error_handler()
    def check_selfhosted_status_to_connect(
            self,
            instance: SelfHostedInstanceDto,
    ) -> SelfHostedInstanceDto:
        if instance:
            if instance.frontend_status.status_key in [
                SelfHostedBusinessStatusEnumDto.AWAITING_CONFIGURATION.name,
            ]:
                typer.echo(__('Instance awaiting to configuration'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                SelfHostedBusinessStatusEnumDto.TERMINATED.name,
                SelfHostedBusinessStatusEnumDto.DELETED.name,
            ]:
                typer.echo(__('Instance is failed or deleted, please start him'))
                raise typer.Exit(1)
            elif instance.frontend_status.status_key in [
                SelfHostedBusinessStatusEnumDto.UNKNOWN.name,
                SelfHostedBusinessStatusEnumDto.ALL.name,
            ]:
                typer.echo(__('Instance status unknown'))
                raise typer.Exit(1)

        return instance

    @error_handler()
    def connect_to_instance(
            self,
            ip_address: str,
            username: str,
    ):
        self.__remote_server_service.connect_to_instance(
            ip_address=ip_address,
            username=username,
        )

    @error_handler()
    def get_rented_list(
            self,
            config: ConfigEntity,
            statuses: List[str],
            row: int = 5,
            page: int = 1,
    ) -> Tuple[List[Any], int]:
        data, total_pages = self.__thestage_api_client.get_rented_instance_list(
            token=config.main.auth_token,
            statuses=statuses,
            page=page,
            limit=row,
        )

        return data, total_pages

    @error_handler()
    def get_self_hosted_list(
            self,
            config: ConfigEntity,
            statuses: List[str],
            row: int = 5,
            page: int = 1,
    ) -> Tuple[List[Any], int]:
        data, total_pages = self.__thestage_api_client.get_selfhosted_instance_list(
            token=config.main.auth_token,
            statuses=statuses,
            page=page,
            limit=row,
        )
        return data, total_pages

    def map_rented_statuses(self, config: ConfigEntity, frontend: List[RentedFrontendStatusEnumDto]) -> Optional[List[str]]:
        statuses_mapper: Optional[Dict[str, str]] = self.__thestage_api_client.get_rented_business_status_map(token=config.main.auth_token,)
        return self.map_frontend_statuses(statuses_mapper=statuses_mapper, frontend=[item.value for item in frontend])

    def map_rented_statuses_old(self, config: ConfigEntity, frontend: List[RentedFrontendStatusEnumDto]) -> Optional[List[str]]:



        real_statuses = []

        statuses_mapper: Optional[InstanceRentedBusinessStatusMapperResponse] = self.__thestage_api_client.get_rented_business_status_map(token=config.main.auth_token,)

        if not statuses_mapper:
            return None

        mapper: Dict[str, List] = {}
        for key, value in statuses_mapper.instance_rented_business_status_map.items():

            map_key = value if ' ' not in value else value.replace(' ', '_')
            if value not in mapper:
                mapper[map_key] = [key]
            else:
                mapper[map_key].append(key)

        for item in frontend:
            if item == RentedFrontendStatusEnumDto.all:
                return []
            elif item == RentedFrontendStatusEnumDto.unknown:
                continue
            else:
                if item.name in mapper:
                    real_statuses.extend(mapper[item.name])
                else:
                    app_logger.error(f'Not found status on mapper rented statuses')

        return real_statuses

    def map_selfhosted_statuses(self, config: ConfigEntity, frontend: List[SelfHostedFrontendStatusEnumDto]) -> Optional[List[str]]:
        statuses_mapper: Optional[Dict[str, str]] = self.__thestage_api_client.get_selfhosted_business_status_map(token=config.main.auth_token,)
        return self.map_frontend_statuses(statuses_mapper=statuses_mapper, frontend=[item.value for item in frontend])

    def map_selfhosted_statuses_old(self, config: ConfigEntity, frontend: List[SelfHostedFrontendStatusEnumDto]) -> Optional[List[str]]:

        real_statuses = []

        statuses_mapper: Optional[SelfHostedRentedRentedBusinessStatusMapperResponse] = self.__thestage_api_client.get_selfhosted_business_status_map(token=config.main.auth_token,)

        if not statuses_mapper:
            return None

        mapper: Dict[str, List] = {}
        for key, value in statuses_mapper.selfhosted_instance_business_status_map.items():
            map_key = value if ' ' not in value else value.replace(' ', '_')
            if value not in mapper:
                mapper[map_key] = [key]
            else:
                mapper[map_key].append(key)

        for item in frontend:
            if item == SelfHostedFrontendStatusEnumDto.all:
                return []
            elif item == SelfHostedFrontendStatusEnumDto.unknown:
                continue
            else:
                if item.name in mapper:
                    real_statuses.extend(mapper[item.name])
                else:
                    app_logger.error(f'Not found status on mapper selfhosted statuses')

        return real_statuses
