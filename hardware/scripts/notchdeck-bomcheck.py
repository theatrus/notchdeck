#!/usr/bin/env python3
"""Validate KiCad's assembly BOM against the reviewed JLCPCB selection snapshot.

This audits exported component identity and coverage, not current stock or
electrical suitability. Run via make verify-bom-notchdeck-one after changes.
"""

import argparse
import csv
import json
from pathlib import Path
import re


def main():
    project = Path(__file__).resolve().parents[1] / "notchdeck-one"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bom", type=Path, default=project / "jlcpcb_bom.csv")
    args = parser.parse_args()
    source = json.loads((project / "bom/jlcpcb-parts.json").read_text())
    expected = {}
    for code, part in source["parts"].items():
        assert re.fullmatch(r"C\d+", code), f"Invalid part number: {code}"
        for ref in part["references"]:
            assert ref not in expected, f"Duplicate selection: {ref}"
            expected[ref] = code
    assert not set(expected) & set(
        source["non_assembly"]
    ), "Assembly and exclusion overlap"
    actual = {}
    with args.bom.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        code = row["LCSC Part #"]
        assert code in source["parts"], f"Missing or unreviewed JLCPCB code: {code!r}"
        part = source["parts"][code]
        for column, key in [
            ("MPN", "mpn"),
            ("Manufacturer", "manufacturer"),
            ("Footprint", "footprint"),
            ("Notes", "bom_comments"),
        ]:
            assert row[column] == part[key], f"{column} mismatch: {row['Designator']}"
        refs = [ref.strip() for ref in row["Designator"].split(",")]
        assert int(row["Qty"]) == len(refs), f"Quantity mismatch: {refs}"
        for ref in refs:
            assert re.fullmatch(
                r"[A-Z]+\d+", ref
            ), f"Invalid or compressed reference: {ref}"
            assert ref not in actual, f"Duplicate BOM reference: {ref}"
            assert (
                expected.get(ref) == code
            ), f"Incorrect part assignment: {ref}: {code}"
            actual[ref] = code
    assert (
        actual == expected
    ), f"BOM coverage mismatch; missing {set(expected) - set(actual)}"
    print(
        f"PASS: {len(actual)} components, {len(set(actual.values()))} JLCPCB part numbers, "
        f"{len(rows)} export rows; identity, footprint, notes, quantities and exclusions match"
    )
    print(
        f"Catalog snapshot: {source['checked_at_utc']}; stock is not revalidated by this check"
    )


if __name__ == "__main__":
    main()
