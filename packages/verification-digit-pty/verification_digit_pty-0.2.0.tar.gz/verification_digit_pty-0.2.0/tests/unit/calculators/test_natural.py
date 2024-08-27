import pytest

from verification_digit_pty.calculators.natural import calculate_verification_digit


class TestCalculateVerificationDigit:
    def testt_errors(self) -> None:
        assert calculate_verification_digit("") == ""
        assert calculate_verification_digit("E") == ""

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ("61302-14-123411", "22"),
            ("1102-85-117211", "95"),
            ("2486589-1-816994", "62"),
            ("1830234-1-710357", "82"),
            ("65219-68-360495", "20"),
            ("41369-85-283456", "73"),
            ("11947-1027-0229562", "71"),
            ("11947-1-0229562", "42"),
            ("64296-75-357434", "00"),
            ("203141-1-17214", "60"),
            ("1075137-1-553125", "18"),
        ],
    )
    def test_juridical(self, input_value, expected_output) -> None:
        assert calculate_verification_digit(input_value) == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ("8-442-445", "08"),
            ("PE-10-442", "50"),
            ("N-45-832", "58"),
            ("E-12-342", "10"),
            ("1AV-432-658", "31"),  # TODO Changed from 96 to 31 with the new implementation
            ("4PI-234-123", "31"),  # TODO Changed from 96 to 31 with the new implementation
        ],
    )
    def test_natural(self, input_value, expected_output) -> None:
        assert calculate_verification_digit(input_value) == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ["155720753-2-2022", "39"],
            ["2588017-1-831938", "20"],
            ["1489806-1-645353", "68"],
            ["1956569-1-732877", "00"],
            ["797609-1-493865", "12"],
            ["15565624-2-2017", "63"],
        ],
    )
    def test_juridical_old(self, input_value, expected_output) -> None:
        """Tests for `verification_digit_pty` package from Panama-RUC-DV-Calculator."""
        # TODO is not raising error.    ["0-0-0", "19"],  # Error
        assert calculate_verification_digit(input_value) == expected_output

    # @pytest.mark.skip(reason="Not supported yet")
    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ["0-NT-0-0", "31"],
            ["8-NT-1-13656", "43"],
            ["1-NT-45-56544", "03"],
            ["5-NT-478-2351", "94"],
            ["7-NT-102-33575", "03"],
            ["11-NT-958-2182101", "82"],
            ["8-NT-1-1234567", "49"],
            ["11-NT-958-218210", "73"],
            ["11-NT-958-2182104", "82"],
            ["8-NT-1-123456", "52"],
        ],
    )
    def test_juridical_nt(self, input_value, expected_output) -> None:
        """Tests for `verification_digit_pty` package from Panama-RUC-DV-Calculator."""
        # TODO this is not working.
        assert calculate_verification_digit(input_value) == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ["E-0-0", "75"],
            ["E-8-127702", "16"],
            ["E-8-127703", "05"],
            ["E-8-127702", "16"],
            ["E-8-12770", "72"],
            ["E-1234-12770", "98"],
            ["E-1235-12770", "23"],
            ["E-1-11", "63"],
            ["E-7824-53189", "90"],
            ["E-9624-41065", "80"],
            ["E-6521-53249", "99"],
            ["E-5056-27219", "16"],
            ["E-123-1277012", "65"],
            ["E-8-96407", "29"],
            ["E-1234-123456789", "26"],
        ],
    )
    def test_natural_e(self, input_value, expected_output) -> None:
        """Tests for `verification_digit_pty` package from Panama-RUC-DV-Calculator."""
        assert calculate_verification_digit(input_value) == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ["0AV-0-0", "10"],
            ["8AV-1-196", "90"],
            ["2AV-1234-12345", "26"],
            ["2AV-1234-123", "33"],
            ["2AV-123-123456", "28"],
            ["8AV-123-123456", "78"],
            ["2AV-1234-1234", "02"],
        ],
    )
    def test_natural_av(self, input_value, expected_output) -> None:
        """Tests for `verification_digit_pty` package from Panama-RUC-DV-Calculator."""
        assert calculate_verification_digit(input_value) == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ["0PI-0-0", "57"],
            ["13PI-1-196", "58"],
            ["8PI-1-80", "05"],
            ["8PI-23-65", "91"],
            ["2PI-23-65", "41"],
            ["2PI-123-1234", "41"],
            ["2PI-1234-12345", "26"],
            ["2PI-1234-123", "33"],
            ["2PI-123-123456", "65"],
            ["2PI-1234-1234", "02"],
            ["8PI-1234-1234", "02"],
            ["8PI-1234-12345", "26"],
        ],
    )
    def test_natural_pi(self, input_value, expected_output) -> None:
        """Tests for `verification_digit_pty` package from Panama-RUC-DV-Calculator."""
        assert calculate_verification_digit(input_value) == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ["N-0-0", "76"],
            ["N-19-1821", "11"],
            ["N-1-24", "89"],
            ["N-1234-12345", "00"],
            ["N-7824-53189", "73"],
            ["N-9624-41065", "63"],
            ["N-6521-53249", "72"],
        ],
    )
    def test_natural_n(self, input_value, expected_output) -> None:
        """Tests for `verification_digit_pty` package from Panama-RUC-DV-Calculator."""
        assert calculate_verification_digit(input_value) == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ["PE-0-0", "14"],
            ["PE-1-19", "60"],
            ["PE-123-12345", "42"],
            ["PE-842-3681", "51"],
            ["PE-712-5789", "82"],
            ["PE-523-8262", "37"],
        ],
    )
    def test_natural_pe(self, input_value, expected_output) -> None:
        """Tests for `verification_digit_pty` package from Panama-RUC-DV-Calculator."""
        assert calculate_verification_digit(input_value) == expected_output
