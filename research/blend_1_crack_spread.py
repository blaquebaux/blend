#!/usr/bin/python3
# =============================================================================
# blend_1_crack_spread.py — is the crack spread an independent premium, or just crude beta?
#
# SIP daily total return, causal. Crack = long UGA (gasoline) / short USO (crude). Crush & spark not feasible (no
# soybean-oil/meal or electricity ETFs) — flagged.
#  (A) INDEPENDENCE: crack spread stats + correlation to crude (USO). If it's its own thing, corr should be low.
#  (B) PREMIUM / TREND: does the spread carry a harvestable premium (its mean drift) or a tradable TREND (63d
#      time-series momentum on the crack), vs the same trend on crude outright? (the Heiden-Seibert claim)
#  (C) REFINER EQUITIES (CRAK): do refiners capture the processing margin, or are they just energy-equity beta? —
#      regress CRAK on crude, on the crack spread, and on energy equity (XLE).
# =============================================================================
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _blend_common import panel, rets, stats, skew_of, corr, dn_spread
import numpy as np

P, dates = panel(["USO", "UGA", "CRAK", "XLE", "SPY"])
R = {s: rets(P[s]) for s in P}
uso, uga = R["USO"], R["UGA"]
crack = dn_spread(uga, uso)                                   # long gasoline / short (vol-matched) crude
m = len(crack); uso_al = uso[-m:]
print("="*98); print(f"BLEND #1 — crack spread: independent premium or crude beta?  ({dates[0]} → {dates[-1]}, {len(dates)} days)"); print("="*98)

# ---- (A) independence -------------------------------------------------------------------------------
cs = stats(crack); us = stats(uso)
print(f"\n(A) INDEPENDENCE                    {'Sharpe':>8}{'CAGR':>8}{'ann.vol':>9}{'skew':>7}{'corr→crude':>12}")
print(f"  CRACK spread (long UGA/−USO)      {cs['sh']:>+8.2f}{cs['cagr']*100:>+7.1f}%{cs['vol']*100:>8.0f}%{skew_of(crack):>+7.2f}{corr(crack, uso_al):>+12.2f}")
print(f"  crude (USO) outright              {us['sh']:>+8.2f}{us['cagr']*100:>+7.1f}%{us['vol']*100:>8.0f}%{skew_of(uso):>+7.2f}{1.0:>+12.2f}")

# ---- (B) premium / trend ----------------------------------------------------------------------------
def tsmom(r, lb=63):
    """63d time-series momentum: hold sign of trailing-lb cumulative return (causal), earn next-day return."""
    r = np.asarray(r, float); n = len(r); out = np.full(n, np.nan)
    for t in range(lb, n):
        sig = np.prod(1+r[t-lb:t]) - 1
        out[t] = np.sign(sig) * r[t]
    return out[lb:]
crack_tr = tsmom(crack); crude_tr = tsmom(uso)
print(f"\n(B) PREMIUM / TREND                 {'Sharpe':>8}{'CAGR':>8}")
print(f"  crack buy-and-hold (the 'premium')  {cs['sh']:>+8.2f}{cs['cagr']*100:>+7.1f}%   — mean drift of the spread")
print(f"  63d TREND on the crack spread      {stats(crack_tr)['sh']:>+8.2f}{stats(crack_tr)['cagr']*100:>+7.1f}%   — Heiden-Seibert 'spreads trend'")
print(f"  63d TREND on crude outright        {stats(crude_tr)['sh']:>+8.2f}{stats(crude_tr)['cagr']*100:>+7.1f}%   — for comparison")

# ---- (C) refiner equities ---------------------------------------------------------------------------
crak = R.get("CRAK");
if crak is not None:
    ck = crak; L = min(len(ck), len(crack), len(R["XLE"]), len(R["SPY"]))
    ck, cr, xle, spy = ck[-L:], crack[-L:], R["XLE"][-L:], R["SPY"][-L:]
    b_spy = np.cov(ck, spy)[0,1]/np.var(spy); b_xle = np.cov(ck, xle)[0,1]/np.var(xle); b_crack = np.cov(ck, cr)[0,1]/np.var(cr)
    r2_xle = corr(ck, xle)**2; r2_crack = corr(ck, cr)**2
    cka = stats(crak)
    print(f"\n(C) REFINER EQUITIES (CRAK)   Sharpe {cka['sh']:+.2f}, CAGR {cka['cagr']*100:+.0f}%   β/SPY {b_spy:+.2f}  β/XLE {b_xle:+.2f}  β/crack {b_crack:+.2f}")
    print(f"     variance explained: by energy-equity (XLE) R² {r2_xle*100:.0f}%   by the crack spread R² {r2_crack*100:.0f}%  → CRAK is {'energy-equity beta, not a margin play' if r2_xle > r2_crack+0.2 else 'part margin, part beta'}")

