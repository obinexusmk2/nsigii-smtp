from __future__ import annotations

from enum import Enum


class TrilateralState(str, Enum):
    HERE_AND_NOW = "HERE_AND_NOW"
    THERE_AND_THEN = "THERE_AND_THEN"
    WHEN_AND_WHERE = "WHEN_AND_WHERE"


class TransportRole(str, Enum):
    ALPHA = "alpha"
    BETA = "beta"
    GAMMA = "gamma"


STATE_ROLE_MAP: dict[TrilateralState, TransportRole] = {
    TrilateralState.HERE_AND_NOW: TransportRole.ALPHA,
    TrilateralState.THERE_AND_THEN: TransportRole.BETA,
    TrilateralState.WHEN_AND_WHERE: TransportRole.GAMMA,
}


def map_state_to_role(state: TrilateralState) -> TransportRole:
    return STATE_ROLE_MAP[state]
