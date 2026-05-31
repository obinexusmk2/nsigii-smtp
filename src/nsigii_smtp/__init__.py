"""Public package exports for nsigii-smtp."""

from .artifacts import Artifact, ArtifactEncoder
from .dispatch import DispatchResult, DispatchStatus
from .message import HumanNeedPayload, NSIGIIMessage
from .schedule import ScheduleSpec
from .trilateral import TransportRole, TrilateralState, map_state_to_role
from .transport import SMTPSettings, SMTPTransport

__all__ = [
    "Artifact",
    "ArtifactEncoder",
    "DispatchResult",
    "DispatchStatus",
    "HumanNeedPayload",
    "NSIGIIMessage",
    "ScheduleSpec",
    "SMTPSettings",
    "SMTPTransport",
    "TransportRole",
    "TrilateralState",
    "map_state_to_role",
]
