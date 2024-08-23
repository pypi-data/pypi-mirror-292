from tau_fibrils_yolo._widget import YoloDetectorWidget
from tau_fibrils_yolo.predict import FibrilsDetector

from ._version import version as __version__
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"