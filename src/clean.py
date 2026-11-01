"""Clean CEC New ZEV Sales data into a county-year table.

Output: data/processed/zev_county_year.csv
    county, year, bev, phev, fcev, zev_total, n_quarters
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_ZEV = ROOT / "data" / "raw" / "New_ZEV_Sales_Last_updated_10-13-2026_ada.xlsx"
OUT_ZEV = ROOT / "data" / "processed" / "zev_county_year.csv"

FUEL_MAP = {"electric": "bev", "phev": "phev", "hydrogen": "fcev"}


def normalize_county(name: pd.Series) -> pd.Series:
    """Canonical county key shared by CEC and Census data.

    'Alameda County, California' / ' ALAMEDA county ' -> 'Alameda'
    """
    return (
        name.astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.replace(r",\s*California$", "", regex=True, case=False)
        .str.replace(r"\s+County$", "", regex=True, case=False)
        .str.title()
    )


def load_zev(path: Path = RAW_ZEV) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="County")
    df = df.rename(columns={
        "Data Year": "year",
        "Quarter": "quarter",
        "COUNTY": "county",
        "FUEL_TYPE": "fuel_type",
        "MAKE": "make",
        "MODEL": "model",
        "Number of Vehicles": "vehicles",
    })

    df["county"] = normalize_county(df["county"])
    df["fuel_type"] = df["fuel_type"].astype("string").str.strip().str.lower().map(FUEL_MAP)
    for col in ["year", "quarter", "vehicles"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Rows without a key or count can't be attributed anywhere.
    before = len(df)
    df = df.dropna(subset=["year", "quarter", "county", "fuel_type", "vehicles"])
    df = df[df["quarter"].between(1, 4) & (df["vehicles"] >= 0)]
    if dropped := before - len(df):
        print(f"Dropped {dropped} rows with missing/invalid values")

    # Out-of-state registrations have no Census counterpart.
    oos = df["county"] == "Out Of State"
    print(f"Dropped {int(df.loc[oos, 'vehicles'].sum()):,} out-of-state vehicles")
    return df[~oos]


def to_county_year(df: pd.DataFrame) -> pd.DataFrame:
    wide = df.pivot_table(
        index=["county", "year"], columns="fuel_type",
        values="vehicles", aggfunc="sum", fill_value=0,
    )

    # County-years with no sales are absent from the source; they are true zeros.
    counties = sorted(df["county"].unique())
    years = range(int(df["year"].min()), int(df["year"].max()) + 1)
    full = pd.MultiIndex.from_product([counties, years], names=["county", "year"])
    wide = wide.reindex(full, fill_value=0).reindex(columns=list(FUEL_MAP.values()), fill_value=0)
    wide["zev_total"] = wide.sum(axis=1)

    # 2008 starts in Q3 and the current year is partial; keep coverage explicit.
    n_q = df.groupby("year")["quarter"].nunique().rename("n_quarters")
    out = wide.reset_index().merge(n_q, on="year", how="left")
    return out.astype({c: "int64" for c in ["year", *FUEL_MAP.values(), "zev_total", "n_quarters"]})


def main() -> None:
    zev = to_county_year(load_zev())
    OUT_ZEV.parent.mkdir(parents=True, exist_ok=True)
    zev.to_csv(OUT_ZEV, index=False)
    print(f"Wrote {len(zev):,} rows ({zev['county'].nunique()} counties) -> {OUT_ZEV}")


if __name__ == "__main__":
    main()
