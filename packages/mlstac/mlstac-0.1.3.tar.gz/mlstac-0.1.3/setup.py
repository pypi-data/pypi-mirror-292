# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlstac',
 'mlstac.specification',
 'mlstac.specification.catalog',
 'mlstac.specification.collection',
 'mlstac.specification.sample']

package_data = \
{'': ['*']}

install_requires = \
['mdutils>=1.6.0',
 'numpy>=1.26.4',
 'pandas>=2.1.4',
 'pydantic>=2.3.0',
 'rasterio>=1.3.10',
 'requests>=2.00.0',
 'tqdm>=4.00.0']

setup_kwargs = {
    'name': 'mlstac',
    'version': '0.1.3',
    'description': 'A Common Language for EO Machine Learning Data',
    'long_description': '# mlstac\n\nA Common Language for EO Machine Learning Data\n\n\n```python\nimport mlstac\n\n# Read the data online\npath = "https://huggingface.co/datasets/JulioContrerasH/prueba1/resolve/main/images_2000.mlstac"\nmetadata = mlstac.core.load_metadata(path)\ndata = mlstac.core.load_data(metadata[0:4])\ndata.shape\n\n# Read the data locally\npath = "/home/cesar/Downloads/images_2000.mlstac"\ndataset = mlstac.core.load_metadata(path)\ndata = mlstac.core.load_data(dataset[0:4])\n\n# From mlstac to GEOTIFF\nimport rasterio as rio\npath = "https://huggingface.co/datasets/JulioContrerasH/prueba1/resolve/main/images_2000.mlstac"\nmetadata = mlstac.core.load_metadata(path)\ndata, metadata = mlstac.core.load_data(metadata[0:1], save_metadata_datapoint=True)[0]\nwith rio.open("data.tif", "w", **metadata) as dst:\n    dst.write(data)\n```\n',
    'author': 'Cesar Aybar',
    'author_email': 'fcesar.aybar@uv.es',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/csaybar/mlstac',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
