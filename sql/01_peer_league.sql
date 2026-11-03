-- Q: Where does HDFC Bank rank on FY26 RoA among the twelve listed banks, and how far is it from the best?
-- Source: Screener standalone financials and valuation (view v_peer_league).
SELECT symbol, ownership, round(roa * 100, 2) AS roa_pct, round(roe * 100, 1) AS roe_pct,
       round(price_to_book, 2) AS price_to_book, roa_rank, round(roa_gap_to_best_bp) AS gap_to_best_bp
FROM v_peer_league
ORDER BY roa_rank;
