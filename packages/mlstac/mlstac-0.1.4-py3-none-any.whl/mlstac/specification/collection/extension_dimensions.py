from typing import List, Optional

import pydantic


class TensorDimension(pydantic.BaseModel):
    """In the ML-STAC specification, the dimensions are from the
    same modalities. This extension defines the dimensions of the samples
    for each Sample.

    fields:
        axis (int): The axis of the dimension.
        description (Optional[str]): A description of the dimension.
    """

    axis: int
    name: str
    description: Optional[str] = None


class TensorDimensions(pydantic.BaseModel):
    """In the ML-STAC specification, the dimensions are equal between
    all the samples. This extension defines the dimensions of the samples
    for each SampleTensor.

    fields:
        dimensions (Dict[str, Dimension]): A dictionary with the dimensions
            of the samples. The key is the name of the dimension and the
            value is a Dimension object.
        dtype (Optional[str]): The data type of the samples. This field
            is defined automatically by the 'automatic_field' method from the
            Collection class.
        shape (Optional[List[int]]): The shape of the samples. This field
            is defined automatically by the 'automatic_field' method from the
            Collection class.
        offsets (Optional[List[int]]): The offsets of the samples. This field
            is defined automatically by the 'automatic_field' method from the
            Collection class.
    """

    dimensions: Optional[List[TensorDimension]] = None
