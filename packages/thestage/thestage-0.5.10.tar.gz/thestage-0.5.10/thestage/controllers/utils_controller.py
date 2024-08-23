import pathlib
from typing import Optional, Dict, Tuple

from thestage_core.entities.config_entity import ConfigEntity

from thestage.helpers.error_handler import error_handler
from thestage.services.service_facade import ServiceFactory
from thestage.services.config_provider.config_provider import ConfigProvider


def get_current_directory() -> pathlib.Path:
    return pathlib.Path.cwd()


@error_handler()
def validate_config_and_get_service_factory(
        working_directory: Optional[str | pathlib.Path] = None,
        no_dialog: bool = False,
) -> ServiceFactory:
    config_provider = ConfigProvider(local_path=get_current_directory() if not working_directory else working_directory)
    service_factory = ServiceFactory(config_provider=config_provider)
    config: ConfigEntity = config_provider.get_full_config()

    validation_service = service_factory.get_validation_service()
    validation_service.check_token(config=config, no_dialog=no_dialog)
    config_provider.save_global_config(config=config)

    return service_factory
