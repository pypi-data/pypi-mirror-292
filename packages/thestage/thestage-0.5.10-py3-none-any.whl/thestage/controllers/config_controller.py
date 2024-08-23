from thestage_core.entities.config_entity import ConfigEntity

from thestage.i18n.translation import __
from thestage.helpers.logger.app_logger import app_logger
from thestage.services.config_provider.config_provider import ConfigProvider
from thestage.services.service_facade import ServiceFactory
from thestage.controllers.utils_controller import get_current_directory, validate_config_and_get_service_factory

import typer

app = typer.Typer(no_args_is_help=True, help=__("Help working with config"))


@app.command(name='get', no_args_is_help=False, help=__("Print all config items"))
def config_get():
    """
        Print all use configs
    """
    app_logger.info(f'Start config from {get_current_directory()}')

    service_factory = validate_config_and_get_service_factory(no_dialog=True)
    config = service_factory.get_config_provider().get_full_config()

    if not config:
        typer.echo(__('You dont have config yet'))
        raise typer.Exit(1)

    typer.echo(__('THESTAGE TOKEN: %token%', {'token': config.main.auth_token or ''}))
    typer.echo(__('THESTAGE CONFIG FILE: %dir%', {'dir': config.main.config_file_name or ''}))
    typer.echo(__('THESTAGE API LINK: %link%', {'link': config.main.config_api_link or ''}))
    if config.main.config_local_path:
        typer.echo(__('THESTAGE LOCAL CONFIG PATH: %path%', {'path': str(config.main.config_local_path or '')}))
    if config.main.config_global_path:
        typer.echo(__('THESTAGE GLOBAL CONFIG PATH: %path%', {'path': str(config.main.config_global_path or '')}))

    raise typer.Exit(0)


@app.command(name='set', no_args_is_help=True, help=__("Set some config item"))
def config_set(
    token: str = typer.Option(
            None,
            "--api-token",
            "-t",
            help=__("If you want initialize or change token"),
            is_eager=False,
            is_flag=True,
        ),
):
    """
        Set up some params
    """
    app_logger.info(f'Start config from {get_current_directory()}')

    config_provider = ConfigProvider(local_path=get_current_directory())
    service_factory = ServiceFactory(config_provider)

    app_service = service_factory.get_app_config_service()

    if token:
        app_service.app_change_token(config=config_provider.get_full_config(), token=token)

    typer.echo('Config changed')
    raise typer.Exit(0)


@app.command(name='clear', no_args_is_help=False, help=__("Clear thestage config"))
def config_clear():
    """
        Clear config
    """
    app_logger.info(f'Start config from {get_current_directory()}')
    service_factory = validate_config_and_get_service_factory(no_dialog=False)
    service_factory.get_config_provider().remove_all_config()

    raise typer.Exit(0)
