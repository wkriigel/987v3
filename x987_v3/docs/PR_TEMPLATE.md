# v3: Universal headful scraper + options_v2 + lean repo

## Goals
- Keep pricing/scoring + table view unchanged.
- Headful-only navigation/scraping.
- AutoTempest-first collector producing mixed VDPs (cars.com, truecar.com, carvana.com).
- Universal VDP scraper with small site profiles.
- Adopt options_v2; remove legacy options logic.
- Trim deps and nonessential tests/lints.

## Acceptance
- [ ] python -m x987 completes; CSVs non-empty when URLs present; table renders.
- [ ] Raw CSV shows cars.com, truecar.com, carvana.com sources.
- [ ] Pricing/scoring/view unchanged vs v2 Cars.com-only baseline.
- [ ] Minimal dependencies only; doctor OK.
- [ ] Repo free of vestigial files.