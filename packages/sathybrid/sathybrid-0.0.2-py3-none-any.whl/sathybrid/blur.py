import torch

from sathybrid.kernels import cubic_kernel, lanczos_kernel, triangle_kernel


def generate_2d_kernel(size, device, method="triangle"):
    x = torch.linspace(-1, 1, size, device=device)
    if method == "triangle":
        kernel_1d = triangle_kernel(x)
    elif method == "lanczos3":
        kernel_1d = lanczos_kernel(3.0, x)
    elif method == "lanczos5":
        kernel_1d = lanczos_kernel(5.0, x)
    elif method == "lanczos7":
        kernel_1d = lanczos_kernel(7.0, x)
    elif method == "cubic":
        kernel_1d = cubic_kernel(x)
    kernel_2d = torch.ger(kernel_1d, kernel_1d)
    kernel_2d = kernel_2d / kernel_2d.sum()  # Normalizar el kernel
    return kernel_2d


# Aplicar el kernel a la imagen
def apply_kernel_to_image(image, kernel_size, method="triangle"):
    device = image.device
    kernel_2d = (
        generate_2d_kernel(kernel_size, device, method=method).unsqueeze(0).unsqueeze(0)
    )
    smoothed_image = torch.zeros_like(image)

    for i in range(image.shape[0]):
        smoothed_image[i] = torch.nn.functional.conv2d(
            image[i].unsqueeze(0), kernel_2d, padding=kernel_size // 2
        ).squeeze(0)

    return smoothed_image
