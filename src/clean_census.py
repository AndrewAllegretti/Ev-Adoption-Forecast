"""Stack yearly ACS 5-year county files and join them to the ZEV county-year table.

Output: data/processed/zev_census_county_year.csv
    county, year, bev, phev, fcev, zev_total, n_quarters, median_income, population
"""
import re
from pathlib import Path

import pandas as pd

from clean import OUT_ZEV, ROOT, normalize_county

RAW_DIR = ROOT / "data" / "raw"
OUT_JOINED = ROOT / "data" / "processed" / "zev_census_county_year.csv"

# ACS table id -> output column. Filenames look like ACSDT5Y2015.B19013-<timestamp>.csv
TABLES = {"B19013": "median_income", "B01003": "population"}
FILE_RE = re.compile(r"ACSDT5Y(?P<year>\d{4})\.(?P<table>B\d+)-")


def load_acs_file(path: Path) -> pd.DataFrame:
    """One wide ACS export (one row, a column per geography) -> long county rows."""
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    est = df.filter(like="!!Estimate").iloc[0]
    est.index = est.index.str.removesuffix("!!Estimate")
    est = est.drop("California")  # state total, not a county

    out = pd.DataFrame({"county": normalize_county(pd.Series(est.index)), "value": est.values})
    # Census uses commas and occasional annotations ("-", "250,000+"); those become NaN.
    out["value"] = pd.to_numeric(out["value"].str.replace(",", "", regex=False), errors="coerce")
    if n_bad := out["value"].isna().sum():
        print(f"{path.name}: {n_bad} non-numeric estimates set to NaN")
    return out


def load_census(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    frames = []
    for path in sorted(raw_dir.glob("ACSDT5Y*.csv")):
        m = FILE_RE.match(path.name)
        if not m or m["table"] not in TABLES:
            continue
        df = load_acs_file(path)
        df["year"] = int(m["year"])
        df["variable"] = TABLES[m["table"]]
        frames.append(df)

    long = pd.concat(frames, ignore_index=True)
    dupes = long.duplicated(["county", "year", "variable"])
    if dupes.any():
        raise ValueError(f"Duplicate ACS county-year-table rows:\n{long[dupes]}")

    # Income is nominal (each vintage is in its own year's dollars).
    wide = long.pivot(index=["county", "year"], columns="variable", values="value")
    wide = wide.reindex(columns=list(TABLES.values())).reset_index()
    wide.columns.name = None
    return wide.astype({"year": "int64", "population": "Int64"})


def join_zev(census: pd.DataFrame, zev_path: Path = OUT_ZEV) -> pd.DataFrame:
    zev = pd.read_csv(zev_path, dtype={"county": "string"})

    unmatched = set(census["county"]) - set(zev["county"])
    if unmatched:
        print(f"Census counties with no ZEV match: {sorted(unmatched)}")

    # Keep every ZEV row; ACS only covers 2015-2024, so other years get NaN.
    out = zev.merge(census, on=["county", "year"], how="left", validate="one_to_one")
    n_missing = out["population"].isna().sum()
    print(f"{n_missing} of {len(out)} ZEV county-years have no ACS data "
          f"(ACS years {census['year'].min()}-{census['year'].max()})")
    return out


def main() -> None:
    census = load_census()
    print(f"Stacked {len(census):,} ACS rows ({census['county'].nunique()} counties, "
          f"{census['year'].nunique()} years)")
    joined = join_zev(census)
    OUT_JOINED.parent.mkdir(parents=True, exist_ok=True)
    joined.to_csv(OUT_JOINED, index=False)
    print(f"Wrote {len(joined):,} rows -> {OUT_JOINED}")


if __name__ == "__main__":
    main()
