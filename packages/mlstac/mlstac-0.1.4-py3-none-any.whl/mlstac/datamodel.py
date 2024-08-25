from typing import Any

import pandas as pd
import pydantic

from mlstac.specification.collection.datamodel import Collection


class MLSTAC(pydantic.BaseModel):
    collection: Collection
    metadata: Any

    @pydantic.field_validator("metadata")
    def check_metadata(cls, v):
        if not isinstance(v, pd.DataFrame):
            raise ValueError("The metadata must be a pandas DataFrame")
        return v

    def __str__(self):
        return f"MLSTAC(collection=<dict>, metadata=<pandas.DataFrame>)"

    def __repr__(self):
        return self.__str__()
