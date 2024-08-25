import re
from typing import List, Literal, Optional

import pydantic


class SingleCatalog(pydantic.BaseModel):
    name: Literal["train", "test", "validation"]
    data_files: List[pydantic.AnyUrl]
    data_descriptions: List[str]
    data_checksum: List[int]
    metadata_file: pydantic.AnyUrl
    metadata_description: str
    metadata_checksum: int

    @pydantic.field_validator("name")
    def name_must_be_valid(cls, value: str) -> str:
        if not re.match(r"train|test|val|validation", value):
            raise ValueError("name must be one of train, test, or validation.")
        return value


class Catalog(pydantic.BaseModel):
    train: SingleCatalog
    validation: Optional[SingleCatalog] = None
    test: Optional[SingleCatalog] = None
