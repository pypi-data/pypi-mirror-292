from typing import Optional, Annotated

from tabulate import tabulate
from thestage_core.entities.config_entity import ConfigEntity

from thestage.entities.project_task import ProjectTaskEntity
from thestage.helpers.error_handler import error_handler
from thestage.i18n.translation import __
from thestage.services.clients.thestage_api.dtos.task_response import TaskDto
from thestage.helpers.logger.app_logger import app_logger
from thestage.controllers.utils_controller import validate_config_and_get_service_factory, get_current_directory

import typer

from thestage.services.project.dto.project_config import ProjectConfig
from thestage.services.project.project_service import ProjectService

app = typer.Typer(no_args_is_help=True, help=__("Help working with projects"))

@app.command(name='clone')
def clone(
        project_slug: str = typer.Option(
            None,
            '--project-uid',
            '-uid',
            help=__("Slug for project (Required)"),
            is_eager=False,
        ),
        working_directory: Optional[str] = typer.Option(
            None,
            "--working-directory",
            "-wd",
            help=__("Full path for working directory"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        Clone project on current working directory
    """
    path = get_current_directory()
    app_logger.info(f'Start project clone from {get_current_directory()}')

    service_factory = validate_config_and_get_service_factory(no_dialog=no_dialog, working_directory=working_directory)
    config = service_factory.get_config_provider().get_full_config()

    project_service = service_factory.get_project_service()
    # file_system_service = service_factory.get_file_system_service()

    project_service.clone_project(
        config=config,
        project_slug=project_slug,
        no_dialog=no_dialog,
    )

    typer.echo(__("Clone done"))
    raise typer.Exit(0)


@app.command(name='init')
def init(
        project_slug: Optional[str] = typer.Option(
            None,
            '--project-uid',
            '-uid',
            help=__("Project Unique ID"),
            is_eager=False,
        ),
        working_directory: Optional[str] = typer.Option(
            None,
            "--working-directory",
            "-wd",
            help=__("Full path for working directory"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        Initialize project on current working directory
    """
    app_logger.info(f'Start project init from {get_current_directory()}')

    service_factory = validate_config_and_get_service_factory(no_dialog=no_dialog, working_directory=working_directory)
    config = service_factory.get_config_provider().get_full_config()

    project_service = service_factory.get_project_service()
    project_config = service_factory.get_config_provider().read_project_config()

    if project_config:
        typer.echo(__("Folder initialized, it contains a working project"))
        raise typer.Exit(1)

    project_service.init_project(
        project_slug=project_slug,
        config=config,
        no_dialog=no_dialog,
    )

    typer.echo(__("Init done"))
    raise typer.Exit(0)


@app.command(name='run')
def run(
        command: str = typer.Option(
            None,
            '--command',
            '-com',
            help=__("Command for run (Required)"),
            is_eager=True,
        ),
        commit_hash: Optional[str] = typer.Option(
            None,
            '--commit-hash',
            '-hash',
            help=__("Commit hash"),
            is_eager=False,
        ),
        task_title: Optional[str] = typer.Option(
            None,
            '--task-title',
            '-t',
            help=__("Title for task"),
            is_eager=False,
        ),
        task_description: Optional[str] = typer.Option(
            None,
            '--task-description',
            '-d',
            help=__("Description for task"),
            is_eager=False,
        ),
        docker_container_slug: Optional[str] = typer.Option(
            None,
            '--docker-container-uid',
            '-dcuid',
            help=__("Docker Container Unique ID"),
            is_eager=False,
        ),
        working_directory: Optional[str] = typer.Option(
            None,
            "--working-directory",
            "-wd",
            help=__("Full path for working directory"),
            show_default=False,
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
        auto_commit: Optional[bool] = typer.Option(
            False,
            "--auto-commit",
            "-ac",
            help=__("Use with no_dialog config, default disable auto commit"),
            is_eager=False,
        ),
):
    """
        Execute a task from a project
    """
    app_logger.info(f'Start project run from {get_current_directory()}')

    if not command:
        typer.echo(__('Command is required'))
        raise typer.Exit(1)

    if not docker_container_slug:
        typer.echo(__('Docker container Unique ID is required'))
        raise typer.Exit(1)

    service_factory = validate_config_and_get_service_factory(no_dialog=no_dialog, working_directory=working_directory)
    config = service_factory.get_config_provider().get_full_config()

    project_service = service_factory.get_project_service()
    project_config: ProjectConfig = service_factory.get_config_provider().read_project_config()

    if not project_config:
        typer.echo(__("This folder is not initialize, please doing init or clone"))
        raise typer.Exit(1)

    task: Optional[TaskDto] = project_service.project_run_task(
        config=config,
        project_config=project_config,
        run_command=command,
        commit_hash=commit_hash,
        task_title=task_title,
        task_description=task_description,
        docker_container_slug=docker_container_slug,
        no_dialog=no_dialog,
        auto_commit=auto_commit,
    )
    if task:
        typer.echo(__(
            "Task id: %task_id% - %task_status%",
            {
                'task_id': str(task.id),
                'task_status': task.frontend_status.status_translation
            }
        ))

    typer.echo(__("Task successfully started"))
    raise typer.Exit(0)


@app.command("task-ls")
def list_runs(
        working_directory: Optional[str] = typer.Option(
            None,
            "--working-directory",
            "-wd",
            help=__("Full path for working directory"),
            is_eager=False,
        ),
        row: int = typer.Option(
            5,
            '--row',
            '-r',
            help=__("Count row in table"),
            is_eager=False,
        ),
        page: int = typer.Option(
            1,
            '--page',
            '-p',
            help=__("Page number"),
            is_eager=False,
        ),
        no_dialog: Optional[bool] = typer.Option(
            None,
            "--no-dialog",
            "-nd",
            help=__("Start process with default values, without future dialog"),
            is_eager=False,
        ),
):
    """
        List tasks started from project
    """
    app_logger.info(f'Start project list-runs from {get_current_directory()}')

    service_factory = validate_config_and_get_service_factory(no_dialog=no_dialog, working_directory=working_directory)
    config = service_factory.get_config_provider().get_full_config()

    project_service: ProjectService = service_factory.get_project_service()

    project_config: ProjectConfig = service_factory.get_config_provider().read_project_config()
    if not project_config:
        typer.echo(__("This folder is not initialize, please doing init or clone"))
        raise typer.Exit(1)

    print_project_task_list(
        config=config,
        project_slug=project_config.slug,
        project_service=project_service,
        row=row,
        page=page,
        no_dialog=no_dialog,
    )
    typer.echo(__("List runs done"))
    raise typer.Exit(0)


def print_project_task_list(
        config: ConfigEntity,
        project_slug: str,
        project_service: ProjectService,
        row: int = 5,
        page: int = 1,
        no_dialog: bool = False,
):
    data, pagination_data = project_service.get_project_task_list(
        project_slug=project_slug,
        config=config,
        row=row,
        page=page,
    )

    raw_data = [list(item.model_dump(by_alias=True).values()) for item in data]

    typer.echo(f"Page: {page}, Limit: {row}, Total Pages: {pagination_data.total_pages} ")
    raw_data.insert(0, ['#'] + list(map(lambda x: x.alias, ProjectTaskEntity.model_fields.values())))
    typer.echo(tabulate(raw_data, showindex="always", tablefmt="double_outline", headers="firstrow"))

    if len(raw_data) == 1:
        typer.echo("List empty, work done")
        raise typer.Exit(0)

    if no_dialog:
        raise typer.Exit(0)

    if page == pagination_data.total_pages:
        typer.echo(__("No more items to show"))
        raise typer.Exit(0)

    next_page: int = typer.prompt(
        text=f'Go to next page (0 to exit)?',
        default=page + 1,
        show_choices=False,
        type=int,
        show_default=True,
    )
    if next_page == 0:
        raise typer.Exit(0)
    else:
        print_project_task_list(
            config=config,
            project_slug=project_slug,
            project_service=project_service,
            row=row,
            page=next_page,
        )
