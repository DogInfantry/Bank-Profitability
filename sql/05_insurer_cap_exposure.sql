-- Q: Which life insurers are most exposed to the proposed IRDAI commission caps relative to profit?
-- Source: insurance module output (tidy_ins_insurer_exposure): commission above caps vs FY25 PAT.
SELECT insurer, round(reset_cr) AS reset_cr, round(reset_pct_total_premium, 2) AS pct_of_premium,
       round(reset_pct_pat) AS pct_of_fy25_pat
FROM tidy_ins_insurer_exposure
WHERE reset_pct_pat IS NOT NULL
ORDER BY reset_pct_pat DESC
LIMIT 10;
