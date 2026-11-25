import math
import re
from datetime import datetime

REC_KEYS = {"flight_id", "origin", "destination", "departure_datetime", "arrival_datetime", "price"}
VALID_KEYS = REC_KEYS | {"min_price", "sort_by", "order", "limit"}


def is_dt_ok(val):
    if not isinstance(val, str):
        return False
    if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", val):
        return False
    try:
        datetime.strptime(val, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def is_num(val):
    if isinstance(val, bool):
        return False
    return isinstance(val, (int, float)) and math.isfinite(val)


def check_query(q):
    if not isinstance(q, dict):
        return False 

    for k in q:
        if k not in VALID_KEYS:
            return False

    for k in ("flight_id", "origin", "destination"):
        if k in q and not isinstance(q[k], str):
            return False

    for k in ("departure_datetime", "arrival_datetime"):
        if k in q and not is_dt_ok(q[k]):
            return False

    for k in ("price", "min_price"):
        if k in q and not is_num(q[k]):
            return False

    if "sort_by" in q:
        if not isinstance(q["sort_by"], str) or q["sort_by"] not in REC_KEYS:
            return False

    if "order" in q:
        if "sort_by" not in q or q["order"] not in ("asc", "desc"):
            return False

    if "limit" in q:
        lim = q["limit"]
        if isinstance(lim, bool) or not isinstance(lim, int) or lim < 0:
            return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    if not check_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    res = []
    for row in db:
        if "flight_id" in query and row["flight_id"] != query["flight_id"]:
            continue
        if "origin" in query and row["origin"] != query["origin"]:
            continue
        if "destination" in query and row["destination"] != query["destination"]:
            continue
        if "departure_datetime" in query and row["departure_datetime"] < query["departure_datetime"]:
            continue
        if "arrival_datetime" in query and row["arrival_datetime"] > query["arrival_datetime"]:
            continue
        if "price" in query and row["price"] > query["price"]:
            continue
        if "min_price" in query and row["price"] < query["min_price"]:
            continue
        res.append(row)

    if "sort_by" in query:
        key = query["sort_by"]
        is_desc = query.get("order", "asc") == "desc"
        res = sorted(res, key=lambda item: item[key], reverse=is_desc)

    if "limit" in query:
        res = res[:query["limit"]]

    return {"query": query, "matches": res}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        return [run_query(db, queries)]
    out = []
    for q in queries:
        out.append(run_query(db, q))
    return out