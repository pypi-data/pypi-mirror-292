# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['satalign', 'satalign.lightglue']

package_data = \
{'': ['*']}

install_requires = \
['kornia[deep]>=0.7.2',
 'numpy>=1.25.2',
 'opencv-python[ecc]>=4.8.0.76',
 'pandas>=2.0.3',
 'rasterio>=1.3.10',
 'scikit-image[pcc]>=0.23.1',
 'torch[deep]>=2.0.0',
 'xarray>=2023.7.0']

setup_kwargs = {
    'name': 'satalign',
    'version': '0.1.5',
    'description': 'Methods for spatial alignment of satellite imagery',
    'long_description': '# \n\n<p align="center">\n  <img src="https://huggingface.co/datasets/JulioContrerasH/DataMLSTAC/resolve/main/banner_satalign.png" width="100%">\n</p>\n\n<p align="center">\n    <em>A Python package for efficient multi-temporal image co-registration</em> 🚀\n</p>\n\n<p align="center">\n<a href=\'https://pypi.python.org/pypi/satalign\'>\n    <img src=\'https://img.shields.io/pypi/v/satalign.svg\' alt=\'PyPI\' />\n</a>\n<a href="https://opensource.org/licenses/MIT" target="_blank">\n    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">\n</a>\n<a href="https://github.com/psf/black" target="_blank">\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">\n</a>\n<a href="https://pycqa.github.io/isort/" target="_blank">\n    <img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336" alt="isort">\n</a>\n</p>\n\n---\n\n**GitHub**: [https://github.com/IPL-UV/satalign](https://github.com/IPL-UV/satalign) 🌐\n\n**PyPI**: [https://pypi.org/project/satalign/](https://pypi.org/project/satalign/) 🛠️\n\n---\n\n## Overview 📊\n\n**Satalign** is a Python package designed for efficient multi-temporal image co-registration. It enables aligning temporal data cubes with reference images using advanced techniques such as Phase Cross-Correlation (PCC), Enhanced Cross-Correlation (ECC), and Local Features Matching (LGM). This package facilitates the manipulation and processing of large volumes of Earth observation data efficiently.\n\n## Key features ✨\n- **Advanced alignment algorithms**: Leverages ECC, PCC, and LGM to accurately align multi-temporal images. 🔍\n- **Efficient data cube management**: Processes large data cubes with memory and processing optimizations. 🧩\n- **Support for local feature models**: Utilizes models like SuperPoint, SIFT, and more for keypoint matching. 🖥️\n- **Parallelization**: Executes alignment processes across multiple cores for faster processing. 🚀\n\n## Installation ⚙️\nInstall the latest version from PyPI:\n\n\n```bash\npip install satalign\n```\n\n## How to use 🛠️\n\n\n### Align an ee.ImageCollection with `satalign.PCC` 🌍\n\n```python\nimport fastcubo\nimport ee\nimport satalign\n\nee.Initialize(opt_url="https://earthengine-highvolume.googleapis.com")\n\n# Download an image collection\ntable = fastcubo.query_getPixels_imagecollection(\n    point=(-75.71260, -14.18835),\n    collection="COPERNICUS/S2_HARMONIZED",\n    bands=["B2", "B3", "B4", "B8"],\n    data_range=["2018-01-01", "2024-12-31"],\n    edge_size=256, \n    resolution=10, \n)\n\nfastcubo.getPixels(table, nworkers=10, output_path="output/aligned_images/s2")\n\n# Create the data cube\ns2_datacube = satalign.utils.create_array("output/aligned_images/s2", "output/datacube_pcc.pickle")\n\n# Define the reference image\nreference_image = s2_datacube.sel(time=s2_datacube.time > "2024-01-03").mean("time")\n\n# Initialize the PCC model\npcc_model = satalign.PCC(\n    datacube=s2_datacube, # T x C x H x W\n    reference=reference_image, # C x H x W\n    channel="mean",\n    crop_center=128,\n    num_threads=2,\n)\n\n# Run the alignment on multiple cores\naligned_cube, warp_matrices = pcc_model.run_multicore()\n\n```\n\n### Align an Image Collection with `satalign.ECC` 📚\n\n```python\nimport fastcubo\nimport ee\nimport satalign\n\nee.Initialize(opt_url="https://earthengine-highvolume.googleapis.com")\n\n# Download an image collection\ntable = fastcubo.query_getPixels_imagecollection(\n    point=(51.079225, 10.452173),\n    collection="COPERNICUS/S2_HARMONIZED",\n    bands=["B4", "B3", "B2"],\n    data_range=["2016-06-01", "2017-07-01"],\n    edge_size=128,\n    resolution=10,\n)\n\nfastcubo.getPixels(table, nworkers=4, output_path="output/aligned_images/ecc")\n\n# Create the data cube\ns2_datacube = satalign.utils.create_array("output/aligned_images/ecc", "output/datacube_ecc.pickle")\n\n# Define the reference image\nreference_image = s2_datacube.isel(time=0)\n\n# Initialize the ECC model\necc_model = satalign.ECC(\n    datacube=s2_datacube, \n    reference=reference_image,\n    gauss_kernel_size=3,\n)\n\n# Run the alignment\naligned_cube, warp_matrices = ecc_model.run()\n```\n### Align using Local Features with `satalign.LGM` 🧮\n\n```python\nimport fastcubo\nimport ee\nimport satalign\n\nee.Initialize(opt_url="https://earthengine-highvolume.googleapis.com")\n\n# Download an image collection\ntable = fastcubo.query_getPixels_imagecollection(\n    point=(-76.5, -9.5),\n    collection="NASA/NASADEM_HGT/001",\n    bands=["elevation"],\n    edge_size=128,\n    resolution=90\n)\n\nfastcubo.getPixels(table, nworkers=4, output_path="output/aligned_images/lgm")\n\n# Create the data cube\ndatacube = satalign.utils.create_array("output/aligned_images/lgm", "output/datacube_lgm.pickle")\n\n# Define the reference image\nreference_image = datacube.isel(time=0)\n\n# Initialize the LGM model\nlgm_model = satalign.LGM(\n    datacube=datacube, \n    reference=reference_image, \n    feature_model="superpoint",\n    matcher_model="lightglue",\n)\n\n# Run the alignment\naligned_cube, warp_matrices = lgm_model.run()\n```\n\nIn this document, we presented three different examples of how to use SatAlign with PCC, ECC, and LGM for multi-temporal image co-registration. Each example shows how to download an image collection from Google Earth Engine, create a data cube, and align the images using one of the three methods provided by the SatAlign package.',
    'author': 'Cesar Aybar',
    'author_email': 'cesar.aybar@uv.es',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/csaybar/satalign',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
