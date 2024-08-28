import torch


def lanczos_kernel(radius: int, x: torch.Tensor) -> torch.Tensor:
    # Calculate the y value
    y = radius * torch.sin(torch.pi * x) * torch.sin(torch.pi * x / radius)

    # Calculate the output where x > 1e-3
    out = torch.where(
        x > 1e-3, y / (torch.pi**2 * x**2), torch.tensor(1.0, device=x.device)
    )

    # Set output to 0 where x > radius
    out = torch.where(x > radius, torch.tensor(0.0, device=x.device), out)

    return out


def cubic_kernel(x: torch.Tensor) -> torch.Tensor:
    abs_x = torch.abs(x)

    # Coefficients for cubic kernel
    a = -0.5

    # First part: ((a + 2) * x - (a + 3)) * x * x + 1
    first_part = ((a + 2) * abs_x - (a + 3)) * abs_x * abs_x + 1

    # Second part: (a * x - 5 * a) * x * x + 8 * a * x - 4 * a
    second_part = (a * abs_x - 5 * a) * abs_x * abs_x + 8 * a * abs_x - 4 * a

    # Combine the parts
    result = torch.where(
        abs_x < 1,
        first_part,
        torch.where(abs_x < 2, second_part, torch.tensor(0.0, device=x.device)),
    )

    return result


def triangle_kernel(x):
    return torch.maximum(torch.tensor(0.0, device=x.device), 1 - torch.abs(x))


def ideal_filter(shape, cutoff):
    rows, cols = shape
    crow, ccol = rows // 2, cols // 2
    filter = torch.zeros((rows, cols), dtype=torch.float32)
    for u in range(rows):
        for v in range(cols):
            if (u - crow) ** 2 + (v - ccol) ** 2 <= cutoff**2:
                filter[u, v] = 1
    return filter


def butterworth_filter(shape, cutoff, order):
    rows, cols = shape
    crow, ccol = rows // 2, cols // 2
    filter = torch.zeros((rows, cols), dtype=torch.float32)
    for u in range(rows):
        for v in range(cols):
            distance = ((u - crow) ** 2 + (v - ccol) ** 2) ** 0.5
            filter[u, v] = 1 / (1 + (distance / cutoff) ** (2 * order))
    return filter


def gaussian_filter(shape, cutoff):
    rows, cols = shape
    crow, ccol = rows // 2, cols // 2
    filter = torch.zeros((rows, cols), dtype=torch.float32)
    for u in range(rows):
        for v in range(cols):
            distance = (u - crow) ** 2 + (v - ccol) ** 2
            filter[u, v] = torch.exp(-distance / (2 * (cutoff**2)))
    return filter


def sigmoid_filter(shape, cutoff, sharpness):
    rows, cols = shape
    crow, ccol = rows // 2, cols // 2
    filter = torch.zeros((rows, cols), dtype=torch.float32)
    for u in range(rows):
        for v in range(cols):
            distance = ((u - crow) ** 2 + (v - ccol) ** 2) ** 0.5
            filter[u, v] = 1 / (1 + torch.exp((distance - cutoff) / sharpness))
    return filter
