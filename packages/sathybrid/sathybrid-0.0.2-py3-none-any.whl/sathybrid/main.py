import pathlib
from typing import Literal, Optional, Union

import rasterio as rio
import requests
import torch

from sathybrid.blur import apply_kernel_to_image
from sathybrid.denoise_model import SwinIR
from sathybrid.kernels import (butterworth_filter, gaussian_filter,
                               ideal_filter, sigmoid_filter)
from sathybrid.resize import resize
from sathybrid.utils import hq_histogram_matching


def setup_denoiser(weight_path: Union[str, pathlib.Path, None] = None) -> SwinIR:
    """This function sets up the denoiser model.

    Args:
        weight_path (str): The path to the weights
            of the denoiser model.
    """
    if weight_path is None:
        weight_uri = "https://github.com/JingyunLiang/SwinIR/releases/download/v0.0/005_colorDN_DFWB_s128w8_SwinIR-M_noise15.pth"
        weight_path = pathlib.Path("weights/SwinIR_noise15.pth")
        weight_path.parent.mkdir(parents=True, exist_ok=True)
        if not weight_path.exists():
            with requests.get(weight_uri, stream=True) as r:
                with open(weight_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=4 * 1024):
                        f.write(chunk)

    # Define the denoiser model
    denoiser_model = SwinIR(
        upscale=1,
        in_chans=3,
        img_size=128,
        window_size=8,
        img_range=1.0,
        depths=[6, 6, 6, 6, 6, 6],
        embed_dim=180,
        num_heads=[6, 6, 6, 6, 6, 6],
        mlp_ratio=2,
        upsampler="",
        resi_connection="1conv",
    )
    denoiser_model.load_state_dict(torch.load(weight_path)["params"])
    denoiser_model.eval()

    # Disable gradient computation
    for param in denoiser_model.parameters():
        param.requires_grad = False

    return denoiser_model


def image_denoise(
    lr_data: torch.Tensor,
    denoiser_model: SwinIR,
    device: Union[str, torch.device] = "cuda",
) -> torch.Tensor:
    """Denoise a RGB Sentinel-2 image.

    Args:
        lr_data (np.ndarray): The low-resolution image.
        denoiser_model (SwinIR): The denoiser model.
        band_order (Optional[List[int]], optional): The order of the
            bands. Defaults to [2, 1, 0].

    Returns:
        np.ndarray: The denoised image.
    """

    # from numpy to torch
    img = lr_data.float()

    # 2 to 98 percentile for each channel
    img_norm = torch.zeros_like(img)
    quantile_2 = torch.zeros(3)
    quantile_98 = torch.zeros(3)
    for i in range(3):
        band = img[0, i]
        quantile = torch.quantile(band, torch.tensor([0.02, 0.98]))
        band_norm = (band - quantile[0]) / (quantile[1] - quantile[0])
        quantile_2[i] = quantile[0]
        quantile_98[i] = quantile[1]
        img_norm[0, i] = band_norm.clamp(0, 1)
    img_norm = img_norm.to(device)

    # Run the denoiser
    img_no_noise = denoiser_model.to(device)(img_norm)
    img_no_noise = img_no_noise.clamp(0, 1).cpu()

    # Go back to the original scale
    #denormalized_img = torch.zeros_like(img)
    #for i in range(3):
    #    denormalized_img[0, i] = (
    #        img_no_noise[0, i] * (quantile_98[i] - quantile_2[i]) + quantile_2[i]
    #    )
    #img_no_noise = denormalized_img[0].clamp(0, 6.5535).cpu()

    return img_no_noise


