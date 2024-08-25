import json
import pathlib
from typing import List, Literal, Optional, Union

import pydantic

import mlstac.specification.catalog.datamodel as mlstac_catalog
import mlstac.specification.collection.extension_authors as mlstac_authors
import mlstac.specification.collection.extension_auto_documentation as auto_documentation
import mlstac.specification.collection.extension_curators as mlstac_curators
import mlstac.specification.collection.extension_dimensions as mlstac_dimensions
import mlstac.specification.collection.extension_reviewers as mlstac_reviewers
import mlstac.specification.collection.extension_sensors as mlstac_sensors
import mlstac.specification.collection.extension_spectralbands as mlstac_spectralbands
import mlstac.specification.collection.extension_target as mlstac_target
import mlstac.specification.collection.stac as stac


class Collection(stac.STACCollection):

    # Required ML-STAC fields -------------------------------
    mlstac_version: str = "0.1.0"
    ml_task: List[str]
    ml_catalog: mlstac_catalog.Catalog
    ml_dataset_version: str


    # Optional ML-STAC fields -------------------------------
    ml_target: Optional[mlstac_target.Target] = None
    ml_authors: Optional[mlstac_authors.Authors] = None
    ml_curators: Optional[mlstac_curators.Curators] = None
    ml_reviewers: Optional[mlstac_reviewers.Reviewers] = None
    ml_dimensions: Optional[mlstac_dimensions.TensorDimensions] = None
    ml_spectral: Optional[mlstac_spectralbands.SpectralBands] = None
    ml_split_strategy: Optional[
        Literal["random", "stratified", "systematic", "other"]
    ] = None
    ml_raw_data_url: Optional[str] = None
    ml_discussion_url: Optional[str] = None
    ml_paper: Optional[str] = None

    def add_extension(self, extension: str) -> None:
        """Add an STAC extension to the ML-STAC collection."""

        # add extension
        if self.stac_extensions is None:
            self.stac_extensions = [extension]
        else:
            self.stac_extensions.append(extension)

        # remove duplicates
        self.stac_extensions = list(set(self.stac_extensions))

        return None

    def add_author(self, **kwargs: dict) -> None:
        """This method adds the authors of the dataset."""

        # Get the previous authors
        if self.ml_authors is not None:
            dataset_authors = self.ml_authors.authors
        else:
            dataset_authors = []

        # Check if the author is already defined
        if any([d.name == kwargs["name"] for d in dataset_authors]):
            for d in dataset_authors:
                if d.name == kwargs["name"]:
                    dataset_authors.remove(d)

        # Load and append the new author
        new_contact = mlstac_curators.Contact(**kwargs)
        dataset_authors.append(new_contact)

        # Save the new authors
        self.ml_authors = mlstac_authors.Authors(authors=dataset_authors)

        # add contact stac extension
        self.add_extension(
            "https://stac-extensions.github.io/contacts/v0.1.1/schema.json"
        )

        print("Author added to self.ml_authors")

        return None

    def add_curator(self, **kwargs: dict) -> None:
        """This method adds the curators of the dataset.
        Useful for reporting errors or requesting changes.
        """

        # Get the previous curators
        if self.ml_curators is not None:
            dataset_curators = self.ml_curators.curators
        else:
            dataset_curators = []

        # Check if the curator is already defined
        if any([d.name == kwargs["name"] for d in dataset_curators]):
            for d in dataset_curators:
                if d.name == kwargs["name"]:
                    dataset_curators.remove(d)

        # Load and append the new curator
        new_contact = mlstac_curators.Contact(**kwargs)
        dataset_curators.append(new_contact)

        # Save the new curators
        self.ml_curators = mlstac_curators.Curators(curators=dataset_curators)

        # add contact stac extension if not already added
        self.add_extension(
            "https://stac-extensions.github.io/contacts/v0.1.1/schema.json"
        )

        print("Curator added to self.ml_curators")
        return None

    def add_labels(self, **kwargs: dict) -> None:
        """This method adds the labels of the dataset.
        Useful for TensorClassification, ObjectDetection and
        SemanticSegmentation tasks.
        """
        self.ml_target = mlstac_target.Target(**kwargs)
        print("Labels added to self.ml_target")
        return None

    def add_dimension(self, **kwargs: dict) -> None:

        # Get the previous dimensions
        if self.ml_dimensions is not None:
            tensor_dimensions = self.ml_dimensions
        else:
            tensor_dimensions = mlstac_dimensions.TensorDimensions(dimensions=[])

        init_dimensions = getattr(tensor_dimensions, "dimensions")

        # Check if the axis is already defined
        try:
            if any([d.axis == kwargs["axis"] for d in init_dimensions.dimensions]):
                for d in init_dimensions.dimensions:
                    if d.axis == kwargs["axis"]:
                        init_dimensions.dimensions.remove(d)
        except:
            pass

        # Load and append the new curator
        dimension = mlstac_dimensions.TensorDimension(**kwargs)
        init_dimensions.append(dimension)

        # Save the new dimensions
        setattr(tensor_dimensions, "dimensions", init_dimensions)

        self.ml_dimensions = tensor_dimensions
        print("Dimensions added to self.ml_dimensions")

        return None

    def add_spectral_band(self, **kwargs: dict) -> None:
        """Add a spectral band to the dataset."""

        # Get the previous spectral bands
        if self.ml_spectral is not None:
            init_bands = self.ml_spectral.bands
        else:
            init_bands = []

        # Check if the axis is already defined
        if any([d.name == kwargs["name"] for d in init_bands]):
            for d in init_bands:
                if d.name == kwargs["name"]:
                    init_bands.remove(d)

        # Load and append the new curator
        band = mlstac_spectralbands.SpectralBand(**kwargs)
        init_bands.append(band)

        # Save the new dimensions
        self.ml_spectral = mlstac_spectralbands.SpectralBands(bands=init_bands)

        print("Dimensions added to self.ml_spectral")

        return None

    def add_sensor(self, sensor: str):
        """Add the sensor of the spectral bands."""
        if self.ml_spectral is None:
            raise ValueError("There are no spectral bands")

        self.ml_spectral = mlstac_spectralbands.SpectralBands(
            bands=self.ml_spectral.bands, axis=self.ml_spectral.axis, sensor=sensor
        )

        print("Specral information added to self.ml_spectral")
        return None

    def add_sentinel2(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_sentinel2(self, bands=bands)
        return None

    def add_landsat1(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat1(self, bands=bands)
        return None

    def add_landsat2(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat2(self, bands=bands)
        return None

    def add_landsat3(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat3(self, bands=bands)
        return None

    def add_landsat4_mss(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat4_mss(self, bands=bands)
        return None

    def add_landsat4_tm(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat4_tm(self, bands=bands)
        return None

    def add_landsat5_mss(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat5_mss(self, bands=bands)
        return None

    def add_landsat5_tm(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat5_tm(self, bands=bands)
        return None

    def add_landsat7(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat7(self, bands=bands)
        return None

    def add_landsat8(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat8(self, bands=bands)
        return None

    def add_landsat9(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_landsat9(self, bands=bands)
        return None

    def add_eo1_ali(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_eo1_ali(self, bands=bands)
        return None

    def add_aster(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_aster(self, bands=bands)
        return None

    def add_modis(self, bands: str = "all"):
        self.ml_spectral = None
        mlstac_sensors.add_modis(self, bands=bands)
        return None

    def add_raw_data_url(self, url: str):
        self.ml_raw_data_url = str(pydantic.AnyHttpUrl(url))
        print("Raw information added to self.ml_raw_data_url")
        return None

    def add_discussion_url(self, url: str):
        self.ml_discussion_url = str(pydantic.AnyHttpUrl(url))
        print("Discussion added to self.ml_discuss_url")
        return None

    def add_split_strategy(self, split_strategy: str):
        self.ml_split_strategy = split_strategy
        print("Split added to self.ml_split")
        return None

    def add_paper(self, url: str):
        """This method adds the paper of the dataset."""
        self.ml_paper = str(pydantic.AnyHttpUrl(url))
        print("Paper added to self.ml_discussion_url")
        return None

    def create_markdown(self, outfile: Union[str, pathlib.Path]) -> None:
        """Add the documentation of the MLSTAC collection."""
        auto_documentation.add_documentation(ml_collection=self, outfile=outfile)
        return None

    def create_json(self, outfile: Union[str, pathlib.Path]) -> None:
        """Create the ML-STAC file."""
        json_dict = self.model_dump()
        with open(outfile, "w") as f:
            json.dump(json_dict, f, indent=4, default=str)
