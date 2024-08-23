import os
import numpy as np
from skimage.exposure import rescale_intensity
from skimage.transform import rescale
from ultralytics import YOLO
import pooch

from tau_fibrils_yolo.postprocess import (
    outside_image_border_filter,
    minimum_neighbor_distance_filter,
    overlapping_obb_filter,
)


MODEL_PATH = os.path.expanduser(os.path.join(os.getenv("XDG_DATA_HOME", "~"), ".yolo"))


def retreive_model():
    """Downloads the model weights from Zenodo."""
    print(
        " /!\ This model is on the Zenodo Sandbox (use it only for testing purposes) /!\ "
    )
    pooch.retrieve(
        url="https://sandbox.zenodo.org/records/99113/files/100ep.pt",
        known_hash="md5:2fc4be1e4feae93f75e335856be3083d",
        path=MODEL_PATH,
        progressbar=True,
        fname="yolo_fibrils_100ep.pt",
    )


def pad_image(image, tile_size_px, overlap_px):
    """Pads the image so that its length and width are divisible by the model's image size (which is assumed to be square)."""
    rx, ry = image.shape

    pad_x = rx % (tile_size_px - overlap_px) + overlap_px
    half_pad_x = pad_x // 2
    nx_ceil = np.ceil((rx + pad_x - overlap_px) / (tile_size_px - overlap_px)).astype(
        int
    )
    padded_image_size_x = nx_ceil * (tile_size_px - overlap_px) + overlap_px

    pad_y = ry % (tile_size_px - overlap_px) + overlap_px
    half_pad_y = pad_y // 2
    ny_ceil = np.ceil((ry + pad_y - overlap_px) / (tile_size_px - overlap_px)).astype(
        int
    )
    padded_image_size_y = ny_ceil * (tile_size_px - overlap_px) + overlap_px

    image_padded = np.zeros((padded_image_size_x, padded_image_size_y))

    image_padded[half_pad_x : (half_pad_x + rx), half_pad_y : (half_pad_y + ry)] = image

    return image_padded, (half_pad_x, half_pad_y), (nx_ceil, ny_ceil)


def image_tile_generator(image, imgsz, overlap_px):
    """Generates image tiles and their coordinates in the image domain."""
    image_p, (pad_x, pad_y), (nx, ny) = pad_image(image, imgsz, overlap_px)
    shift_x = imgsz - overlap_px
    shift_y = imgsz - overlap_px
    for ix in range(nx):
        for iy in range(ny):
            image_tile = image_p[
                (ix * shift_x) : (ix * shift_x + imgsz),
                (iy * shift_y) : (iy * shift_y + imgsz),
            ]
            coord_x = ix * shift_x - pad_x
            coord_y = iy * shift_y - pad_y

            yield image_tile, (coord_x, coord_y)


def to_rgb(arr):
    return np.repeat(arr[..., None], repeats=3, axis=-1)


def preprocess_image(image, rescale_factor):
    # Make sure the image is single-channel
    if len(image.shape) == 2:
        image = rescale_intensity(image, out_range=(0, 255)).astype(np.uint8)
    elif len(image.shape) == 3:
        image = image[..., 0]

    # Rescale the image to make it match the target resolution.
    image = rescale(image, rescale_factor, order=3, preserve_range=True)

    return image


def predict_generator(image, model, imgsz, rescale_factor=1.0, overlap_px=None):
    if overlap_px is None:
        # 10% overlap by default
        overlap_px = imgsz // 10

    image = preprocess_image(image, rescale_factor)

    for k, (image_tile, (coord_x, coord_y)) in enumerate(
        image_tile_generator(image, imgsz, overlap_px)
    ):
        image_input = to_rgb(image_tile)

        result = model.predict(
            source=image_input,
            conf=0.05,  # Confidence threshold for detections.
            iou=0.1,  # Intersection over union threshold.
            max_det=500,  # Max detections per 640 x 640 crop
            augment=False,
            imgsz=imgsz,  # Square resizing
        )[0]

        probabilities = result.obb.conf.cpu().numpy()
        boxes_coordinates = result.obb.xyxyxyxy.cpu().numpy()
        boxes_coordinates[..., 1] = (
            boxes_coordinates[..., 1] + coord_x
        ) / rescale_factor
        boxes_coordinates[..., 0] = (
            boxes_coordinates[..., 0] + coord_y
        ) / rescale_factor

        # Invert X-Y
        boxes_coordinates = boxes_coordinates[..., ::-1]

        yield k, boxes_coordinates, probabilities


class FibrilsDetector:
    def __init__(self):
        retreive_model()
        self.model = YOLO(os.path.join(MODEL_PATH, "yolo_fibrils_100ep.pt"))
        self.imgsz = 640
        self.overlap_px = self.imgsz // 10

    def n_crops(self, image: np.ndarray, rescale_factor: float):
        return np.prod(
            pad_image(
                preprocess_image(image, rescale_factor), self.imgsz, self.overlap_px
            )[-1]
        )

    def predict(self, image: np.ndarray, rescale_factor: float):
        boxes = []
        probas = []
        for _, b, p in predict_generator(image, self.model, self.imgsz, rescale_factor):
            boxes.extend(b)
            probas.extend(p)
        boxes = np.array(boxes)
        probas = np.array(probas)

        filt = outside_image_border_filter(boxes)
        boxes = boxes[filt]
        probas = probas[filt]

        filt = overlapping_obb_filter(boxes)
        boxes = boxes[filt]
        probas = probas[filt]

        filt = minimum_neighbor_distance_filter(boxes, rescale_factor)
        boxes = boxes[filt]
        probas = probas[filt]

        return boxes, probas

    def yield_predictions(self, image: np.ndarray, rescale_factor: float):
        for k, boxes, probas in predict_generator(
            image, self.model, self.imgsz, rescale_factor
        ):
            yield k, boxes, probas
