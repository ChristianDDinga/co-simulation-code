# profile_generator/plots.py
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _ensure_dt_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    return df


def _customer_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c != "date"]


def plot_all_customers_timeseries(
    df: pd.DataFrame,
    title: str,
    ylabel: str = "kW",
    out_path: str | None = None,
    alpha: float = 0.10,
    linewidth: float = 0.6,
):
    """
    Plot all customer profiles in one plot (each customer = one line).
    Works for PV / EV / consumption dataframes with columns: date + customers.
    """
    df = _ensure_dt_index(df)
    cols = _customer_cols(df)
    t = df["date"]

    plt.figure()
    for c in cols:
        plt.plot(t, df[c].values, alpha=alpha, linewidth=linewidth)

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.tight_layout()

    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=200)
    plt.show()


def plot_all_customers_daily_mean_band(
    df: pd.DataFrame,
    title: str,
    ylabel: str = "kW",
    out_path: str | None = None,
):
    """
    Optional: makes the plot easier to read by aggregating to daily mean
    and plotting mean ± percentiles across customers.
    """
    df = _ensure_dt_index(df)
    cols = _customer_cols(df)

    # daily mean per customer
    daily = df.set_index("date")[cols].resample("D").mean()

    # stats across customers for each day
    mean = daily.mean(axis=1)
    p10 = daily.quantile(0.10, axis=1)
    p90 = daily.quantile(0.90, axis=1)

    plt.figure()
    plt.plot(mean.index, mean.values)
    plt.fill_between(mean.index, p10.values, p90.values, alpha=0.2)

    plt.title(title + " (daily mean; band = 10–90% across customers)")
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.tight_layout()

    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=200)
    plt.show()


def plot_random_customer_three_profiles(
    pv_df: pd.DataFrame,
    ev_df: pd.DataFrame,
    cons_df: pd.DataFrame,
    customer_index_1based: int | None = None,
    title: str = "Random customer: PV, EV, Consumption",
    out_path: str | None = None,
):
    """
    Plot PV, EV, and consumption for ONE customer on the same figure.
    Uses customer_1(kW)...customer_95(kW) naming convention.
    """
    pv_df = _ensure_dt_index(pv_df)
    ev_df = _ensure_dt_index(ev_df)
    cons_df = _ensure_dt_index(cons_df)

    # assume same timestamps
    t = pv_df["date"]

    # choose customer
    n_customers = len(_customer_cols(pv_df))
    if customer_index_1based is None:
        customer_index_1based = np.random.randint(1, n_customers + 1)

    col = f"customer_{customer_index_1based}(kW)"
    if col not in pv_df.columns or col not in ev_df.columns or col not in cons_df.columns:
        raise KeyError(f"Expected column '{col}' in PV/EV/Consumption dataframes.")

    plt.figure()
    plt.plot(t, cons_df[col].values, label="Consumption")
    plt.plot(t, ev_df[col].values, label="EV")
    plt.plot(t, pv_df[col].values, label="PV")

    plt.title(f"{title} (customer {customer_index_1based})")
    plt.xlabel("Date")
    plt.ylabel("kW")
    plt.legend()
    plt.tight_layout()

    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=200)
    plt.show()


