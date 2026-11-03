# Tableau-ready extracts (long format)

| File | Grain | Key fields |
|---|---|---|
| banks_long.csv | bank x period x metric | row_id, entity (NSE symbol), period (FY26, Q2FY27, FYxx), metric, value, unit, source, page, status (primary / secondary-tied / derived) |
| upi_app_share_long.csv | month x app | month, app (normalised), app_type (Bank app / Third-party app), volume (count), value_rs, volume_share |
| upi_monthly.csv | month | volume_mn, value_cr, avg_ticket_rs, daily_volume_mn, mom_volume_pct, source |
| insurers_exposure.csv | insurer (FY25) | total_premium, indiv_nb_<channel> premium, bank_ca_share, blended_gap_pp, reset_cr, reset_pct_total_premium, pat_fy25, reset_pct_pat |

Units: INR crore unless stated; ratios in %. `status=derived` rows are computed in `pipeline/`; trace them through `docs/methodology.md`.
Suggested Tableau build: one data source per file; RoA tree as a stacked bar on banks_long (metric in nii/other_income/opex/provisions/tax, period=FY26); app share as an area chart on upi_app_share_long with a 30% reference line.
