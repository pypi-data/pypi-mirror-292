import enum
from typing import Callable, List, Union

import numpy as np
import torch

from sathybrid.kernels import cubic_kernel, lanczos_kernel, triangle_kernel


def compute_weight_mat(
    input_size: int,
    output_size: int,
    scale: Union[float, torch.Tensor],
    translation: float,
    kernel: Callable[[torch.Tensor], torch.Tensor],
    antialias: bool,
) -> torch.Tensor:
    """
    Computes a weight matrix for resampling operations.

    Args:
        input_size (int): The size of the input dimension.
        output_size (int): The size of the output dimension.
        scale (Union[float, torch.Tensor]): The scaling factor. If tensor, it should be of the same dtype as the desired output.
        translation (float): The translation factor.
        kernel (Callable[[torch.Tensor], torch.Tensor]): The kernel function to compute weights.
        antialias (bool): Whether to apply antialiasing.

    Returns:
        torch.Tensor: The computed weight matrix.
    """

    # Determine the dtype based on the scale type
    dtype = torch.float32 if isinstance(scale, float) else scale.dtype

    # Compute the inverse scale
    inv_scale = torch.tensor(1.0) / scale

    # Adjust the kernel scale for antialiasing
    kernel_scale = (
        torch.max(inv_scale, torch.tensor(1.0, dtype=dtype)) if antialias else 1.0
    )

    # Compute the sample positions in the input space
    sample_f = (
        (torch.arange(output_size, dtype=dtype) + 0.5) * inv_scale
        - translation * inv_scale
        - 0.5
    )

    # Compute the absolute distances for the kernel
    x = (
        torch.abs(
            sample_f.unsqueeze(0) - torch.arange(input_size, dtype=dtype).unsqueeze(1)
        )
        / kernel_scale
    )

    # Apply the kernel to the distances to get the weights
    weights = kernel(x)

    # Normalize the weights to sum to 1
    total_weight_sum = torch.sum(weights, dim=0, keepdim=True)
    weights = torch.where(
        torch.abs(total_weight_sum) > 1000.0 * np.finfo(np.float32).eps,
        weights / total_weight_sum,
        torch.zeros_like(weights),
    )

    # Define the valid range for sample positions
    input_size_minus_0_5 = input_size - 0.5

    # Mask weights that correspond to out-of-bound positions
    return torch.where(
        (sample_f >= -0.5) & (sample_f <= input_size_minus_0_5).unsqueeze(0),
        weights,
        torch.zeros_like(weights),
    )


def _scale_and_translate(
    x: torch.Tensor,
    output_shape: List[int],
    spatial_dims: List[int],
    scale: List[float],
    translation: List[float],
    kernel: Callable[[torch.Tensor], torch.Tensor],
    antialias: bool,
) -> torch.Tensor:
    """
    Scales and translates an input tensor `x` to a specified `output_shape`
    along given `spatial_dims`.

    Args:
        x (torch.Tensor): The input tensor.
        output_shape (List[int]): The desired output shape.
        spatial_dims (List[int]): The dimensions along which to apply scaling
            and translation.
        scale (List[float]): Scaling factors for each spatial dimension.
        translation (List[float]): Translation factors for each spatial dimension.
        kernel (Callable[[torch.Tensor], torch.Tensor]): The kernel function to
            compute weights.
        antialias (bool): Whether to apply antialiasing.

    Returns:
        torch.Tensor: The scaled and translated tensor.
    """

    input_shape = x.shape

    # If there are no spatial dimensions, return the input tensor as is
    if len(spatial_dims) == 0:
        return x

    contractions = []

    # Compute the weight matrices for each spatial dimension
    for i, d in enumerate(spatial_dims):
        m = input_shape[d]
        n = output_shape[d]
        w = compute_weight_mat(
            input_size=m,
            output_size=n,
            scale=scale[i],
            translation=translation[i],
            kernel=kernel,
            antialias=antialias,
        ).type_as(x)
        contractions.append(w)

    # Contract along the first spatial dimension
    new_x = torch.tensordot(x, contractions[0], dims=([spatial_dims[0]], [0]))

    # Permute dimensions to bring the newly added dimension to the correct position
    permute_order = list(range(new_x.dim()))
    permute_order[spatial_dims[0]] = permute_order[-1]
    permute_order[-1] = spatial_dims[0]
    new_x = new_x.permute(permute_order)

    # Contract along the second spatial dimension if it exists
    if len(spatial_dims) > 1:
        new_x = torch.tensordot(new_x, contractions[1], dims=([spatial_dims[1]], [0]))

        # Permute dimensions to bring the newly added dimension to the correct position
        permute_order = list(range(new_x.dim()))
        permute_order[spatial_dims[1]] = permute_order[-1]
        permute_order[-1] = spatial_dims[1]
        new_x = new_x.permute(permute_order)

    return new_x


