import json
import pathlib
from typing import List, Union

import tqdm

import mlstac.specification.collection.stac as stac
import mlstac.core

from mlstac.main import download, get_data, load, prepare_data
from mlstac.specification.catalog.datamodel import Catalog, SingleCatalog
from mlstac.specification.collection.datamodel import Collection


def create_file(
    files: List[str],
    output: Union[str, pathlib.Path],
    chunk_size: int = 1024 * 1024 * 100,
) -> pathlib.Path:
    """Create a .mls file

    Args:
        files (List[str]): The list of files to be included in the
            MLSTAC file.
        output (Union[str, pathlib.Path]): The output file.

    Returns:
        pathlib.Path: The output file.
    """

    # Create the output file
    nmagic = b"#y"  # (31011).to_bytes(2, "little")
    dict_bytes = dict()

    # Get the total size of the files
    bytes_counter = 0
    for file in files:

        # Get the size of the file
        file_path = pathlib.Path(file)
        file_size: int = file_path.stat().st_size

        # Update the counter
        bytes_counter += file_size

        # Save the file size
        dict_bytes[file_path.stem] = [bytes_counter - file_size, file_size]

    # Encode the dictionary
    dict_bytes_enc: bytes = json.dumps(dict_bytes).encode()

    # Create the final file
    with open(output, "wb") as f:

        # Write the magic number
        f.write(nmagic)

        # Write the length of the HEADER
        f.write(len(dict_bytes_enc).to_bytes(8, "little"))

        # Write the HEADER
        f.write(dict_bytes_enc)

        # Write the data by chunks
        for file in tqdm.tqdm(files, desc="Creating MLSTAC file"):
            with open(file, "rb") as g:
                while True:
                    chunk = g.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)

    return output
