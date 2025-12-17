# profile_generator/combine_profiles.py
from __future__ import annotations
from pathlib import Path
import pandas as pd
from profile_generator.config_loader import load_profile_config
from profile_generator.pv_profile_generator import PvProfileGenerator
from profile_generator.ev_profile_generator import EvProfileGenerator
from profile_generator.consumption_profile_generator import ConsumptionProfileGenerator

def main() -> None:
    cfg = load_profile_config("configurations/profile_generator_config.yml")

    pv_cfg = cfg["pv_profile_generator"]
    ev_cfg = cfg["ev_profile_generator"]
    cons_cfg = cfg["consumption_profile_generator"]

    # Create generators from YAML
    pv_gen = PvProfileGenerator(
        csv_path=pv_cfg["csv_path"],
        n_customers=pv_cfg["n_customers"],
        noise_std_frac=pv_cfg["noise_pv"],
        random_state=pv_cfg["random_state"],
    )

    ev_gen = EvProfileGenerator(
        csv_path=ev_cfg["csv_path"],
        n_customers=ev_cfg["n_customers"],
        noise_std_frac=ev_cfg["noise_ev"],
        random_state=ev_cfg["random_state"],
    )

    cons_gen = ConsumptionProfileGenerator(
        csv_path=cons_cfg["csv_path"],
        n_customers=cons_cfg["n_customers"],
        noise_std_frac=cons_cfg["noise_consumption"],
        random_state=cons_cfg["random_state"],
    )

    # Sample profiles 
    pv_df = pv_gen.sample_pv_profiles(
        n_pv_customers=pv_cfg["n_pv_customers"],
        pv_size_kwp=pv_cfg["pv_size_kwp"],
        include_pv_mask=True,
    )

    ev_df = ev_gen.sample_ev_profiles(
        n_ev_customers=ev_cfg["n_ev_customers"],
        include_ev_mask=True,
    )

    cons_df = cons_gen.sample_consumption()

    # Align by date (safety)
    assert cons_df["date"].equals(ev_df["date"])
    assert cons_df["date"].equals(pv_df["date"])

    # Combine: net_load = consumption + EV - PV
    customer_cols = [c for c in cons_df.columns if c != "date"]

    combined = pd.DataFrame({"snapshots": cons_df["date"]})

    customer_cols = [c for c in cons_df.columns if c != "date"]
    combined[customer_cols] = (
        cons_df[customer_cols].to_numpy()
        + ev_df[customer_cols].to_numpy()
        - pv_df[customer_cols].to_numpy()
    )

    out_path = Path("data/combined_profiles_one_year.csv")
    combined.to_csv(out_path, index=False)   
    print("Saved:", out_path)


    # Plot summaries
#     from profile_generator.plots import (
#     plot_all_customers_timeseries,
#     plot_random_customer_three_profiles,
# )

# # PV: all customers together
#     plot_all_customers_timeseries(
#         pv_df,
#         title="PV profiles (all customers)",
#         ylabel="PV generation (kW)",
#     )

#     # EV: all customers together
#     plot_all_customers_timeseries(
#         ev_df,
#         title="EV profiles (all customers)",
#         ylabel="EV charging (kW)",
#     )

#     # Consumption: all customers together
#     plot_all_customers_timeseries(
#         cons_df,
#         title="Consumption profiles (all customers)",
#         ylabel="Consumption (kW)",
#     )

#     # One random customer: PV + EV + consumption together
#     plot_random_customer_three_profiles(
#         pv_df=pv_df,
#         ev_df=ev_df,
#         cons_df=cons_df,
#         customer_index_1based=None,   # random each run
#     )

