




# profile_generator/ev_profile_generator.py
from __future__ import annotations
import pandas as pd
import numpy as np

class EvProfileGenerator:
    def __init__(
        self,
        csv_path: str,
        n_customers: int = 95,
        noise_std_frac: float = 0.15,
        clip_min_kw: float = 0.0,
        random_state: int | None = None,
    ):
        self.n_customers = n_customers
        self.noise_std_frac = noise_std_frac
        self.clip_min_kw = clip_min_kw
        self.rng = np.random.default_rng(random_state)

        base_df = pd.read_csv(csv_path, parse_dates=["date"])
        self.timestamps = base_df["date"].reset_index(drop=True)

        # assume all other columns are customers
        customer_cols = [c for c in base_df.columns if c != "date"]
        if len(customer_cols) != n_customers:
            raise ValueError(f"Expected {n_customers} customer columns, got {len(customer_cols)}")

        self.base_mat = base_df[customer_cols].to_numpy(dtype=float)
        self.col_names = [f"customer_{i+1}(kW)" for i in range(n_customers)]
        self.n_steps = self.base_mat.shape[0]

    def sample_ev_profiles(self, n_ev_customers: int, include_ev_mask: bool = False) -> pd.DataFrame:
        if not (0 <= n_ev_customers <= self.n_customers):
            raise ValueError(f"n_ev_customers must be between 0 and {self.n_customers}")

        # choose EV customers
        all_idx = np.arange(self.n_customers)
        ev_idx = self.rng.choice(all_idx, size=n_ev_customers, replace=False)

        mat = np.zeros_like(self.base_mat)
        mat[:, ev_idx] = self.base_mat[:, ev_idx]

        # multiplicative Gaussian noise: x * (1 + eps)
        eps = self.rng.normal(0.0, self.noise_std_frac, size=mat.shape)
        mat_noisy = mat * (1.0 + eps)

        mat_noisy = np.clip(mat_noisy, self.clip_min_kw, None)

        out = pd.DataFrame(mat_noisy, columns=self.col_names)
        out.insert(0, "date", self.timestamps)

        if include_ev_mask:
            out.attrs["ev_customers_1based"] = (ev_idx + 1).tolist()
        return out
    








    
# # ev_profile_generator.py
# from __future__ import annotations

# import pandas as pd
# import numpy as np


# class EvProfileGenerator:
#     """
#     Generates one-year 15-min EV charging profiles with Gaussian noise.
#     """

#     def __init__(
#         self,
#         csv_path: str,
#         n_customers: int = 95,
#         noise_std_frac: float = 0.10,   # EV behavior is noisier than PV
#         clip_min_kw: float = 0.0,
#         random_state: int | None = None,
#     ):
#         self.csv_path = csv_path
#         self.n_customers = n_customers
#         self.noise_std_frac = noise_std_frac
#         self.clip_min_kw = clip_min_kw

#         self.rng = np.random.default_rng(random_state)

#         # Load base EV profiles
#         base_df = pd.read_csv(csv_path, parse_dates=["date"])
#         self.timestamps = base_df["date"].reset_index(drop=True)

#         # Expect customer columns only after date
#         self.base_ev = base_df.iloc[:, 1:].to_numpy(dtype=float)

#         if self.base_ev.shape[1] != n_customers:
#             raise ValueError("Mismatch between n_customers and EV profile columns")

#         self.n_steps = len(self.base_ev)

#     # ----------------------------
#     # EV sampling
#     # ----------------------------
#     def sample_ev_profiles(
#         self,
#         n_ev_customers: int,
#         customer_prefix: str = "customer_",
#         include_ev_mask: bool = False,
#     ) -> pd.DataFrame:

#         if not (0 <= n_ev_customers <= self.n_customers):
#             raise ValueError(f"n_ev_customers must be between 0 and {self.n_customers}")

#         # Select EV customers
#         all_idx = np.arange(self.n_customers)
#         ev_idx = self.rng.choice(all_idx, size=n_ev_customers, replace=False)
#         ev_mask = np.zeros(self.n_customers, dtype=bool)
#         ev_mask[ev_idx] = True

#         # Initialize output matrix
#         mat = np.zeros((self.n_steps, self.n_customers), dtype=float)

#         # Add noise only to EV customers
#         for j in ev_idx:
#             base = self.base_ev[:, j]
#             eps = self.rng.normal(0.0, self.noise_std_frac, size=self.n_steps)
#             noisy = base * (1.0 + eps)
#             mat[:, j] = np.clip(noisy, self.clip_min_kw, None)

#         # Build DataFrame
#         col_names = [f"{customer_prefix}{i+1}(kW)" for i in range(self.n_customers)]
#         out = pd.DataFrame(mat, columns=col_names)
#         out.insert(0, "date", self.timestamps)

#         if include_ev_mask:
#             out.attrs["ev_customers_1based"] = (ev_idx + 1).tolist()

#         return out


# # ----------------------------
# # Example usage
# # ----------------------------
# if __name__ == "__main__":
#     gen = EvProfileGenerator(
#         csv_path="data/ev_one_year_15min.csv",
#         n_customers=95,
#         noise_std_frac=0.15,   # EVs are more stochastic
#         random_state=42
#     )

#     ev_df = gen.sample_ev_profiles(
#         n_ev_customers=40,
#         include_ev_mask=True
#     )

#     print(ev_df.head())
#     print("Rows:", len(ev_df))        # 35040
#     print("Cols:", ev_df.shape[1])    # 1 + 95
#     print("EV customers:", ev_df.attrs.get("ev_customers_1based"))

#     # ev_df.to_csv("ev_profiles_95_customers_40ev.csv", index=False)
