import numpy as np
from skimage.exposure import rescale_intensity
import cv2
from scipy.ndimage import zoom
from scipy.spatial import distance_matrix
from sklearn.neighbors import KernelDensity


def minimum_neighbor_distance_filter(boxes, rescale_factor, min_dist_px=150):
    """Returns a filter matching objects isolated by less than min_dist_px pixels."""
    min_dist_px = min_dist_px / rescale_factor
    box_centers = boxes_center_coordinates(boxes)
    dist_matrix = distance_matrix(box_centers, box_centers)
    np.fill_diagonal(dist_matrix, np.inf)
    min_distances = np.min(dist_matrix, axis=1)
    filt = min_distances <= min_dist_px
    return filt


def overlapping_obb_filter(bounding_boxes):
    """Returns the indeces of bounding boxes to keep after IOU filtering."""
    keep = []
    for i in range(len(bounding_boxes)):
        should_keep_i = True
        box_i = bounding_boxes[i]
        for j in keep:
            box_j = bounding_boxes[j]
            intersection_area, _ = cv2.intersectConvexConvex(box_i, box_j)
            if intersection_area > 0:
                should_keep_i = False
                break
        if should_keep_i:
            keep.append(i)
    return keep


def outside_image_border_filter(boxes):
    """Returns a filter matching boxes falling outside the image border."""
    return ~(boxes < 0).any(axis=2).any(axis=1)


def boxes_center_coordinates(boxes):
    """Returns the center coordinates of the boxes."""
    x_coords = boxes[..., 0]
    y_coords = boxes[..., 1]
    box_cy = (np.max(y_coords, axis=1) + np.min(y_coords, axis=1)) / 2
    box_cx = (np.max(x_coords, axis=1) + np.min(x_coords, axis=1)) / 2
    box_centers = np.vstack((box_cx, box_cy)).T

    return box_centers


def boxes_kernel_density_map(boxes, image, gaussian_sigma_px=50, downscale_factor=8):
    """Kernel density estimate from bounding box coordinates"""

    image_shape = np.array(image.shape) // downscale_factor

    x_grid, y_grid = np.meshgrid(
        np.linspace(0, image_shape[1] - 1, image_shape[1]),
        np.linspace(0, image_shape[0] - 1, image_shape[0]),
    )

    grid_points = np.vstack([y_grid.ravel(), x_grid.ravel()]).T

    kde = KernelDensity(
        bandwidth=gaussian_sigma_px, 
        kernel="gaussian", 
        algorithm="ball_tree"
    )

    kde.fit(boxes_center_coordinates(boxes) / downscale_factor)

    density_map = np.exp(kde.score_samples(grid_points)).reshape(image_shape)
    density_map = zoom(density_map, zoom=downscale_factor, order=1)
    density_map = rescale_intensity(density_map, out_range=(0, 1))

    return density_map
