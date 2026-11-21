import re

REGEXP = re.compile(
    r"\[\s*\d+\]\s+"
    r"(?P<interval>\d+\.\d+-\d+\.\d+)\s+sec\s+"
    r"(?P<transfer>[\d.]+)\s+(?P<t_unit>[KMG]?Bytes)\s+"
    r"(?P<bitrate>[\d.]+)\s+(?P<b_unit>[KMG]?bits/sec)"
    r"(?:\s+(?P<retr>\d+)\s+(?P<cwnd>[\d.]+)\s+(?P<c_unit>[KMG]?Bytes))?"
)


def _to_mbytes(val: float, unit: str) -> float:
    u = unit.lower()
    if u == "gbytes":
        return val * 1024.0
    if u == "kbytes":
        return val / 1024.0
    if u == "bytes":
        return val / (1024.0 * 1024.0)
    return val


def _to_mbits(val: float, unit: str) -> float:
    u = unit.lower()
    if u == "gbits/sec":
        return val * 1000.0
    if u == "kbits/sec":
        return val / 1000.0
    if u == "bits/sec":
        return val / 1_000_000.0
    return val


def parser(raw_output):
    result_list = []
    if not raw_output:
        return result_list

    for line in raw_output.splitlines():
        if "sender" in line or "receiver" in line:
            continue
        match = REGEXP.search(line)
        if not match:
            continue

        transfer = _to_mbytes(float(match.group("transfer")), match.group("t_unit"))
        bitrate = _to_mbits(float(match.group("bitrate")), match.group("b_unit"))
        retr = float(match.group("retr")) if match.group("retr") else 0.0
        cwnd = (
            _to_mbytes(float(match.group("cwnd")), match.group("c_unit")) * 1024.0
            if match.group("cwnd")
            else 0.0
        )

        result_list.append(
            {
                "Interval": match.group("interval"),
                "Transfer": round(transfer, 2),
                "Bitrate": round(bitrate, 2),
                "Retr": retr,
                "Cwnd": round(cwnd, 2),
            }
        )

    return result_list