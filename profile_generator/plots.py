from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _ensure_dt_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    return df


def _customer_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c != "date"]


def _drop_tz(s: pd.Series) -> pd.Series:
    """
    Make a datetime Series timezone-naive.
    Works for both tz-aware and tz-naive datetimes.
    """
    
    if getattr(s.dt, "tz", None) is not None:
        return s.dt.tz_convert(None)
    
    return s


def plot_all_customers_timeseries(
    df: pd.DataFrame,
    title: str,
    ylabel: str = "kW",
    out_path: str | None = None,
    alpha: float = 0.10,
    linewidth: float = 0.6,
):
    df = _ensure_dt_index(df)
    df["date"] = _drop_tz(df["date"])

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


def plot_random_day_all_customers(
    pv_df: pd.DataFrame,
    ev_df: pd.DataFrame,
    cons_df: pd.DataFrame,
    day: str | pd.Timestamp | None = None,
    ylabel: str = "kW",
    alpha: float = 0.15,
    linewidth: float = 0.7,
    out_dir: str | None = None,
):
   
    pv_df = _ensure_dt_index(pv_df)
    ev_df = _ensure_dt_index(ev_df)
    cons_df = _ensure_dt_index(cons_df)

   
    pv_df["date"] = _drop_tz(pv_df["date"])
    ev_df["date"] = _drop_tz(ev_df["date"])
    cons_df["date"] = _drop_tz(cons_df["date"])

    
    if day is None:
        available_days = cons_df["date"].dt.normalize().unique()
        day = pd.Timestamp(np.random.choice(available_days))
    else:
        day = pd.Timestamp(day).normalize()

    start = day
    end = day + pd.Timedelta(days=1)

   
    pv_day = pv_df[(pv_df["date"] >= start) & (pv_df["date"] < end)]
    ev_day = ev_df[(ev_df["date"] >= start) & (ev_df["date"] < end)]
    cons_day = cons_df[(cons_df["date"] >= start) & (cons_df["date"] < end)]

    if pv_day.empty or ev_day.empty or cons_day.empty:
        raise ValueError(f"No data found for day {day.date()}")

   
    cust_cols = _customer_cols(cons_day)

    
    def _plot(df_day: pd.DataFrame, title: str, filename: str | None):
        t = df_day["date"]

        plt.figure()
        for c in cust_cols:
            plt.plot(t, df_day[c].values, alpha=alpha, linewidth=linewidth)

        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel(ylabel)
        plt.tight_layout()

        if filename is not None:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(filename, dpi=200)

        plt.show()

    date_str = day.strftime("%Y-%m-%d")

    _plot(
        cons_day,
        f"Consumption – all customers ({date_str})",
        None if out_dir is None else f"{out_dir}/consumption_{date_str}.png",
    )
    _plot(
        ev_day,
        f"EV charging – all customers ({date_str})",
        None if out_dir is None else f"{out_dir}/ev_{date_str}.png",
    )
    _plot(
        pv_day,
        f"PV generation – all customers ({date_str})",
        None if out_dir is None else f"{out_dir}/pv_{date_str}.png",
    )
