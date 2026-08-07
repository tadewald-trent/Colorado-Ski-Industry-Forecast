-- ============================================================
-- Assign region (north/south) to ALL stations based on county,
-- not just the 7 core stations. This lets RQ1's SNOTEL/SWE
-- comparison use the full 46-station dataset instead of just
-- Vail Mountain vs. Wolf Creek Summit.
--
-- North counties: Summit, Routt, Grand, Eagle
-- South counties: San Miguel, Gunnison, Mineral
-- ============================================================

UPDATE stations
SET region = 'north'
WHERE county IN ('Summit', 'Routt', 'Grand', 'Eagle')
  AND region IS NULL;

UPDATE stations
SET region = 'south'
WHERE county IN ('San Miguel', 'Gunnison', 'Mineral')
  AND region IS NULL;

-- Verify: every station should now have a region assigned
SELECT region, COUNT(*) FROM stations GROUP BY region;
