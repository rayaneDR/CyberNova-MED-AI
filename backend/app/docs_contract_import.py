"""Use the reviewed Pydantic contract models rather than redefining API schemas."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from docs.contracts.v1_design import (  # noqa: E402
    MeasurementInput, CheckInInput, RadiationInput, AcknowledgeInput,
)
__all__=["MeasurementInput","CheckInInput","RadiationInput","AcknowledgeInput"]
