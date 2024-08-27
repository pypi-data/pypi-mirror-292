from verification_digit_pty.adapters.ruc.natural import (
    av_adapter,
    e_adapter,
    n_adapter,
    nt_adapter,
    pe_adapter,
    pi_adapter,
)
from verification_digit_pty.handlers import _digitDV

OLD_RUC_CROSS_REFERENCE = {
    "00": "00",
    "10": "01",
    "11": "02",
    "12": "03",
    "13": "04",
    "14": "05",
    "15": "06",
    "16": "07",
    "17": "08",
    "18": "09",
    "19": "01",
    "20": "02",
    "21": "03",
    "22": "04",
    "23": "07",
    "24": "08",
    "25": "09",
    "26": "02",
    "27": "03",
    "28": "04",
    "29": "05",
    "30": "06",
    "31": "07",
    "32": "08",
    "33": "09",
    "34": "01",
    "35": "02",
    "36": "03",
    "37": "04",
    "38": "05",
    "39": "06",
    "40": "07",
    "41": "08",
    "42": "09",
    "43": "01",
    "44": "02",
    "45": "03",
    "46": "04",
    "47": "05",
    "48": "06",
    "49": "07",
}


def calculate_verification_digit(ruc):
    rs = ruc.split("-")
    if (len(rs) == 4 and rs[1] != "NT") or len(rs) < 3 or len(rs) > 5:
        return ""

    sw = False

    # TODO: NT
    if ruc[0] == "E":
        ructb = e_adapter(ruc)
    elif rs[1] == "NT":
        ructb = nt_adapter(ruc)
        # ructb = '0' * (4 - len(rs[1])) + '0000005' + '00' * (2 - len(rs[0][:-2])) + rs[0][:-2] + '43' + '0' * (
        #     3 - len(rs[2])) + rs[2] + '0' * (5 - len(rs[3])) + rs[3]

    elif rs[0][-2:] == "AV":
        ructb = av_adapter(ruc)
    elif rs[0][-2:] == "PI":
        ructb = pi_adapter(ruc)
    elif rs[0] == "PE":
        ructb = pe_adapter(ruc)
    elif ruc[0] == "N":
        ructb = n_adapter(ruc)
    elif 0 < len(rs[0]) <= 2:
        ructb = (
            "0" * (4 - len(rs[1]))
            + "0000005"
            + "0" * (2 - len(rs[0]))
            + rs[0]
            + "00"
            + "0" * (3 - len(rs[1]))
            + rs[1]
            + "0" * (5 - len(rs[2]))
            + rs[2]
        )

    else:  # RUC juridico
        ructb = "0" * (10 - len(rs[0])) + rs[0] + "0" * (4 - len(rs[1])) + rs[1] + "0" * (6 - len(rs[2])) + rs[2]
        # print ructb

        # sw es true si es ruc antiguo
        sw = ructb[3] == "0" and ructb[4] == "0" and ructb[5] < "5"

    # rutina de referencia cruzada
    if sw:
        ructb = ructb[:5] + OLD_RUC_CROSS_REFERENCE.get(ructb[5:7], ructb[5:7]) + ructb[7:]

    # print ructb

    dv1 = _digitDV(sw, ructb)
    # print dv1
    dv2 = _digitDV(sw, ructb + chr(48 + dv1))

    return chr(48 + dv1) + chr(48 + dv2)
    # print ret


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="DV calculator")
    parser.add_argument("ruc", type=str)
    args = parser.parse_args()

    dv = calculate_verification_digit(args.ruc)
    if len(dv) == 0:
        sys.exit(1)