class ResizeMethod(enum.Enum):
    NEAREST = 0
    LINEAR = 1
    LANCZOS3 = 2
    LANCZOS5 = 3
    LANCZOS7 = 4
    CUBIC = 5

    @staticmethod
    def from_string(s: str):
        if s == "nearest":
            return ResizeMethod.NEAREST
        if s in ["linear", "bilinear", "trilinear", "triangle"]:
            return ResizeMethod.LINEAR
        elif s == "lanczos3":
            return ResizeMethod.LANCZOS3
        elif s == "lanczos5":
            return ResizeMethod.LANCZOS5
        elif s == "lanczos7":
            return ResizeMethod.LANCZOS7
        elif s in ["cubic", "bicubic", "tricubic"]:
            return ResizeMethod.CUBIC
        else:
            raise ValueError(f'Unknown resize method "{s}"')


_kernels = {
    ResizeMethod.LINEAR: triangle_kernel,
    ResizeMethod.LANCZOS3: lambda x: lanczos_kernel(3.0, x),
    ResizeMethod.LANCZOS5: lambda x: lanczos_kernel(5.0, x),
    ResizeMethod.LANCZOS7: lambda x: lanczos_kernel(7.0, x),
    ResizeMethod.CUBIC: cubic_kernel,
}


def scale_and_translate(
    image: torch.Tensor,
    shape: List[int],
    spatial_dims: List[int],
    scale: List[float],
    translation: List[float],
    method: Union[str, ResizeMethod],
    antialias: bool = True,
) -> torch.Tensor:
    """
    Scales and translates an image to a specified shape using a given method.

    Args:
        image (torch.Tensor): The input image tensor.
        shape (List[int]): The desired output shape.
        spatial_dims (List[int]): The dimensions along which to apply scaling and translation.
        scale (List[float]): Scaling factors for each spatial dimension.
        translation (List[float]): Translation factors for each spatial dimension.
        method (Union[str, ResizeMethod]): The method to use for resampling.
        antialias (bool, optional): Whether to apply antialiasing. Defaults to True.

    Returns:
        torch.Tensor: The scaled and translated image.
    """

    if len(shape) != image.ndim:
        raise ValueError(
            f"shape must have length equal to the number of dimensions of x; {shape} vs {image.shape}"
        )

    if isinstance(method, str):
        method = ResizeMethod.from_string(method)

    if method == ResizeMethod.NEAREST:
        raise ValueError(
            "Nearest neighbor resampling is not currently supported for scale_and_translate."
        )

    kernel = _kernels[method]
    return _scale_and_translate(
        image, shape, spatial_dims, scale, translation, kernel, antialias
    )


def _resize_nearest(x: torch.Tensor, output_shape: List[int]) -> torch.Tensor:
    """
    Resizes an image using nearest neighbor interpolation.

    Args:
        x (torch.Tensor): The input image tensor.
        output_shape (List[int]): The desired output shape.

    Returns:
        torch.Tensor: The resized image.
    """

    input_shape = x.shape
    spatial_dims = tuple(
        i for i in range(len(input_shape)) if input_shape[i] != output_shape[i]
    )

    for d in spatial_dims:
        m = input_shape[d]
        n = output_shape[d]
        offsets = (torch.arange(n, dtype=torch.float32) + 0.5) * m / n
        offsets = torch.floor(offsets).long()
        indices = [slice(None)] * len(input_shape)
        indices[d] = offsets
        x = x[tuple(indices)]

    return x


def resize(
    image: torch.Tensor,
    shape: List[int],
    method: Union[str, ResizeMethod],
    antialias: bool = True,
) -> torch.Tensor:
    """
    Resizes an image to a specified shape using a given method.

    Args:
        image (torch.Tensor): The input image tensor.
        shape (List[int]): The desired output shape.
        method (Union[str, ResizeMethod]): The method to use for resampling.
        antialias (bool, optional): Whether to apply antialiasing. Defaults to True.

    Returns:
        torch.Tensor: The resized image.
    """

    if len(shape) != image.ndim:
        raise ValueError(
            f"shape must have length equal to the number of dimensions of x; {shape} vs {image.shape}"
        )

    if isinstance(method, str):
        method = ResizeMethod.from_string(method)

    if method == ResizeMethod.NEAREST:
        return _resize_nearest(image, shape)

    kernel = _kernels[method]
    spatial_dims = tuple(i for i in range(len(shape)) if image.shape[i] != shape[i])
    scale = [1.0 if shape[d] == 0 else shape[d] / image.shape[d] for d in spatial_dims]

    return _scale_and_translate(
        x=image,
        output_shape=shape,
        spatial_dims=spatial_dims,
        scale=scale,
        translation=[0.0] * len(spatial_dims),
        kernel=kernel,
        antialias=antialias,
    )
