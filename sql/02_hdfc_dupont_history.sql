-- Q: How did HDFC Bank's RoA tree move over ten years, and when did the margin step down?
-- Source: HDFC Bank IR26 p234 ten-year highlights (table in_hdfc_10yr_highlights), simple-average assets.
WITH long AS (
  UNPIVOT in_hdfc_10yr_highlights ON COLUMNS(* EXCLUDE (metric, source)) INTO NAME fy VALUE v),
w AS (
  SELECT fy,
         max(v) FILTER (WHERE metric = 'nii') AS nii, max(v) FILTER (WHERE metric = 'other_income') AS oi,
         max(v) FILTER (WHERE metric = 'opex') AS opex, max(v) FILTER (WHERE metric = 'provisions_total') AS prov,
         max(v) FILTER (WHERE metric = 'pat') AS pat, max(v) FILTER (WHERE metric = 'total_assets') AS ta
  FROM long GROUP BY fy),
a AS (SELECT *, (ta + lag(ta) OVER (ORDER BY fy)) / 2 AS avg_ta FROM w)
SELECT fy,
       round(100 * nii / avg_ta, 2) AS nii_pct, round(100 * oi / avg_ta, 2) AS other_income_pct,
       round(100 * opex / avg_ta, 2) AS opex_pct, round(100 * prov / avg_ta, 2) AS provisions_pct,
       round(100 * pat / avg_ta, 2) AS roa_pct
FROM a WHERE avg_ta IS NOT NULL ORDER BY fy;
