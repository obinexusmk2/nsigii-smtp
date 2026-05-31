from nsigii_smtp import TransportRole, TrilateralState, map_state_to_role


def test_state_to_role_mapping():
    assert map_state_to_role(TrilateralState.HERE_AND_NOW) is TransportRole.ALPHA
    assert map_state_to_role(TrilateralState.THERE_AND_THEN) is TransportRole.BETA
    assert map_state_to_role(TrilateralState.WHEN_AND_WHERE) is TransportRole.GAMMA
