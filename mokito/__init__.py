from .documents import Document, Documents
from .models import Model
# from .manage import ModelManager
from .fields import ChoiceField as Choice
from .geo_fileds import (
    GEOPoint,
    GEOLine,
    GEOPolygon,
    GEOMultiPoint,
    GEOMultiLine,
    GEOMultiPolygon
)
import mokito.errors as errors

__all__ = [
    "Document",
    "Documents",
    "Model",
    # "ModelManager",
    "errors",
    "Choice",
    "GEOPoint",
    "GEOLine",
    "GEOPolygon",
    "GEOMultiPoint",
    "GEOMultiLine",
    "GEOMultiPolygon"
]

version = "0.3.8"

# TODO: add indexes
# TODO: add forms
# TODO: add GraphQL
# TODO: add test .reload
