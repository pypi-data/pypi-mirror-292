import sys
from ultralytics import YOLO

PRETRAINED_MODEL_FILE = '/home/wittwer/code/tau-fibrils-yolo/pretrained_models/yolov8n-obb.pt'

if __name__=='__main__':
    _, metadata_file = sys.argv
    model = YOLO(
        model=PRETRAINED_MODEL_FILE,
        task='obb'
    )

    model.train(
        data=metadata_file, 
        epochs=100, 
        imgsz=640,
        device=0,  # Single GPU.
        project='/home/wittwer/code/tau-fibrils-yolo',
        name='yolo_output',
        exist_ok=True,  # Overwrite the previous output
        pretrained=True,
        val=True,
        plots=False,
        # Augmentations
        flipud=0.5,  # Flip the image with the specified probability
        fliplr=0.5,
        scale=0.5,  # Meaningful?
        degrees=180,  # Rotation
    )
