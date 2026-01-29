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

       
        customer_cols = [c for c in base_df.columns if c != "date"]
        if len(customer_cols) != n_customers:
            raise ValueError(f"Expected {n_customers} customer columns, got {len(customer_cols)}")

        self.base_mat = base_df[customer_cols].to_numpy(dtype=float)
        self.col_names = [f"Customer_{i+1} (kW)" for i in range(n_customers)]
        self.n_steps = self.base_mat.shape[0]

    def sample_ev_profiles(self, n_ev_customers: int, include_ev_mask: bool = False) -> pd.DataFrame:
        if not (0 <= n_ev_customers <= self.n_customers):
            raise ValueError(f"n_ev_customers must be between 0 and {self.n_customers}")

        # choose EV customers
        all_idx = np.arange(self.n_customers)
        ev_idx = self.rng.choice(all_idx, size=n_ev_customers, replace=False)

        mat = np.zeros_like(self.base_mat)
        mat[:, ev_idx] = self.base_mat[:, ev_idx]

        
        eps = self.rng.normal(0.0, self.noise_std_frac, size=mat.shape)
        mat_noisy = mat * (1.0 + eps)

        mat_noisy = np.clip(mat_noisy, self.clip_min_kw, None)

        out = pd.DataFrame(mat_noisy, columns=self.col_names)
        out.insert(0, "date", self.timestamps)

        if include_ev_mask:
            out.attrs["ev_customers_1based"] = (ev_idx + 1).tolist()
        return out
    





