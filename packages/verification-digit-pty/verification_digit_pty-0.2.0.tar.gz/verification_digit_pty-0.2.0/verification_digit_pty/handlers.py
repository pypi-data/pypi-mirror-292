def calculate_vd(old_ruc: bool, ructb: str) -> str:
    j = 2
    nsuma = 0

    for c in reversed(ructb):
        if old_ruc and j == 12:
            old_ruc = False
            j -= 1

        nsuma += j * (ord(c) - ord("0"))
        j += 1
    r = nsuma % 11
    return str(11 - r) if r > 1 else str(0)


def _digitDV(sw, ructb):
    # rutina calcula dv
    j = 2
    nsuma = 0

    for c in reversed(ructb):
        if sw and j == 12:
            sw = False
            j -= 1

        nsuma += j * (ord(c) - ord("0"))
        j += 1
    r = nsuma % 11
    if r > 1:
        return 11 - r
    return 0
