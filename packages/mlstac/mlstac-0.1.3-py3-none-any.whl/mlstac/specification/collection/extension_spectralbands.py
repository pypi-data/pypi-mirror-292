from typing import List, Optional

import pydantic


class SpectralBand(pydantic.BaseModel):
    """This extension provides a way to define the spectral bands of a
    dataset. Useful for Remote Sensing datasets.

    fields:
        band (str): The name of the band.
        index (Optional[int]): The index of the band.
        description (Optional[str]): A description of the band.
        unit (Optional[str]): The unit of the band.
        wavelengths (Optional[List[float]]): The wavelengths of the band.
            It must be a list of two floats. The first float is the minimum
            wavelength and the second float is the maximum wavelength.
    """

    name: str
    index: Optional[int]
    common_name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    center_wavelength: Optional[float] = None
    full_width_half_max: Optional[float] = None


class SpectralBands(pydantic.BaseModel):
    """This extension provides a way to define the
    spectral bands of a dataset. Useful for Remote
    Sensing datasets.

    fields:
        bands (Dict[str, SpectralBand]): A dictionary with
            the spectral bands of the dataset. The key is the
            name of the band and the value is a SpectralBand
            object.
        axis (Optional[int]): The axis of the spectral bands.
        sensor (Optional[str]): The sensor of the spectral bands.
    """

    bands: List[SpectralBand]
    axis: Optional[int] = None
    sensor: Optional[str] = None