def image_fusion(
    hr_file: Union[str, pathlib.Path],
    lr_file: Union[str, pathlib.Path],
    output_file: Union[str, pathlib.Path],
    scale_factor: float,
    hr_bands: Optional[list[int]] = [1, 2, 3],
    hr_normalization: Optional[int] = 255,
    lr_bands: Optional[list[int]] = [1, 2, 3],
    lr_normalization: Optional[int] = 10_000,
    denoise: Optional[bool] = False,
    denoiser_model: Optional[SwinIR] = None,
    upsampling_method: Optional[
        Literal["nearest", "bilinear", "bicubic", "tricubic", "lanczos3", "lanczos5"]
    ] = "lanczos3",
    fourier: Optional[bool] = False,
    fourier_params: Optional[dict] = None,
) -> pathlib.Path:
    """Create a hybrid image using a low-frequency from Sentinel-2 and
    high-frequency from a high-resolution image.

    Args:
        lr_data (np.ndarray): The low-resolution image.
        hr_data (np.ndarray): The high-resolution image.
        interpolation_method (Optional[str], optional): The interpolation
            method to use. Defaults to "lanczos3".
        fourier (Optional[bool], optional): Whether to use Fourier
            interpolation. Defaults to False.
        antialias (Optional[bool], optional): Whether to apply antialiasing.
            Defaults to True.

    Returns:
        np.ndarray: The hybrid image.
    """
    if fourier_params is None:
        fourier_params = {"method": "butterworth", "order": 6, "sharpness": 3}
        fourier_params_method = fourier_params["method"]
        fourier_params_order = fourier_params["order"]
        fourier_params_sharpness = fourier_params["sharpness"]
    else:
        fourier_params_method = fourier_params["method"]
        fourier_params_order = fourier_params["order"]
        fourier_params_sharpness = fourier_params["sharpness"]

    # Load the HR images
    with rio.open(hr_file) as src:
        hr_data = src.read(hr_bands) / hr_normalization
        hr_data = torch.from_numpy(hr_data).float()
        hr_meta = src.meta

    # Load the LR images
    with rio.open(lr_file) as src:
        lr_data = src.read(lr_bands) / lr_normalization
        lr_data = torch.from_numpy(lr_data).float()
        lr_meta = src.meta

    if denoise:
        if denoiser_model is None:
            denoiser_model = setup_denoiser()

        # Denoise the image
        lr_data_denoise = image_denoise(
            lr_data=lr_data[None], denoiser_model=denoiser_model, device="cuda"
        ).float()[0]

        hr_data_denoise = image_denoise(
            lr_data=hr_data[None], denoiser_model=denoiser_model, device="cuda"
        ).float()[0]
    else:
        lr_data_denoise = lr_data
        hr_data_denoise = hr_data

    # Upsample the low-resolution image
    hr_shape = hr_data.shape
    lr_shape = lr_data.shape

    # Resize the low-resolution image
    lr_data_up = resize(
        image=lr_data_denoise, shape=hr_shape, method=upsampling_method, antialias=True
    )

    # Apply histogram matching to the high-resolution image
    hr_data_denoise = hq_histogram_matching(hr_data_denoise, lr_data_up).float()

    #import matplotlib.pyplot as plt
    #fig, axs = plt.subplots(1, 3, figsize=(10, 5))
    #axs[0].imshow(lr_data_up.numpy().transpose(1, 2, 0)*70)
    #axs[0].set_title("Low Resolution (Upsampled)")
    #axs[1].imshow(hybrid_image.numpy().transpose(1, 2, 0))
    #axs[1].set_title("Low Resolution")
    #axs[2].imshow(hr_data.numpy().transpose(1, 2, 0))
    #axs[2].set_title("High Resolution")
    #plt.show()


    # Estimate the error
    hr_data_down = resize(
        image=hr_data_denoise, shape=lr_shape, method=upsampling_method, antialias=True
    ).float()
    error = torch.abs(lr_data - hr_data_down).mean()

    if fourier:
        torch_container = torch.zeros_like(hr_data)
        for idx in range(hr_data.shape[0]):
            # Apply Fourier transform
            f1 = torch.fft.fft2(lr_data_up[idx])
            f2 = torch.fft.fft2(hr_data_denoise[idx])

            # Shift the zero-frequency component to the center
            f1_shifted = torch.fft.fftshift(f1)
            f2_shifted = torch.fft.fftshift(f2)

            # Create a low-pass filter for image1 and high-pass filter for image2
            h, w = hr_shape[-2:]
            center_h, center_w = h // 2, w // 2

            # Calculate the radius for the low-pass filter based on the scale factor
            if fourier_params_method == "ideal":
                radius = min(center_h, center_w) // scale_factor
                low_pass_mask = ideal_filter((h, w), radius)
            elif fourier_params_method == "butterworth":
                radius = min(center_h, center_w) // scale_factor
                low_pass_mask = butterworth_filter(
                    (h, w), radius, order=fourier_params_order
                )
            elif fourier_params_method == "gaussian":
                radius = min(center_h, center_w) // scale_factor
                low_pass_mask = gaussian_filter((h, w), radius)
            elif fourier_params_method == "sigmoid":
                radius = min(center_h, center_w) // scale_factor
                low_pass_mask = sigmoid_filter(
                    (h, w), radius, sharpness=fourier_params_sharpness
                )
            else:
                raise ValueError(f"Unsupported fourier_method: {fourier_params_method}")

            # High-pass filter is the complement of the low-pass filter
            high_pass_mask = 1 - low_pass_mask

            # Apply the masks to the shifted Fourier transforms
            f1_low = f1_shifted * low_pass_mask
            f2_high = f2_shifted * high_pass_mask

            # Combine the filtered components
            combined = f1_low + f2_high

            # Inverse shift and inverse Fourier transform to get the hybrid image
            combined_ishift = torch.fft.ifftshift(combined)
            hybrid_image = torch.real(torch.fft.ifft2(combined_ishift))
            torch_container[idx] = hybrid_image.float()
        hybrid_image = torch_container
    else:
        # Resize the high-resolution image (downsample)
        hr_data_down = resize(
            image=hr_data, shape=lr_shape, method=upsampling_method, antialias=True
        )

        # Resize the high-resolution image (upsample)
        hr_data_down_up = resize(
            image=hr_data_down, shape=hr_shape, method=upsampling_method, antialias=True
        )

        # Calculate the simple ratio
        hr_ratio = hr_data / hr_data_down_up

        # Calculate the hybrid image
        hybrid_image = lr_data_up * hr_ratio

    # Save the hybrid image
    hr_meta["count"] = hybrid_image.shape[0]
    hr_meta["dtype"] = lr_meta["dtype"]

    norm_result = (
        hq_histogram_matching(hybrid_image, lr_data) * lr_normalization
    ).numpy().astype(lr_meta["dtype"])
    norm_result = norm_result[[2, 1, 0]]

    with rio.open(output_file, "w", **hr_meta) as dst:
        dst.write(norm_result)

    return hybrid_image, error


