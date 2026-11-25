import re
import math
from datetime import datetime


def check_dt(s):
    if not isinstance(s, str):
        return None
    if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", s):
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def load_airports(path: str) -> set[str]:
    codes = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            codes.add(line)
    return codes


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT" 

    clean = [x.strip() for x in fields]
    f_id, orig, dest, dep, arr, price_s = clean

    for item in clean:
        if item == "":
            return "MISSING_FIELD"

    if not re.match(r"^[A-Za-z0-9]{2,8}$", f_id):
        return "INVALID_FLIGHT_ID"

    if not re.match(r"^[A-Z]{3}$", orig) or orig not in airports:
        return "INVALID_ORIGIN"

    if not re.match(r"^[A-Z]{3}$", dest) or dest not in airports:
        return "INVALID_DESTINATION"

    if orig == dest:
        return "SAME_ORIGIN_DESTINATION"

    dep_dt = check_dt(dep)
    if dep_dt is None:
        return "INVALID_DEPARTURE"

    arr_dt = check_dt(arr)
    if arr_dt is None:
        return "INVALID_ARRIVAL"

    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        p = float(price_s)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(p):
        return "INVALID_PRICE"

    if p <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    clean = [x.strip() for x in fields]
    return {
        "flight_id": clean[0],
        "origin": clean[1],
        "destination": clean[2],
        "departure_datetime": clean[3],
        "arrival_datetime": clean[4],
        "price": float(clean[5]),
    }