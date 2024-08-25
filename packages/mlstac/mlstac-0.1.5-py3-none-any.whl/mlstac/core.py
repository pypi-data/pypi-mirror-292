"""Core functions for reading and writing MLSTAC files.

This module contains the core functions for reading and writing MLS files.

# Local reading functions

- read_mlstac_metadata_local: Read the metadata of a MLSTAC file given a path.
- read_mlstac_data_local: Read the data of a MLSTAC file given a path.

# Remote reading functions

- read_mlstac_metadata_url: Read the metadata of a MLSTAC file given a URL.
- read_mlstac_data_url: Read the data of a MLSTAC file given a URL.

# Target encoding/decoding functions

- encode_json_array: Encode a dictionary as a NumPy array.
- decode_json_array: Decode a NumPy array as a dictionary.

# High-level functions
- load_metadata: Load the metadata of a MLSTAC file.
- load_data: Load the data of a MLSTAC file.
"""

import json
import pathlib
import struct
from io import BytesIO
from typing import List, Optional, Tuple, Union, Literal

import numpy as np
import pandas as pd
import rasterio as rio
import requests

import mlstac.utils


def read_mlstac_metadata_local(file: Union[str, pathlib.Path]) -> dict:
    """Read the metadata of a .mls file

    Args:
        file (Union[str, pathlib.Path]): A .mls file.

    Returns:
        dict: The metadata of the .mls file.
    """

    with open(file, "rb") as f:
        # Read the FIRST 2 bytes of the file
        nmagic = f.read(2)

        if nmagic != b"#y":
            raise ValueError("The file is not a '.mlstac' file")

        # Read the NEXT 8 bytes of the file
        header_len = f.read(8)

        # Convert bytes to uint64
        length = int.from_bytes(header_len, "little")

        # Read the HEADER considering the length (JSON)
        header = f.read(length)

        # Read the bytes 100-200
        header: dict = json.loads(header.decode())

    return header


def read_mlstac_data_local(
    file: Union[str, pathlib.Path],
    datapoint: pd.Series,
    metadata_length: Optional[dict] = None,
) -> Tuple[np.ndarray, dict]:
    """Read the data of a mlstac file

    Args:
        file (Union[str, pathlib.Path]): The file to read.
        datapoint (pd.Series): The datapoint to read.
        metadata_length (Optional[dict], optional): The length of the
            metadata. If None, the code seeks the metadata of the file.
            Defaults to None.

    Returns:
        Tuple[np.ndarray, dict]: The data and metadata of the
            datapoint.
    """

    # Read the metadata
    if metadata_length is None:
        metadata = read_mlstac_metadata_local(file)
        metadata_length = len(json.dumps(metadata))

    # Define fseek
    fseek: int = datapoint["begin"] + metadata_length + 2 + 8

    with open(file, "rb") as f:
        # Move the pointer to the right position
        f.seek(fseek)

        # Read the specific bytes
        data: bytes = f.read(datapoint["length"])

        # Convert the bytes to a rasterio object
        with BytesIO() as bio:
            bio.write(data)
            bio.seek(0)
            with rio.open(bio) as src:
                data = src.read()
                metadata = src.meta
        
    return data, metadata


def read_mlstac_metadata_url(url: str) -> dict:
    """Read the metadata of a mlstac file given a URL. The
    server must support the HTTPS Range Request.

    Args:
        url (str): The URL of the file.

    Returns:
        Tuple[dict, int]: The metadata of the mlstac file
        and the length of the header.
    """

    # Fetch the first 8 bytes of the file
    headers = {"Range": "bytes=2-9"}
    response: requests.Response = requests.get(url, headers=headers)

    # Interpret the bytes as a little-endian unsigned 64-bit integer
    length_of_header: int = struct.unpack("<Q", response.content)[0] + 9

    # Fetch length_of_header bytes starting from the 9th byte
    headers = {"Range": f"bytes=10-{length_of_header}"}

    with requests.get(url, headers=headers) as response:
        # Interpret the response as a JSON object
        header = json.loads(response.content)

    return header


def read_mlstac_data_url(
    url: str, datapoint: pd.Series, metadata_length: Optional[int] = None
) -> Tuple[np.ndarray, dict]:
    """Read the data of a mlstac file given a URL.
    The server must support HTTPS Range Request.

    Args:
        URL (Union[str, pathlib.Path]): The file to be read.
        datapoint_id (str): The ID of the datapoint to read.
        length_metadata (Optional[int], optional): The length of the
            metadata. If None, the code seeks the metadata of the file.
            Defaults to None.

    Returns:
        Tuple[np.ndarray, dict]: The data and metadata of the
            datapoint.
    """

    # Read the metadata
    if metadata_length is None:
        metadata = read_mlstac_metadata_url(url)
        metadata_length = len(json.dumps(metadata))

    # Define the byte range to read the data
    fseek = datapoint["begin"] + metadata_length + 2 + 8

    # Define the HTTP Range Request
    headers = {"Range": f'bytes={fseek}-{fseek + datapoint["length"] - 1}'}

    # Fetch the data
    with requests.get(url, headers=headers) as response:
        response.raise_for_status()
        with BytesIO() as bio:
            bio.write(response.content)
            bio.seek(0)            
            with rio.open(bio) as src:
                data = src.read()
                metadata = src.meta

    return data, metadata

