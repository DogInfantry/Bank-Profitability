-- Q: Is HDFC Bank's credit cost below its through-the-cycle level, and by how much?
-- Source: IR26 p234 loan-loss provisions and advances; credit cost = provisions / average advances.
WITH long AS (
  UNPIVOT in_hdfc_10yr_highlights ON COLUMNS(* EXCLUDE (metric, source)) INTO NAME fy VALUE v),
w AS (
  SELECT fy, max(v) FILTER (WHERE metric = 'loan_loss_provisions') AS llp, max(v) FILTER (WHERE metric = 'loans') AS loans
  FROM long GROUP BY fy),
c AS (SELECT fy, llp / ((loans + lag(loans) OVER (ORDER BY fy)) / 2) AS cc FROM w)
SELECT round(100 * avg(cc) FILTER (WHERE fy BETWEEN 'FY21' AND 'FY26'), 2) AS through_cycle_fy21_26_pct,
       round(100 * avg(cc) FILTER (WHERE fy BETWEEN 'FY24' AND 'FY26'), 2) AS recent_fy24_26_pct,
       round(1e4 * (avg(cc) FILTER (WHERE fy BETWEEN 'FY21' AND 'FY26') - avg(cc) FILTER (WHERE fy BETWEEN 'FY24' AND 'FY26'))) AS normalisation_gap_bp
FROM c;
