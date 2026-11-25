import csv
import os
from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    valid_rows = []
    err_list = []
    seen = set()

    for p in paths:
        fname = os.path.basename(p)
        with open(p, "r", encoding="utf-8") as f:
            for idx, raw in enumerate(f, 1):
                line = raw.rstrip("\r\n")

                if idx == 1:
                    continue
                if line.strip() == "" or line.strip().startswith("#"):
                    continue

                cols = next(csv.reader([line]))
                err = validate_row(cols, airports)
                if err is not None:
                    err_list.append(f"{fname}:{idx}: {err} | {line}")
                    continue

                rec = to_record(cols)
                dup_key = (rec["flight_id"], rec["departure_datetime"])
                if dup_key in seen:
                    err_list.append(f"{fname}:{idx}: DUPLICATE_FLIGHT | {line}")
                    continue

                seen.add(dup_key)
                valid_rows.append(rec)

    return valid_rows, err_list