def encode_json_array(
    data: dict, shape: tuple[int, int], dtype: np.dtype
) -> np.ndarray:
    """Encode a dictionary as a NumPy array.

    Args:
        data (dict): The dictionary to encode.
        shape (tuple[int, int]): The shape of the NumPy array.
        dtype (np.dtype): The data type of the NumPy array.

    Returns:
        np.ndarray: The NumPy array.
    """

    # Convert dictionary to JSON string
    json_bytes = json.dumps(data).encode("utf-8")

    # Convert the NumPy array to bytes
    array = np.zeros(shape, dtype=dtype)
    byte_data = array.tobytes()

    # Convert from bytes to bytearray
    byte_data_arr = bytearray(byte_data)

    # Replace eight bytes with the length of the JSON string (UInt64)
    len_bytes = struct.pack("Q", len(json_bytes))
    byte_data_arr[:8] = len_bytes
    byte_data_arr[8 : (8 + len(json_bytes))] = json_bytes

    return np.frombuffer(byte_data_arr, dtype=np.uint16).reshape(array.shape)


def decode_json_array(array: np.ndarray) -> dict:
    """Decode a NumPy array as a dictionary.

    Args:
        data (dict): The dictionary to encode.
        shape (tuple[int, int]): The shape of the NumPy array.
        dtype (np.dtype): The data type of the NumPy array.

    Returns:
        np.ndarray: The NumPy array.
    """

    # Convert the NumPy array to bytes
    byte_data = array.tobytes()

    # Read the length of the JSON string
    len_bytes = byte_data[:8]
    header_len = struct.unpack("Q", len_bytes)[0]

    # Read the JSON string
    json_bytes = byte_data[8 : (8 + header_len)]

    # Convert the JSON string to a dictionary
    return json.loads(json_bytes.decode("utf-8"))


def load_metadata(path: Union[str, pathlib.Path]) -> pd.DataFrame:
    """Load a MLSTAC file

    Args:
        path (Union[str, pathlib.Path]): The path to the MLSTAC file.
            It can be a local path or a URL. If it is a URL, the
            server must support the HTTP Range requests.

    Returns:
        pd.DataFrame: The dataframe with three columns: 'datapoint_id',
            'begin', and 'length'. The 'datapoint_id' is the ID of the
            datapoint, 'begin' is the byte where the datapoint starts,
            and 'length' is the length of the datapoint in bytes.
    """

    # Convert the path to a string
    path = path.as_posix() if isinstance(path, pathlib.Path) else path

    # Obtain the file metadata
    if mlstac.utils.is_valid_url(path):
        dataset = read_mlstac_metadata_url(path)
        status = "remote"
    else:
        dataset = read_mlstac_metadata_local(path)
        status = "local"

    # Obtaint the length header
    length_dataset = len(json.dumps(dataset))

    # Convert dataset to DataFrame
    datapoints = list(dataset.items())
    metadata = pd.DataFrame(datapoints, columns=["datapoint_id", "values"])

    # Expand 'values' into 'begin' and 'length' columns
    metadata[["begin", "length"]] = pd.DataFrame(
        metadata["values"].tolist(), index=metadata.index
    )
    metadata = metadata.drop(columns="values")
    metadata.attrs.update(
        {"status": status, "path": path, "length_dataset": length_dataset}
    )

    return metadata


def load_data(
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

    # The dataset must have the attribute 'state' that indicates if the
    # data is remote or local.
    state: Literal["remote", "local"] = dataset.attrs["status"]


    def data_generator():
        for idx, row in dataset.iterrows():
            # Print the progress of the download
            if not quiet:
                print(f"Downloading datapoint: {row['datapoint_id']}")
            
            # Read the data and metadata of the datapoint according to the state
            if state == "remote":
                data, metadata = read_mlstac_data_url(
                    url=dataset.attrs["path"],
                    datapoint=row,
                    metadata_length=dataset.attrs["length_dataset"],
                )
            elif state == "local":
                data, metadata = read_mlstac_data_local(
                    file=dataset.attrs["path"],
                    datapoint=row,
                    metadata_length=dataset.attrs["length_dataset"],
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