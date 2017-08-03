from .documents import Document, Documents
from .models import Model
# from .manage import ModelManager
from .fields import ChoiceField as Choice
import mokito.errors as errors

__all__ = [
    "Document",
    "Documents",
    "Model",
    # "ModelManager",
    "errors",
    "Choice",
]

version = "0.3.2"

# TODO: add indexes
# TODO: add forms
