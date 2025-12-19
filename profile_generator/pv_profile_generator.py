
# profile_generator/pv_profile_generator.py
from __future__ import annotations
import pandas as pd
import numpy as np

class PvProfileGenerator:
    def __init__(
        self,
        csv_path: str,
        n_customers: int = 95,
        noise_std_frac: float = 0.07,
        clip_min_irr: float = 0.0,
        stc_irradiance: float = 1000.0,
        random_state: int | None = None,
    ):
        self.n_customers = n_customers
        self.noise_std_frac = noise_std_frac
        self.clip_min_irr = clip_min_irr
        self.stc_irradiance = stc_irradiance
        self.rng = np.random.default_rng(random_state)

        base_df = pd.read_csv(csv_path, parse_dates=["date"])
        self.timestamps = base_df["date"].reset_index(drop=True)
        self.base_irradiance = base_df["irradiance"].to_numpy(dtype=float)
        self.n_steps = len(self.base_irradiance)

    def sample_irradiance_one_year(self) -> pd.DataFrame:
        eps = self.rng.normal(0.0, self.noise_std_frac, size=self.n_steps)
        irr_noisy = self.base_irradiance * (1.0 + eps)
        irr_noisy = np.clip(irr_noisy, self.clip_min_irr, None)
        return pd.DataFrame({"date": self.timestamps, "irradiance": irr_noisy})

    def sample_pv_profiles(
        self,
        n_pv_customers: int,
        pv_size_kwp: float,
        include_pv_mask: bool = False,
    ) -> pd.DataFrame:
        if not (0 <= n_pv_customers <= self.n_customers):
            raise ValueError(f"n_pv_customers must be between 0 and {self.n_customers}")
        if pv_size_kwp < 0:
            raise ValueError("pv_size_kwp must be >= 0")

        irr = self.sample_irradiance_one_year()["irradiance"].to_numpy(float)

        pv_power_single = pv_size_kwp * (irr / self.stc_irradiance)
        pv_power_single = np.clip(pv_power_single, 0.0, None)

        all_idx = np.arange(self.n_customers)
        pv_idx = self.rng.choice(all_idx, size=n_pv_customers, replace=False)

        mat = np.zeros((self.n_steps, self.n_customers), dtype=float)
        mat[:, pv_idx] = pv_power_single[:, None]

        out = pd.DataFrame(mat, columns=[f"Customer_{i+1} (kW)" for i in range(self.n_customers)])
        out.insert(0, "date", self.timestamps)

        if include_pv_mask:
            out.attrs["pv_customers_1based"] = (pv_idx + 1).tolist()
        return out


