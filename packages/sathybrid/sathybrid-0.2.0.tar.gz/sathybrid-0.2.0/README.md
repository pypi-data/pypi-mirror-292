# sathybrid
A Python package to fusion LR and HR imagery


## Installation
```bash
pip install sathybrid
```

## Usage

```python
import sathybrid
import pathlib


# Select the HR image
PATH = pathlib.Path("/home/cesar/demo/NA5120_E1186N0724/")
HRfile = PATH / "naip" / "m_3812243_nw_10_060_20220524.tif"

# Find the most similar LR image
data_stats = sathybrid.utils.find_similar_lr(
    hr_file=HRfile,
    lr_folder=PATH / "s2",
    hr_bands=[1, 2, 3],
    hr_normalization=255,
    lr_bands=[3, 2, 1],
    lr_normalization=10_000,
    downsampling_method="lanczos3",
    method="fft_l1",
)

# Select the best LR image
LRfile = PATH / "s2" / (data_stats.iloc[0]["lr_img"] + ".tif")

# Define the output path
OUTfile = PATH / "fusion.tif"

# Fusion
sathybrid.image_fusion(
    hr_file=HRfile,
    lr_file=LRfile,
    output_file=OUTfile,
    hr_bands=[1, 2, 3],
    hr_normalization=255,
    lr_bands=[3, 2, 1],
    lr_normalization=10_000,
    upsampling_method="lanczos3",
    fourier=True,
    fourier_params={"method": "ideal", "order": 6, "sharpness": 3},
    scale_factor=8,
    denoise=True,
)    
```