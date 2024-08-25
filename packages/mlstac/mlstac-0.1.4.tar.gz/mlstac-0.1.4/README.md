# mlstac

A Common Language for EO Machine Learning Data


```python
import mlstac

# Read the data online
path = "https://huggingface.co/datasets/JulioContrerasH/prueba1/resolve/main/images_2000.mlstac"
metadata = mlstac.core.load_metadata(path)
data = mlstac.core.load_data(metadata[0:4])
data.shape

# Read the data locally
path = "/home/cesar/Downloads/images_2000.mlstac"
dataset = mlstac.core.load_metadata(path)
data = mlstac.core.load_data(dataset[0:4])

# From mlstac to GEOTIFF
import rasterio as rio
path = "https://huggingface.co/datasets/JulioContrerasH/prueba1/resolve/main/images_2000.mlstac"
metadata = mlstac.core.load_metadata(path)
data, metadata = mlstac.core.load_data(metadata[0:1], save_metadata_datapoint=True)[0]
with rio.open("data.tif", "w", **metadata) as dst:
    dst.write(data)
```
