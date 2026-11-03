-- Q: Base, Upside and Downside side by side: FY29E RoA, RoE, NIM and value per share.
-- Source: recalculated model export (hdfc_scenarios).
SELECT scenario,
       round(100 * max(value) FILTER (WHERE line = 'Return on average assets' AND period = 'FY29E'), 2) AS roa_fy29_pct,
       round(100 * max(value) FILTER (WHERE line = 'Return on average net worth' AND period = 'FY29E'), 1) AS roe_fy29_pct,
       round(100 * max(value) FILTER (WHERE line = 'Net interest margin on interest-earning assets' AND sheet = 'Model' AND period = 'FY29E'), 2) AS nim_fy29_pct,
       round(max(value) FILTER (WHERE line = 'RoA FY29E with levers' AND period = 'E'), 1) AS roa_with_levers_bp,
       round(max(value) FILTER (WHERE line = 'Residual income per share' AND period = 'E')) AS ri_per_share,
       round(max(value) FILTER (WHERE line = 'Sum of the parts per share' AND period = 'E')) AS sotp_per_share
FROM hdfc_scenarios
GROUP BY scenario
ORDER BY roa_fy29_pct;
