









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

        out = pd.DataFrame(mat, columns=[f"customer_{i+1}(kW)" for i in range(self.n_customers)])
        out.insert(0, "date", self.timestamps)

        if include_pv_mask:
            out.attrs["pv_customers_1based"] = (pv_idx + 1).tolist()
        return out





# # irradiance_generator.py

# from __future__ import annotations

# import pandas as pd
# import numpy as np


# class PvProfileGenerator:

#     def __init__(
#         self,
#         csv_path: str,
#         n_customers: int = 95,
#         noise_std_frac: float = 0.07,     # epsilon ~ N(0, 0.07)
#         clip_min_irr: float = 0.0,
#         stc_irradiance: float = 1000.0,   # W/m² at STC
#         random_state: int | None = None,
#     ):
#         self.csv_path = csv_path
#         self.n_customers = n_customers
#         self.noise_std_frac = noise_std_frac
#         self.clip_min_irr = clip_min_irr
#         self.stc_irradiance = stc_irradiance

#         self.rng = np.random.default_rng(random_state)

#         # Load base irradiance profile
#         base_df = pd.read_csv(csv_path, parse_dates=["date"])
#         self.timestamps = base_df["date"].reset_index(drop=True)
#         self.base_irradiance = base_df["irradiance"].to_numpy(dtype=float)
#         self.n_steps = len(self.base_irradiance)

   
#     # Irradiance sampling
    
#     def sample_irradiance_one_year(self) -> pd.DataFrame:
        
#         eps = self.rng.normal(loc=0.0, scale=self.noise_std_frac, size=self.n_steps)
#         irr_noisy = self.base_irradiance * (1.0 + eps)
#         irr_noisy = np.clip(irr_noisy, self.clip_min_irr, None)  # no negative irradiance
#         return pd.DataFrame({"date": self.timestamps, "irradiance": irr_noisy})

    
#     # PV assignment + power
    
#     def sample_pv_profiles(
#         self,
#         n_pv_customers: int,
#         pv_size_kwp: float,
#         customer_prefix: str = "customer_",
#         include_pv_mask: bool = False,
#     ) -> pd.DataFrame:
#         # Input validation
#         if not (0 <= n_pv_customers <= self.n_customers):
#             raise ValueError(f"n_pv_customers must be between 0 and {self.n_customers}")

#         if pv_size_kwp < 0:
#             raise ValueError("pv_size_kwp must be >= 0")

#         # Sample irradiance for this "scenario-year"
#         irr_df = self.sample_irradiance_one_year()
#         irr = irr_df["irradiance"].to_numpy(dtype=float)

#         # Convert irradiance -> PV power per PV customer (kW)
    
#         pv_power_single = pv_size_kwp * (irr / self.stc_irradiance)
#         pv_power_single = np.clip(pv_power_single, 0.0, None)

#         # Choose random PV customer indices (1..n_customers)
#         all_idx = np.arange(self.n_customers)
#         pv_idx = self.rng.choice(all_idx, size=n_pv_customers, replace=False)
#         pv_mask = np.zeros(self.n_customers, dtype=bool)
#         pv_mask[pv_idx] = True

#         # Build (time_steps x n_customers) matrix
#         mat = np.zeros((self.n_steps, self.n_customers), dtype=float)
#         mat[:, pv_mask] = pv_power_single[:, None]  # broadcast to selected customers

#         # 5 Build DataFrame
#         col_names = [f"{customer_prefix}{i+1}(kW)" for i in range(self.n_customers)]
#         out = pd.DataFrame(mat, columns=col_names)
#         out.insert(0, "date", self.timestamps)

#         if include_pv_mask:
#             out.attrs["pv_customers_1based"] = (pv_idx + 1).tolist()
#         return out


# if __name__ == "__main__":
#     gen = PvProfileGenerator(
#         csv_path="data/irradiance_one_year_15min.csv",
#         n_customers=95,
#         noise_std_frac=0.07,
#         random_state=42
#     )

#     pv_df = gen.sample_pv_profiles(
#         n_pv_customers=50,
#         pv_size_kwp=10.0,
#         include_pv_mask=True
#     )

#     print(pv_df.head())
#     print("Rows:", len(pv_df))         # 35040
#     print("Cols:", pv_df.shape[1])     # 1 + 95
#     print("PV customers:", pv_df.attrs.get("pv_customers_1based"))

#     #pv_df.to_csv("pv_profiles_95_customers_50pv_10kwp.csv", index=False)
