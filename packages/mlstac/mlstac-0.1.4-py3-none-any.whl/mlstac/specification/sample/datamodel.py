import datetime
import re
import warnings
from typing import Any, List, Tuple, Union

import numpy as np
import pydantic

SixFloats = Tuple[float, float, float, float, float, float]
CubeTime = Union[str, datetime.datetime, List[str], List[datetime.datetime]]


class Sample(pydantic.BaseModel):
    tensor: Any
    geotransform: SixFloats
    start_datetime: CubeTime
    crs: str
    end_datetime: Union[CubeTime, None] = None

    @pydantic.field_validator("tensor")
    def check_tensor(cls, v: np.ndarray) -> np.ndarray:
        if not isinstance(v, np.ndarray):
            raise ValueError("tensor must be a numpy array")
        return v

    @pydantic.field_validator("crs")
    def check_crs(cls, v: str) -> str:
        regex_exp = re.compile(r"^(?:EPSG|ESRI|SR-ORG):[0-9]+$")
        if not regex_exp.match(v):
            warnings.warn(
                "It is recommended crs to be from the format: <authority>:<code>"
            )
        return v

    @pydantic.model_validator(mode="after")
    def check_start_end_datetime(self) -> "Sample":
        # If the start_datetime is a list, the end_datetime must be a list
        # both lists must have the same length
        if isinstance(self.start_datetime, list):
            if self.end_datetime is not None:
                if not isinstance(self.end_datetime, list):
                    raise ValueError("end_datetime must be a list")
                if len(self.start_datetime) != len(self.end_datetime):
                    raise ValueError(
                        "start_datetime and end_datetime must have the same length"
                    )
            # the end_datetime must be always higher than the start_datetime
            for i in range(len(self.start_datetime)):
                if self.start_datetime[i] < self.end_datetime[i]:
                    raise ValueError("end_datetime must be after start_datetime")

        # If the start_datetime is a string, the end_datetime must be a string
        if isinstance(self.start_datetime, str):
            if self.end_datetime is not None:
                if not isinstance(self.end_datetime, str):
                    raise ValueError("end_datetime must be a string")

            # the end_datetime must be always higher than the start_datetime
            if self.start_datetime > self.end_datetime:
                raise ValueError("end_datetime must be after start_datetime")

        return self


## Create model squema
# demo = Sample(
#    tensor=np.random.rand(10, 10, 10),
#    geotransform=(0, 1, 0, 0, 0, 1),
#    start_datetime="2021-01-01",
#    end_datetime="2021-01-02",
#    crs="EPSG:4326",
# )
#
# import json
# with open("mlstac/specification/sample/squema.json", "w") as f:
#    json.dump(demo.model_json_schema(), f, indent=2)
