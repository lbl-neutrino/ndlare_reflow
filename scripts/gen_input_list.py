#!/usr/bin/env python3

import argparse
from collections import defaultdict
import json
import sqlite3


def get_crs2lrs(conn: sqlite3.Connection):
    crs2lrs = defaultdict[str, list[str]](list)

    q = f"SELECT c.nersc_path, l.nersc_path from All_global_subruns a" + \
        f" JOIN CRS_summary c ON (a.crs_run = c.run AND a.crs_subrun = c.subrun)" + \
        f" JOIN LRS_summary l ON (a.lrs_run = l.run AND a.lrs_subrun = l.subrun)" + \
        f" ORDER BY crs_run, crs_subrun, lrs_run, lrs_subrun"

    for crs_path, lrs_path in conn.execute(q):
        crs2lrs[crs_path].append(lrs_path)

    return crs2lrs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--db-file',
                    help='RunDB sqlite file',
                    required=True)
    ap.add_argument('-o', '--output',
                    help='Output json file',
                    required=True)
    args = ap.parse_args()

    result = []

    conn = sqlite3.connect(args.db_file)
    crs2lrs = get_crs2lrs(conn)

    for crs_path, lrs_paths in crs2lrs.items():
        spec = {
            'ARCUBE_CHARGE_FILE': crs_path,
            # hope there ain't no spaces in them paths
            'ARCUBE_LIGHT_FILES': ' '.join(lrs_paths)
        }
        result.append(spec)

    with open(args.output, 'w') as f:
        json.dump(result, f, indent=4)

    conn.close()


if __name__ == '__main__':
    main()
