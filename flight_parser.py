import argparse
import json
import logging
import os
import sys
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries

STUDENT_ID = "251ADB239"
FIRST_NAME = "YUSUFDOGUKAN"
LAST_NAME = "DOGAN"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("-i", dest="csv_file")
    src.add_argument("-d", dest="csv_dir")
    src.add_argument("-j", dest="json_file")

    parser.add_argument("-a", dest="airports")
    parser.add_argument("-o", dest="out_db")
    parser.add_argument("-q", dest="queries")
    parser.add_argument("-r", dest="resp_dir", default=".")

    try:
        args = parser.parse_args(argv)
        if (args.csv_file or args.csv_dir) and not args.airports:
            parser.error("-a is required with -i or -d")
        if args.json_file and args.out_db is not None:
            parser.error("-o cannot be used with -j")
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1

    db = []

    if args.csv_file or args.csv_dir:
        try:
            airport_set = load_airports(args.airports)
        except OSError as e:
            print(f"Error: could not read airports file: {e}", file=sys.stderr)
            return 1

        if args.csv_file:
            if not os.path.isfile(args.csv_file):
                print(f"Error: file not found: {args.csv_file}", file=sys.stderr)
                return 1
            files = [args.csv_file]
        else:
            if not os.path.isdir(args.csv_dir):
                print(f"Error: folder not found: {args.csv_dir}", file=sys.stderr)
                return 1
            try:
                csvs = sorted(
                    f for f in os.listdir(args.csv_dir)
                    if f.endswith(".csv") and os.path.isfile(os.path.join(args.csv_dir, f))
                )
            except OSError as e:
                print(f"Error: could not list folder: {e}", file=sys.stderr)
                return 1
            if not csvs:
                print(f"Error: no csv files in {args.csv_dir}", file=sys.stderr)
                return 1
            files = [os.path.join(args.csv_dir, f) for f in csvs]

        out_path = args.out_db if args.out_db is not None else "db.json"
        log_folder = os.path.dirname(out_path) or "."
        log_path = os.path.join(log_folder, "errors.log")

        logger = logging.getLogger("flight_parser")
        logger.setLevel(logging.INFO)
        fh = None

        try:
            fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            fh.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
            logger.addHandler(fh)

            db, errs = parse_files(files, airport_set)
            for msg in errs:
                logger.warning(msg)

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
        except OSError as e:
            print(f"Error: file error: {e}", file=sys.stderr)
            return 1
        finally: 
            if fh is not None:
                logger.removeHandler(fh)
                fh.close()
    else:
        try:
            with open(args.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error: invalid json database: {e}", file=sys.stderr)
            return 1

        if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
            print("Error: json database must be a list of objects", file=sys.stderr)
            return 1
        db = data

    if args.queries:
        try:
            with open(args.queries, "r", encoding="utf-8") as f:
                q_data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error: invalid query file: {e}", file=sys.stderr)
            return 1

        is_single = isinstance(q_data, dict)
        is_list = isinstance(q_data, list) and all(isinstance(x, dict) for x in q_data)
        if not (is_single or is_list):
            print("Error: wrong query file format", file=sys.stderr)
            return 1

        ans = run_queries(db, q_data)
        now_str = datetime.now().strftime("%Y%m%d_%H%M")
        resp_file = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{now_str}.json"
        resp_path = os.path.join(args.resp_dir, resp_file)

        try:
            with open(resp_path, "w", encoding="utf-8") as f:
                json.dump(ans, f, indent=2)
        except OSError as e:
            print(f"Error: could not write response file: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())