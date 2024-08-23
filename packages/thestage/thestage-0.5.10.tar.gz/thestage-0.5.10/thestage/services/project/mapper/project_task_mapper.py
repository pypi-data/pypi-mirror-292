from typing import Optional

from thestage.entities.project_task import ProjectTaskEntity
from thestage.services.clients.thestage_api.dtos.task_response import TaskDto


class ProjectTaskMapper:

    @staticmethod
    def build_task_entity(item: TaskDto) -> Optional[ProjectTaskEntity]:
        if not item:
            return None

        return ProjectTaskEntity(
            id=item.id,
            title=item.title,
            status=item.frontend_status.status_translation,
            docker_container_id=item.docker_container_id,
            started_at=item.started_at,
            finished_at=item.finished_at,
        )
