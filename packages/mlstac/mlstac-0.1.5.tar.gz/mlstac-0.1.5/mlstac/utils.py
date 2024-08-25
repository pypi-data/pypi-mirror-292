import base64
import json
import pathlib
import re
import zlib
from typing import List, Union
from urllib.parse import urlparse

import pandas as pd
import requests


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc])
    except ValueError:
        return False


def compress_string(input_string):
    # Compress the string using zlib
    compressed_data = zlib.compress(input_string.encode("utf-8"))

    # Encode the compressed data to base64 to get a string output
    compressed_string = base64.b64encode(compressed_data).decode("utf-8")

    return compressed_string


def from_mlstac_to_df_download(
    metadata: dict, path: Union[pathlib.Path, str], splits: List[str]
) -> pd.DataFrame:
    # Load the metadata
    concat_list = []
    for split_idx in splits:

        # Save the metadata
        metadata_url_file = metadata["ml_catalog"][split_idx]["metadata_file"]
        metadata_checksum = metadata["ml_catalog"][split_idx]["metadata_checksum"]
        metadata_local_file = (
            pathlib.Path(path) / split_idx / "mls" / metadata_url_file.split("/")[-1]
        )
        metadata_local_file.parent.mkdir(parents=True, exist_ok=True)
        concat_list.append(
            {
                "url": metadata_url_file,
                "local": metadata_local_file,
                "checksum": metadata_checksum,
            }
        )

        # Save the data files
        data_files = metadata["ml_catalog"][split_idx]["data_files"]
        for idx, data_file in enumerate(data_files):
            data_url_file = data_file
            data_local_file = (
                pathlib.Path(path) / split_idx / "mls" / data_file.split("/")[-1]
            )
            data_checksum = metadata["ml_catalog"][split_idx]["data_checksum"][idx]
            concat_list.append(
                {
                    "url": data_url_file,
                    "local": data_local_file,
                    "checksum": data_checksum,
                }
            )

    # Download the files
    download_db = pd.DataFrame(concat_list)

    return download_db


def load_mlstac_collection_file(snippet: Union[str, pathlib.Path, dict]) -> dict:
    """Load a MLSTAC collection file

    Args:
        snippet (Union[str, pathlib.Path, dict]): The snippet of the

    Returns:
        dict: The MLSTAC collection file.
    """

    # Load the MLSTAC collection file
    if not (isinstance(snippet, str) or isinstance(snippet, pathlib.Path)):
        return snippet, "remote"
    else:
        snippet = str(snippet)

    # Get the snippet file name if is a URL
    regex_compile = re.compile(r"^[\w-]+/[\w-]+$")

    # is your dataset in HF Datasets?
    if regex_compile.match(snippet):
        snippet_file = (
            f"https://huggingface.co/datasets/{snippet}/resolve/main/main.json"
        )
        with requests.get(snippet_file) as response:
            mlstac_collection = response.json()
        return mlstac_collection, "remote"

    # is your dataset a local file?
    if pathlib.Path(snippet).exists():
        snippet_file = snippet
        with open(snippet_file) as f:
            mlstac_collection = json.load(f)
        return mlstac_collection, "local"

    # is your dataset a valid URL?
    if is_valid_url(snippet):
        snippet_file = snippet
        with requests.get(snippet_file) as response:
            mlstac_collection = response.json()
        return mlstac_collection, "remote"


def download_file_with_recovery(
    url: str,
    local_filename: pathlib.Path,
    checksum: int,
    chunk_size: int = 1024 * 1024 * 100,
    quiet: bool = False,
) -> None:
    """Download a file with recovery capabilities

    This function downloads a file from a URL with the capability of
    resuming the download from a specific byte. If the file is already
    downloaded, the function checks the checksum and returns the
    local filename.

    Args:
        url (str): The URL of the file to download.
        local_filename (pathlib.Path): The local filename to save the file.
        checksum (int): The checksum of the file.
        chunk_size (int, optional): The size of the chunks to download. By
            default, it is 100 MB.
        quiet (bool, optional): If True, the function does not print any
            message. By default, it is False.

    Returns:
        None: The function does not return any value.
    """

    # Determine the starting point for the download
    start = 0
    if pathlib.Path(local_filename).exists():
        start = pathlib.Path(local_filename).stat().st_size

    # Check if the file is already downloaded
    if start == checksum:
        return None

    # Define the headers for the HTTP request
    headers = {"Range": f"bytes={start}-"}

    # Download the file
    with requests.get(url, headers=headers, stream=True) as response:

        # Check if the response is successful
        response.raise_for_status()

        # Open the file in append mode if the file already exists
        mode = "ab" if start > 0 else "wb"

        with open(local_filename, mode) as f:

            # Print a message if the download is resumed
            if start != 0:
                start_gb = start / 1024 / 1024 / 1024
                if not quiet:
                    print(f"Resuming download from byte {start} ({start_gb:.2f} GB)")

            # Download the file
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

    return None


def from_mlstac_to_metadata_parquet(
    mlstac_collection: dict, state: str, snippet: pathlib.Path
) -> pd.DataFrame:
    """Convert a MLSTAC collection to a metadata parquet file

    Every MLSTAC collection has three splits: train, validation, and test.
    This function reads the metadata of each split and concatenates them
    into a single DataFrame. This is useful to create a metadata DataFrame
    that can be queried to extract information about the dataset.

    Args:
        mlstac_collection (dict): The MLSTAC collection.
        state (str): The state of the MLSTAC collection. It can be
            "remote" or "local".
        snippet (pathlib.Path): The snippet of the MLSTAC collection.

    Returns:
        pd.DataFrame: The metadata as a DataFrame.
    """

    splits = ["train", "validation", "test"]
    concat_list = []
    if state == "remote":
        for split_idx in splits:
            # Get the metadata URL
            metadata_url_file = mlstac_collection["ml_catalog"][split_idx][
                "metadata_file"
            ]
            if metadata_url_file is None:
                continue

            # Download the metadata
            metadata_dataset = pd.read_parquet(str(metadata_url_file))
            concat_list.append(metadata_dataset)
    elif state == "local":
        data_path: pathlib.Path = pathlib.Path(snippet).parent
        for split_idx in splits:
            # Get the metadata file
            metadata_local_file = data_path / split_idx / "mls" / "metadata.parquet"
            if metadata_local_file.exists():
                metadata_dataset = pd.read_parquet(metadata_local_file)
                metadata_dataset["file_path"] = list(
                    metadata_dataset["url"].apply(
                        lambda x: metadata_local_file.parent / x.split("/")[-1]
                    )
                )
                concat_list.append(metadata_dataset)

    results = pd.concat(concat_list)
    results["state"] = state

    return results
