import pytest

from verification_digit_pty.handlers import _digitDV, calculate_vd


@pytest.mark.parametrize(
    "is_old, input_value, expected_output",
    [
        (False, "00000005004300000000", "0"),
        (False, "000000050043000000000", "9"),
        (False, "00000005084300100024", "3"),
        (False, "000000050843001000243", "3"),
        (False, "00000005034346545624", "0"),
        (False, "000000050343465456240", "3"),
        (False, "00000050943002421578", "5"),
        (False, "000000509430024215785", "0"),
        (False, "00000050643227888555", "0"),
        (False, "000000506432278885550", "9"),
        (False, "00000005124304502154", "1"),
        (False, "000000051243045021541", "7"),
    ],
)
def test_calculate_vd_nt(is_old, input_value, expected_output) -> None:
    assert calculate_vd(is_old, input_value) == expected_output


@pytest.mark.parametrize(
    "is_old, input_value, expected_output",
    [
        (False, "00000005004300000000", 0),
        (False, "000000050043000000000", 9),
        (False, "00000005084300100024", 3),
        (False, "000000050843001000243", 3),
        (False, "00000005034346545624", 0),
        (False, "000000050343465456240", 3),
        (False, "00000050943002421578", 5),
        (False, "000000509430024215785", 0),
        (False, "00000050643227888555", 0),
        (False, "000000506432278885550", 9),
        (False, "00000005124304502154", 1),
        (False, "000000051243045021541", 7),
    ],
)
def test__digitDV_nt(is_old, input_value, expected_output) -> None:
    assert _digitDV(is_old, input_value) == expected_output
