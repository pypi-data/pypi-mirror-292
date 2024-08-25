import gc
import json
import pathlib
import pickle
import tempfile
from typing import List, Literal, Tuple, Union

import numpy as np
import pandas as pd

import mlstac.datamodel
import mlstac.utils


def download(
    snippet: str,
    path: Union[str, pathlib.Path],
    split: Literal["train", "validation", "test", "all"] = "all",
    quiet: bool = False,
) -> pd.DataFrame:
    """Download the files of a MLSTAC collection.

    This function downloads the files of a MLSTAC collection. The
    function downloads the files of the collection according to the
    split. The split can be 'train', 'validation', 'test', or 'all'.

    Args:
        snippet (str): The URL of the MLSTAC Collection file.
        path (Union[str, pathlib.Path]): The path where the files
            will be downloaded.
        split: Literal["train", "validation", "test", "all"]: The
            split folder to download. The split can be 'train',
            'validation', 'test', or 'all'. Defaults to 'all'.
        quiet (bool, optional): Whether to print the progress of
            the download.

    Raises:
        ValueError: The split must be one of 'train', 'validation',
            'test', or 'all'.

    Returns:
        pd.DataFrame: The DataFrame with the files downloaded. There
            are three columns: 'url', 'local', and 'checksum'.
    """

    # Load the ML-STAC collection
    mlstac_collection, _ = mlstac.utils.load_mlstac_collection_file(snippet)
    mlstac_file = pathlib.Path(path) / "main.json"

    # Download the MLSTAC file
    with open(mlstac_file, "wb") as f:
        f.write(json.dumps(mlstac_collection).encode())

    # Prepare the files to download
    splits = {
        "all": ["train", "validation", "test"],
        "train": ["train"],
        "validation": ["validation"],
        "test": ["test"],
    }.get(split, None)

    if splits is None:
        raise ValueError(
            "The split must be one of 'train', 'validation', 'test', or 'all'."
        )

    # Define all the files to download and set it up the folder structures
    download_db: pd.DataFrame = mlstac.utils.from_mlstac_to_df_download(
        metadata=mlstac_collection, path=path, splits=splits
    )

    # Start the download
    for idx, row in download_db.iterrows():
        if not quiet:
            print(f"Downloading file {idx+1} of {len(download_db)}: {row['url']}")

        mlstac.utils.download_file_with_recovery(
            url=row["url"],
            local_filename=row["local"],
            checksum=row["checksum"],
            quiet=quiet,
        )

    return download_db


def load(snippet: Union[str, pathlib.Path, dict], force: bool = False) -> pd.DataFrame:
    """Load a MLSTAC collection.

    Args:
        snippet (Union[str, pathlib.Path, dict]): The URL of the MLSTAC
            Collection file, the path to the MLSTAC Collection file, or
            the MLSTAC Collection file as a dictionary.
        force (bool, optional): In the first time, the function saves
            the metadata as a parquet file in the temp folder. If the
            metadata file exists, the function loads the metadata from
            the file. To desactivate this behavior, set force to True.

    Returns:
        pd.DataFrame: The DataFrame with the MLSTAC Collection metadata.
    """

    # Before to prepare the metadata, check if the snippet is a dictionary
    tmp_folder = tempfile.gettempdir()

    if not isinstance(snippet, dict):
        tmp_filename = mlstac.utils.compress_string(str(snippet))
        tmp_mtd = pathlib.Path(tmp_folder) / tmp_filename
        condition = tmp_mtd.exists() and not force
    else:
        tmp_filename = mlstac.utils.compress_string(snippet["id"])
        tmp_mtd = pathlib.Path(tmp_folder) / tmp_filename
        condition = False

    # If the metadata exists, load the metadata from pickle file
    if condition:
        with open(tmp_mtd, "rb") as f:
            mlstac_object = pickle.load(f)
    else:

        # Load the ML-STAC collection
        mlstac_collection, state = mlstac.utils.load_mlstac_collection_file(
            snippet=snippet
        )

        # Prepare the metadata
        metadata_total = mlstac.utils.from_mlstac_to_metadata_parquet(
            mlstac_collection=mlstac_collection, state=state, snippet=snippet
        )

        # Return a MLSTAC object
        mlstac_object = mlstac.datamodel.MLSTAC(
            metadata=metadata_total, collection=mlstac_collection
        )

        # Save the MLS
        with open(tmp_mtd, "wb") as f:
            pickle.dump(mlstac_object, f)

    return mlstac_object


def get_data(
    dataset: Union[pd.DataFrame, pd.Series],
    save_metadata_datapoint: bool = False,
    return_generator: bool = False,
    quiet: bool = False,
) -> Union[np.ndarray, List[Tuple[np.ndarray, dict]]]:
    """Download the data of a MLSTAC file.

    Args:
        dataset (pd.DataFrame): A DataFrame with byte ranges of
            the datapoints.
        save_metadata_datapoint (bool, optional): Each datapoint
            has associated metadata. If True, the function returns
            a list of tuples with the data and metadata of each
            datapoint. If False, the function returns a numpy array
            with the data of each datapoint. Defaults to False.
        return_generator (bool, optional): Whether to return a
            generator with the data of the datapoints. Defaults
            to False.
        quiet (bool, optional): Whether to print the progress of
            the download. If the file is local, the progress is
            not printed. Defaults to False.

    Returns:
        Union[np.ndarray, List[Tuple[np.ndarray, dict]]]: The data
            of the datapoints. If save_metadata_datapoint is True,
            the function returns a list of tuples with the data and
            metadata of each datapoint. If save_metadata_datapoint
            is False, the function returns a numpy array with the
            data of each datapoint.
    """

    if isinstance(dataset, pd.Series):
        dataset = pd.DataFrame(dataset).T

    # The dataset must have the column 'state' that indicates if the
    # data is remote or local
    state = dataset.iloc[0]["state"]

    def data_generator():
        for idx, row in dataset.iterrows():
            # Print the progress of the download
            if not quiet:
                print(f"Reading datapoint: {row['datapoint_id']}")

            if state == "remote":
                # Read the data and metadata of the datapoint
                data, metadata = mlstac.core.read_mlstac_data_url(
                    url=row.url,
                    datapoint=row,
                    metadata_length=row.metadata_length,
                )
            else:
                # Read the data and metadata of the datapoint
                data, metadata = mlstac.core.read_mlstac_data_local(
                    file=row.file_path, datapoint=row, metadata_length=row.metadata_length
                )

            # Whether to save the metadata of the datapoint
            if save_metadata_datapoint:
                yield (data, metadata)
            else:
                yield data

    # Return the data as a generator
    generator = data_generator() 

    if return_generator:
        return generator
    else:
        data_list = list(generator)
        if save_metadata_datapoint:
            return data_list
        else:
            return np.array(data_list)


def prepare_data(
    mls_path: Union[str, pathlib.Path],
    safetensor_path: Union[str, pathlib.Path],
    split: Literal["train", "val", "validation", "test", "all"] = "all",
    verbose: bool = False,
):
    pass