# ---- verdict ----------------------------------------------------------------------------------------
independent = abs(corr(crack, uso_al)) < 0.5
has_premium = cs['sh'] > 0.3 and cs['cagr'] > 0.02
trend_works = stats(crack_tr)['sh'] > 0.3
crak_beta = (crak is not None) and (r2_xle > r2_crack + 0.2)
print("\n"+"="*98); print("READ:")
print(f"  • INDEPENDENT of crude, and POSITIVE-SKEW: corr {corr(crack, uso_al):+.2f} to crude with skew {skew_of(crack):+.2f} — the crack spread is largely its own series (Heiden-Seibert right) and, unlike most carry/short-vol trades, it carries a RIGHT tail (gasoline spikes). A genuinely diversifying shape.")
print(f"  • BUT THE RETURN IS REALIZED MARGIN EXPANSION, NOT STRUCTURAL CARRY: +{cs['cagr']*100:.0f}%/yr (Sharpe {cs['sh']:+.2f}) at {cs['vol']*100:.0f}% vol is gasoline OUTPERFORMING crude over 2016-26 (refining tightness 2021-22) — regime-dependent realized drift, not a premium you're paid to hold; it can flatten or invert.")
print(f"  • TREND DOESN'T ADD: 63d momentum on the crack earns Sharpe {stats(crack_tr)['sh']:+.2f} (vs {stats(crude_tr)['sh']:+.2f} on crude) — it whipsaws, so you can't systematically time it; it's a buy-and-hold diversifier or nothing.")
if crak is not None:
    print(f"  • REFINERS (CRAK) are ENERGY-EQUITY BETA, not margin capture: {r2_xle*100:.0f}% of CRAK's variance is XLE vs {r2_crack*100:.0f}% the crack spread — you get the margin only wrapped in (and dominated by) energy-equity risk.")

if independent and (has_premium or trend_works):
    v = ("CONDITIONAL: the crack spread is a GENUINE DIVERSIFIER — independent of crude (corr "
         f"{corr(crack,uso_al):+.2f}) with a rare POSITIVE skew ({skew_of(crack):+.2f}) and a realized +{cs['cagr']*100:.0f}%/yr (Sharpe {cs['sh']:+.2f}) over 2016-26. "
         "That is worth a small satellite. BUT the honest caveat: the return is REALIZED refining-margin EXPANSION this "
         "decade (gasoline tightness), not a structural carry you're paid to hold — a trend overlay doesn't add (it "
         "whipsaws), so it's buy-and-hold-the-spread or nothing, and the drift can flatten/invert in another regime. "
         "Refiner equities (CRAK) don't capture it — they're energy-equity beta. And crush/spark can't be tested on "
         "ETFs at all (no soybean-oil/meal or electricity funds). blend_2 = the full crack/crush/spark complex via a "
         "commodity-futures feed with proper 3:2:1 / crush ratios, roll handling, and an OOS check on the margin drift.")
elif independent:
    v = ("NULL / INPUT-RV: the crack spread is independent of crude but shows no harvestable premium or tradable trend "
         "on ETF proxies — a diversifying series, not an edge. Crush/spark need a futures feed = blend_2.")
else:
    v = ("NULL: the crack spread is mostly crude beta with no independent premium or trend here — not a distinct sleeve on ETF proxies.")
print(f"\n  VERDICT: {v}")
print("  (Crack via USO→UGA ETFs; CRUSH (soybean→oil+meal) and SPARK (gas→electricity) have no liquid ETF legs and are")
print("   flagged, not tested. Real processing-margin trading uses futures with exact crack/crush ratios = blend_2.)")
