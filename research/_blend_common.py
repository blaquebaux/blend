#!/usr/bin/python3
# =============================================================================
# _blend_common.py — shared helpers for Blaque Baux BLEND (processing-margin spreads: crack / crush / spark).
# Alpaca SIP daily bars (adjustment=all → total return); env keys. Read-only.
#
# Processing-margin spreads are the gap between a raw input and its refined output — crack (crude → gasoline/
# distillates), crush (soybeans → oil + meal), spark (gas → electricity). Heiden & Seibert treat them as a distinct
# research area because the SPREAD trends at different times than the outright contract. BLEND tests the honest null:
# is a processing margin an INDEPENDENT risk premium / diversifying trend, or just directional beta on the input
# commodity? DATA REALITY: only the CRACK spread is cleanly feasible on Alpaca ETFs — USO (crude) → UGA (gasoline),
# plus CRAK (refiner equities, who earn the margin). CRUSH needs soybean-oil/meal ETFs and SPARK needs an electricity
# ETF — neither exists liquidly, so those are flagged, not tested (= blend_2 with a futures feed).
# =============================================================================
import os, json, urllib.request, math
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars(s):
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: b["c"] for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def panel(syms):
    D = {s: bars(s) for s in syms}; D = {s: v for s, v in D.items() if len(v) > 250}
    if not D: return {}, []
    u = list(D); dates = sorted(set.intersection(*[set(D[s]) for s in u]))
    return {s: np.array([D[s][d] for d in dates], float) for s in u}, dates

def rets(px): return px[1:] / px[:-1] - 1

def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return dict(sh=float('nan'), cagr=float('nan'), dd=float('nan'), vol=float('nan'))
    cum = np.cumprod(1 + r)
    return dict(sh=r.mean()/r.std()*math.sqrt(252), cagr=cum[-1]**(252/len(r))-1,
                dd=float((cum/np.maximum.accumulate(cum)-1).min()), vol=r.std()*math.sqrt(252))

def skew_of(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return float('nan')
    z = (r - r.mean())/r.std(); return float(np.mean(z**3))

def corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); m = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() > 30 else float('nan')

def dn_spread(long_r, short_r):
    """Vol-matched dollar-neutral spread (long − vol-scaled short), so it isn't a hidden input-beta bet."""
    long_r = np.asarray(long_r, float); short_r = np.asarray(short_r, float)
    m = min(len(long_r), len(short_r)); long_r, short_r = long_r[-m:], short_r[-m:]
    sl = (long_r.std()/short_r.std()) if short_r.std() > 0 else 1.0
    return long_r - sl*short_r
