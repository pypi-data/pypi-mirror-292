import pytest

from verification_digit_pty.adapters.ruc.natural import e_adapter, nt_adapter


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ["E-0-0", "00000005005000000000"],
        ["E-8-127702", "00000050050008127702"],
        ["E-8-127703", "00000050050008127703"],
        ["E-8-127702", "00000050050008127702"],
        ["E-8-12770", "00000005005000812770"],
        ["E-1234-12770", "00000005665123412770"],
        ["E-1235-12770", "00000005665123512770"],
        ["E-1-11", "00000005005000100011"],
        ["E-7824-53189", "00000005665782453189"],
        ["E-9624-41065", "00000005665962441065"],
        ["E-6521-53249", "00000005665652153249"],
        ["E-5056-27219", "00000005665505627219"],
        ["E-123-1277012", "00000005005012312770"],
        ["E-8-96407", "00000005005000896407"],
        ["E-1234-123456789", "00000005665123412345"],
    ],
)
def test_natural_e_adapter(input_value, expected_output) -> None:
    """Error in calculating the rud format e_adapter returns 21 digits instead of 20."""
    new_value = e_adapter(input_value)
    assert new_value == expected_output


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("0-NT-0-0", "00000005004300000000"),
        ("8-NT-1-24", "00000005084300100024"),
        ("3-NT-465-45624", "00000005034346545624"),
        ("9-NT-2-421578", "00000050943002421578"),
        ("6-NT-227-888555", "00000050643227888555"),
        ("12-NT-45-2154", "00000005124304502154"),
    ],
)
def test_nt_adapter(input_value, expected_output) -> None:
    new_value = nt_adapter(input_value)
    assert new_value == expected_output
