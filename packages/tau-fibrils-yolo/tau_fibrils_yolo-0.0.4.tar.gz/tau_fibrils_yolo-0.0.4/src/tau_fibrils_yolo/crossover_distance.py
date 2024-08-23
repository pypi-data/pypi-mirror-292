import numpy as np
from numpy.linalg import norm
from scipy.fft import fft
from scipy.fft import fftfreq
from skimage.measure import profile_line
from skimage.exposure import rescale_intensity


def crossover_distance_measurement(box, image):
    p0, p1, p2, p3 = box

    if norm(p2 - p0) < norm(p1 - p0):
        p0, p3, p2, p1 = box

    p5 = p0 + (p1 - p0) / 2
    p6 = p3 + (p2 - p3) / 2

    line_width = norm(p1 - p0)
    line_length = norm(p2 - p0)

    # Compute the intensity profile along the line, averaged over the width
    pixel_values = profile_line(
        image, src=p5, dst=p6, linewidth=int(line_width), order=1
    )

    # Normalize the pixel values
    pixel_values = rescale_intensity(pixel_values, out_range=(-1, 1))

    # Perform the Fourier transform
    fft_values = fft(pixel_values)

    # Calculate the frequencies
    freqs = fftfreq(len(pixel_values))[1:]  # Remove frequency = zero (?)

    # Identify the main frequency
    main_freq = freqs[np.argmax(np.abs(fft_values))]

    # Calculate the distance
    distance = (1 / main_freq) * (line_length / len(pixel_values))

    # Line for visualization
    diagonal = p6 - p5
    center = p5 + diagonal / 2
    diagonal_norm = diagonal / norm(diagonal)
    line_points = np.array(
        [center - distance / 2 * diagonal_norm, center + distance / 2 * diagonal_norm]
    )

    return distance, line_points, center, line_length, line_width
