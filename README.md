# Blaque Baux Blend

**Processing-margin spreads (crack / crush / spark) — an independent premium, or just input beta? The crack spread is a real diversifier, but its return is realized margin expansion, not carry.**

Processing margins are the gap between a raw input and its refined output — crack (crude → gasoline), crush (soybeans →
oil + meal), spark (gas → electricity). Heiden & Seibert treat them as a distinct area because the *spread* trends at
different times than the outright. Blend tests the honest null: independent risk premium, or directional beta on the
input? **Data reality:** only the **crack spread** is cleanly feasible on Alpaca ETFs (USO → UGA, plus CRAK refiners);
crush and spark have no liquid ETF legs and are flagged, not tested.

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/blend_1_crack_spread.py   # needs Alpaca data keys in the environment
```

## The finding (a genuine diversifier, with a caveat)

[`research/blend_1_crack_spread.py`](research/blend_1_crack_spread.py) — crack = long UGA / short vol-matched USO,
SIP daily total return, causal, 2016–2026.

| | Sharpe | CAGR | ann. vol | skew | corr → crude |
|---|---|---|---|---|---|
| CRACK spread (long UGA / −USO) | **+0.43** | +7.8% | 24% | **+1.31** | **−0.32** |
| crude (USO) outright | +0.29 | +3.8% | 39% | −0.91 | +1.00 |

- **Independent *and* positive-skew** — corr −0.32 to crude with skew **+1.31**. Unlike most carry/short-vol trades, the
  crack carries a *right* tail (gasoline spikes). A genuinely diversifying shape — Heiden-Seibert are right that it's its
  own series.
- **But the return is realized margin expansion, not structural carry.** The +8%/yr is gasoline *outperforming* crude
  over 2016–26 (refining tightness in 2021-22) — regime-dependent realized drift, not a premium you're paid to hold; it
  can flatten or invert.
- **Trend doesn't add.** 63-day momentum on the crack earns Sharpe −0.04 (vs +0.06 on crude) — it whipsaws, so you can't
  systematically time it. Buy-and-hold-the-spread or nothing.
- **Refiners (CRAK) are energy-equity beta**, not margin capture: 61% of CRAK's variance is XLE vs **1%** the crack spread.

## Verdict

**CONDITIONAL — a genuine diversifier, worth a small satellite, but not a structural premium.** The crack spread is
independent of crude with a rare positive skew and a real +0.43 Sharpe this decade; that earns a tactical place. The
honest caveat is that the return is *realized refining-margin expansion*, not carry — a trend overlay doesn't rescue the
timing, so it's buy-and-hold or nothing, and the drift can reverse in another regime. Crush and spark can't be tested on
ETFs at all. A `blend_2` builds the full crack/crush/spark complex on a commodity-futures feed with proper 3:2:1 / crush
ratios, roll handling, and an out-of-sample check on whether the margin drift persists.

## Status

**Research.** Honest conditional — one feasible leg (crack) tested with the premium-vs-beta question answered squarely,
the other two legs flagged as data-blocked. Independence/skew diagnostics, trend test, refiner-equity decomposition,
Alpaca SIP daily total return. No live capital.
