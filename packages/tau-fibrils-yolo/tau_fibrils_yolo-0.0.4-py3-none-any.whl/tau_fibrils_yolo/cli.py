from tau_fibrils_yolo.predict import FibrilsDetector
from tau_fibrils_yolo.crossover_distance import crossover_distance_measurement
import tifffile
from pathlib import Path
import argparse
import glob
import pandas as pd


def process_input_file_predict(input_image_file, predictor, rescale_factor):
    image = tifffile.imread(input_image_file)

    boxes, probas = predictor.predict(image, rescale_factor)

    distances = []
    line_data = []
    centers_x = []
    centers_y = []
    lengths = []
    widths = []
    for box in boxes:
        distance, line_points, center, length, width = (
            crossover_distance_measurement(box, image)
        )
        distances.append(distance)
        line_data.append(line_points)
        centers_x.append(center[0])
        centers_y.append(center[1])
        lengths.append(length)
        widths.append(width)

    df = pd.DataFrame(
            {
                "detection_probability": probas,
                "crossover_distance": distances,
                "length": lengths,
                "width": widths,
                "center_x": centers_x,
                "center_y": centers_y,
            }
        )

    pt = Path(input_image_file)
    out_file_name = pt.parent / f"{pt.stem}_results.csv"

    df.to_csv(out_file_name)

    print("Saved results to ", out_file_name)


def cli_predict_image():
    """Command-line entry point for model inference."""
    parser = argparse.ArgumentParser(description="Use this command to run inference.")
    parser.add_argument(
        "-i",
        type=str,
        required=True,
        help="Input image. Must be a TIF image file.",
    )
    parser.add_argument(
        "-r",
        type=float,
        required=False,
        default=1.0,
        help="Rescale factor.",
    )
    args = parser.parse_args()

    input_image_file = args.i
    rescale_factor = args.r

    predictor = FibrilsDetector()

    process_input_file_predict(input_image_file, predictor, rescale_factor)


def cli_predict_folder():
    parser = argparse.ArgumentParser(
        description="Use this command to run inference in batch on a given folder."
    )
    parser.add_argument(
        "-i",
        type=str,
        required=True,
        help="Input folder. Must contain suitable TIF image files.",
    )
    parser.add_argument(
        "-r",
        type=float,
        required=False,
        default=1.0,
        help="Rescale factor.",
    )
    args = parser.parse_args()

    input_folder = args.i
    rescale_factor = args.r

    predictor = FibrilsDetector()

    for input_image_file in glob.glob(str(Path(input_folder) / "*.tif")):
        process_input_file_predict(input_image_file, predictor, rescale_factor)
