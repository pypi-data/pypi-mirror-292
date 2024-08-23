from typing import Optional, List

from pydantic import BaseModel, Field
from thestage_core.entities.file_item import FileItemEntity


class SftpFileItemEntity(FileItemEntity):

    instance_path: Optional[str] = Field(None)
    container_path: Optional[str] = Field(None)
    tmp_path: Optional[str] = Field(None)
    children: List['SftpFileItemEntity'] = Field(default=[])
    dest_path: Optional[str] = Field(None)



class SftpPathHelper(BaseModel):

    tmp_container_path: str = Field(None)
    tmp_instance_path: str = Field(None)

    tmp_folder_path: str = Field(None)

    item_name: str = Field(None)

    item_path: str = Field(None)
    item_dop_path: str = Field(None)


    def tmp_container_path_with_name(self) -> str:
        return f"{self.tmp_container_path}/{self.item_name}"

    def tmp_instance_path_with_name(self) -> str:
        return f"{self.tmp_instance_path}/{self.item_name}"
