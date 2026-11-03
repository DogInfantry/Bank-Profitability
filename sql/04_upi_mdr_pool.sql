-- Q: How big is the UPI MDR pool on the last twelve months of merchant (P2M) value?
-- Source: NPCI P2M value and ticket-band shares via FactIQ (in_npci_p2m_monthly). Same method as the model's Fees tab:
-- twelve-month value x simple average of the monthly share above INR 2,000 (months without a band split are skipped)
-- x (1 - 30% exempt) x 0.4% MDR x 0.95 haircut for the INR 300 cap.
WITH t12 AS (SELECT * FROM in_npci_p2m_monthly ORDER BY month DESC LIMIT 12)
SELECT min(month) AS from_month, max(month) AS to_month,
       round(sum(p2m_value_cr)) AS p2m_value_cr,
       round(avg(p2m_value_share_above_2000_pct), 2) AS value_share_above_2000_pct,
       count(p2m_value_share_above_2000_pct) AS months_with_band_split,
       round(sum(p2m_value_cr) * avg(p2m_value_share_above_2000_pct) / 100 * (1 - 0.30) * 0.004 * 0.95) AS mdr_pool_cr
FROM t12;
