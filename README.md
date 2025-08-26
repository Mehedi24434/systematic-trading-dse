# DSE Systematic Trading (Public Demo)

A compact, **three‑file** repo that demonstrates my end‑to‑end workflow for systematic equity trading on the Dhaka Stock Exchange (DSE): data updating, signal filters, and historical performance analysis. Alpha‑generating filters are intentionally **not** included—only illustrative filters are shown.

## Files in this repo

* `data_updater.py` — fetches day‑end data from DSE and updates per‑ticker CSVs, plus a small data‑hygiene helper.
* `Historical_performance.py` — three example filters and a yearly win/loss summary per filter.
* `myTrade.ipynb` — runnable walkthrough: update data → run filters → visualize performance.

> **Note on data**: The notebook expects per‑ticker CSVs under `./Scrapped_data/daily/` named like `AAMRANET.csv` with columns `date, open, high, low, close, volume, trade`.

## Quickstart

1. **Install**

   ```bash
   pip install -r requirements.txt
   ```

   Minimal requirements:

   * pandas
   * lxml  # for `pandas.read_html`
   * matplotlib  # for charts in the notebook

2. **Prepare data folder**

   * Create `./Scrapped_data/daily/` and drop a few sample ticker CSVs for testing. (Or run the updater for a specific date.)

3. **Run the demo notebook**

   * Open `myTrade.ipynb` and run all cells: it will (a) update daily data for a chosen date, (b) compute example filters, (c) show yearly win/loss ratios and simple charts.

## System design (high‑level)

* **Data layer**: day‑end archive pulled from DSE via `pandas.read_html`, merged into per‑ticker CSVs; a helper sanitizes zeros in OHLC using the previous close.
* **Signal layer**: three demonstration filters using classic TA blocks (RSI, MACD, rolling std, simple EMA/SMA relationships) and event/price‑action gates.
* **Backtest layer**: each filter simulates trades with fixed take‑profit / stop‑loss; outcomes are aggregated into yearly win/loss summaries.

## Example filters in this demo

* **Filter 1 — Momentum+Volatility spike**
  Uses RSI of rolling std‑dev on *trade* and price RSI thresholds; TP 15%, SL 8%.
* **Filter 2 — Mean‑reversion with regime screen**
  RSI oversold + MACD regime constraint + volume/participation proxy; TP 40%, SL 15%.
* **Filter 3 — Mean‑reversion (alt thresholds)**
  Variant gating on RSI bands and EMA regime; TP 15%, SL 8%.  

## Sample output

When filters are run, the system prints sample signals and yearly summaries.

Example signals:
```text
IBP gave a signal on 2025-06-19
AAMRANET gave a signal on 2024-11-05
BXPHARMA gave a signal on 2023-08-14  

```
> Exact research filters are withheld; these are safe, illustrative examples to showcase code quality and workflow.

## How to interpret historical performance

* Each filter reports **yearly wins, losses, and win/loss ratio** over all listed tickers for which data is available.
* These **do not** reflect live trading with costs, slippage, or liquidity constraints; they’re intentionally conservative approximations for portfolio‑level signal hit‑rate.
* **Historical ≠ live**: real‑time execution quality, availability (T+0/T+1), and corporate actions can materially change live results.

## Visualizations (in the notebook)

The notebook includes simple charts:

* Bars of wins vs losses per year per filter.
* Line chart of cumulative wins‑minus‑losses over time (toy equity proxy).

## Reproducibility & limits

* **Deterministic inputs**: the updater writes one new row per trading day; the filters are stateless across runs.
* **Known caveats**: corporate actions and symbol changes are not normalized; some illiquid tickers may have zeros in OHLC that are sanitized as described.

## Ethical & legal

* Data is obtained from DSE’s public day‑end archive for educational, non‑commercial demonstration here. Respect the exchange’s terms of use and rate limits.

## Contact

Mehedi Hasan Ahmed
Email: [mehedi24434@gmail.com](mailto:mehedi24434@gmail.com)
LinkedIn: <https://www.linkedin.com/in/mehedi-hasan-ahmed-1a2b3c4d5/>

---


