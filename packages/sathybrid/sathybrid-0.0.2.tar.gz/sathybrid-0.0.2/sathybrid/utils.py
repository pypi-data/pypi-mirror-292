import pathlib
from typing import Literal, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio as rio
import torch
from skimage.exposure import match_histograms

from sathybrid.kernels import (butterworth_filter, gaussian_filter,
                               ideal_filter, sigmoid_filter)
from sathybrid.resize import resize


def hq_histogram_matching(image1: torch.Tensor, image2: torch.Tensor) -> torch.Tensor:
    """Lazy implementation of histogram matching

    Args:
        image1 (torch.Tensor): The low-resolution image (C, H, W).
        image2 (torch.Tensor): The super-resolved image (C, H, W).

    Returns:
        torch.Tensor: The super-resolved image with the histogram of
            the target image.
    """

    # Go to numpy
    np_image1 = image1.detach().cpu().numpy()
    np_image2 = image2.detach().cpu().numpy()

    if np_image1.ndim == 3:
        np_image1_hat = match_histograms(np_image1, np_image2, channel_axis=0)
    elif np_image1.ndim == 2:
        np_image1_hat = match_histograms(np_image1, np_image2, channel_axis=None)
    else:
        raise ValueError("The input image must have 2 or 3 dimensions.")

    # Go back to torch
    image1_hat = torch.from_numpy(np_image1_hat).to(image1.device)

    return image1_hat


def find_similar_lr(
    hr_file: Union[str, pathlib.Path],
    lr_folder: Union[str, pathlib.Path],
    hr_bands: Optional[list[int]] = [1, 2, 3],
    hr_normalization: Optional[int] = 255,
    lr_bands: Optional[list[int]] = [1, 2, 3],
    lr_normalization: Optional[int] = 10_000,
    method: Literal["l1", "l2", "correlation", "cosine_similarity", "fft_l1"] = "l1",
    downsampling_method: str = "lanczos3",
) -> pd.DataFrame:
    """Calculate the similarity score between two images using the L1 loss.

    Args:
        hr_file (Union[str, pathlib.Path]): The high-resolution image.
        lr_folder (Union[str, pathlib.Path]): The folder containing the low-resolution images.
        hr_bands (Optional[list[int]]): The bands to use for the high-resolution image.
        hr_normalization (Optional[int]): The normalization value for the high-resolution image.
        lr_bands (Optional[list[int]]): The bands to use for the low-resolution image.
        lr_normalization (Optional[int]): The normalization value for the low-resolution image.
        method (Literal["l1", "l2", "correlation", "cosine_similarity", "fft_l1"]): The method to use for the similarity score.
        downsampling_method (str): The method to use for downsampling the high-resolution image.

    Returns:
        pd.DataFrame: The similarity scores.
    """
    # Go to pathlib
    hr_file = pathlib.Path(hr_file)

    # Load the HR images
    with rio.open(hr_file) as src:
        hr_data = src.read(hr_bands) / hr_normalization

    # Load the LR images
    lr_files = list(pathlib.Path(lr_folder).glob("*.tif"))

    np_container = []
    for lr_file in lr_files:
        with rio.open(lr_file) as src:
            lr_data = src.read(lr_bands) / lr_normalization
        np_container.append(lr_data)
    lr_data = np.stack(np_container)

    # Downsample the high-resolution image
    lr_shape = lr_data.shape[-2:]
    hr_shape = hr_data.shape
    hr_shape_down = (len(hr_bands), lr_shape[0], lr_shape[1])

    # Resize the high-resolution image
    hr_data_down = resize(
        image=torch.from_numpy(hr_data), shape=hr_shape_down, method=downsampling_method
    ).float()

    container_dict = []
    for idx, lr_img in enumerate(lr_data):
        # Go to torch
        lr_img_torch = torch.from_numpy(lr_img).float()

        # Histogram matching between the LR and HR images
        hr_img_fixed = hq_histogram_matching(image1=hr_data_down, image2=lr_img_torch)

        # Calculate the similarity score
        if method == "l1":
            metric = get_metric(x=hr_img_fixed, y=lr_img_torch, method="l1")
        elif method == "l2":
            metric = get_metric(x=hr_img_fixed, y=lr_img_torch, method="l2")
        elif method == "cosine_similarity":
            metric = get_metric(
                x=hr_img_fixed, y=lr_img_torch, method="cosine_similarity"
            )
        elif method == "fft_l1":
            metric = get_metric(x=hr_img_fixed, y=lr_img_torch, method="fft_l1")

        # Store the results
        container_dict.append(
            {
                "metric": metric.item(),
                "lr_img": lr_files[idx].stem,
                "hr_img": hr_file.stem,
            }
        )

    dataset = pd.DataFrame(container_dict).sort_values("metric")
    dataset.reset_index(drop=True, inplace=True)

    return dataset


def get_metric(x: torch.Tensor, y: torch.Tensor, method: str = "l1"):
    """Calculate the similarity score between two images using the L1 loss.

    Args:
        x (torch.Tensor): The low-resolution image.
        y (torch.Tensor): The high-resolution image.

    Returns:
        torch.Tensor: The similarity score.
    """

    if method == "l1":
        metric = torch.abs(x - y).mean()
    elif method == "l2":
        metric = torch.sqrt((x - y) ** 2 / len(x)).mean()
    elif method == "cosine_similarity":
        metric = 1 - torch.nn.functional.cosine_similarity(x, y, dim=0).mean()
    elif method == "fft_l1":
        x_fft = torch.fft.fftn(x)
        y_fft = torch.fft.fftn(y)
        metric = torch.nn.functional.l1_loss(x_fft, y_fft)
    else:
        raise ValueError(f"Unknown method {method}")

    return metric


def display_kernel_fusion(
    shape: tuple[int, int],
    cutoff: int,
    order: int,
    sharpness: int,
):
    """Display the kernel for the fusion process.

    Args:
        shape (tuple[int, int]): The shape of the kernel.
        cutoff (int): The cutoff frequency.
        order (int): The order of the Butterworth filter.
        sharpness (int): The sharpness of the sigmoid filter.
    """
    # Generate filters
    ideal_filt = ideal_filter(shape, cutoff)
    butter_filt = butterworth_filter(shape, cutoff, order)
    gaussian_filt = gaussian_filter(shape, torch.tensor(cutoff, dtype=torch.float32))
    sigmoid_filt = sigmoid_filter(
        shape,
        torch.tensor(cutoff, dtype=torch.float32),
        torch.tensor(sharpness, dtype=torch.float32),
    )

    # Plot filters
    filters = [ideal_filt, butter_filt, gaussian_filt, sigmoid_filt]
    titles = ["Ideal Filter", "Butterworth Filter", "Gaussian Filter", "Sigmoid Filter"]

    ax, fig = plt.subplots(2, 2, figsize=(12, 8))
    for i, filt in enumerate(filters):
        fig[i // 2, i % 2].imshow(filt.numpy(), cmap="gray")
        fig[i // 2, i % 2].set_title(titles[i])
        fig[i // 2, i % 2].axis("off")
    plt.tight_layout()

    return ax, fig
