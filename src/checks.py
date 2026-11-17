"""Sanity checks on the joined ZEV + Census county-year table."""
import pandas as pd

from clean_census import OUT_JOINED

N_COUNTIES = 58
# ACS 5-year vintages on disk; years outside this range are expected to lack income.
ACS_YEARS = range(2015, 2025)


def run_checks(df: pd.DataFrame) -> None:
    per_year = df.groupby("year")["county"].nunique()
    bad_years = per_year[per_year != N_COUNTIES]
    assert bad_years.empty, f"Years without {N_COUNTIES} counties:\n{bad_years}"

    dupes = df[df.duplicated(["county", "year"], keep=False)]
    assert dupes.empty, f"Duplicate county-years:\n{dupes[['county', 'year']]}"

    acs = df[df["year"].isin(ACS_YEARS)]
    missing = acs[acs["median_income"].isna()]
    assert missing.empty, f"Missing median_income after join:\n{missing[['county', 'year']]}"


def main() -> None:
    run_checks(pd.read_csv(OUT_JOINED))
    print("All checks passed")


if __name__ == "__main__":
    main()
