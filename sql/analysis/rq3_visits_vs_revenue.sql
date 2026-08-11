-- ============================================================
-- RQ3: Does skier-visit volume predict Vail Resorts revenue, or is
-- revenue driven more by pricing changes and acquisitions than by
-- weather-driven visit volume?
--
-- IMPORTANT SCOPE LIMITATION: Vail Resorts operates resorts across
-- multiple US states and countries (Whistler Blackcomb, Park City,
-- Midwest/Northeast properties, etc.), while skier_visits is Colorado
-- statewide only. This test can only speak to whether Colorado
-- visitation correlates with total (not Colorado-only) company
-- revenue - a real, structural limitation on what this can prove.
-- ============================================================

-- Query 1: Side-by-side view - Vail Resorts fiscal year revenue next
-- to that same winter's Colorado skier visits (fiscal_year matches
-- winter_year: Vail's FY ends July 31, covering the ski season that
-- concluded that spring), with the acquisition-year flag shown.
SELECT
    r.fiscal_year,
    r.revenue_millions,
    r.is_acquisition_year,
    r.acquisition_note,
    v.visits AS co_skier_visits,
    v.measurement_basis
FROM vail_revenue r
LEFT JOIN skier_visits v
    ON v.winter_year = r.fiscal_year
    AND v.measurement_basis IN ('resort_level_sum', 'full_state_estimate')
ORDER BY r.fiscal_year;