def image_fusion2(
    lr_data: torch.Tensor,
    hr_data: torch.Tensor,
    interpolation_method: Optional[
        Literal["nearest", "bilinear", "bicubic", "tricubic", "lanczos3", "lanczos5"]
    ] = "lanczos3",
    kernel_method: Optional[
        Literal["triangle", "lanczos3", "lanczos5", "lanczos7", "cubic"]
    ] = "triangle",
    kernel_size: int = 7,
) -> pathlib.Path:
    """Create a hybrid image using a low-frequency from Sentinel-2 and
    high-frequency from a high-resolution image.

    Args:
        lr_data (np.ndarray): The low-resolution image.
        hr_data (np.ndarray): The high-resolution image.
        interpolation_method (Optional[str], optional): The interpolation
            method to use. Defaults to "lanczos3".
        fourier (Optional[bool], optional): Whether to use Fourier
            interpolation. Defaults to False.
        antialias (Optional[bool], optional): Whether to apply antialiasing.
            Defaults to True.

    Returns:
        np.ndarray: The hybrid image.
    """

    # Upsample the low-resolution image
    hr_shape = hr_data.shape
    lr_shape = lr_data.shape

    # Resize the low-resolution image
    lr_down = resize(
        image=lr_data, shape=hr_shape, method=interpolation_method, antialias=True
    ).float()

    # Apply histogram matching to the high-resolution image
    hr_data = hq_histogram_matching(hr_data, lr_down).float()

    # Estimate the error
    hr_data_down = resize(
        image=hr_data, shape=lr_shape, method=interpolation_method, antialias=True
    ).float()
    error = torch.abs(lr_data - hr_data_down).mean()

    # Apply the blur kernel
    hr_data_blur = apply_kernel_to_image(
        image=hr_data.float(), kernel_size=kernel_size, method=kernel_method
    )
    lr_data_blur = apply_kernel_to_image(
        image=lr_down.float(), kernel_size=kernel_size, method=kernel_method
    )
    high_freq = hr_data - hr_data_blur

    # Calculate the hybrid image
    fusion = lr_data_blur + high_freq

    return fusion, error
