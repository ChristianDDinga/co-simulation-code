from __future__ import annotations
import pandas as pd
import numpy as np


class ConsumptionProfileGenerator:
    def __init__(
        self,
        csv_path: str,
        n_customers: int = 95,
        noise_std_frac: float = 0.02,
        clip_min_kw: float = 0.0,
        random_state: int | None = None,
    ):
        self.csv_path = csv_path
        self.n_customers = n_customers
        self.noise_std_frac = noise_std_frac
        self.clip_min_kw = clip_min_kw
        self.rng = np.random.default_rng(random_state)

        base_df = pd.read_csv(csv_path, parse_dates=["date"])
        if "date" not in base_df.columns:
            raise ValueError("CSV must contain a 'date' column")

        self.timestamps = base_df["date"].reset_index(drop=True)

        customer_cols = [c for c in base_df.columns if c != "date"]
        if len(customer_cols) != n_customers:
            raise ValueError(f"Expected {n_customers} customer columns, got {len(customer_cols)}")

        self.customer_cols = customer_cols  # keep original names
        self.base_mat = base_df[customer_cols].to_numpy(dtype=float)
        self.n_steps = self.base_mat.shape[0]

        if self.n_steps != 35040:
            raise ValueError(f"Expected 35040 rows (15-min year), got {self.n_steps}")

    def sample_consumption(self) -> pd.DataFrame:
        eps = self.rng.normal(loc=0.0, scale=self.noise_std_frac, size=self.base_mat.shape)
        mat_noisy = self.base_mat * (1.0 + eps)
        mat_noisy = np.clip(mat_noisy, self.clip_min_kw, None)

        out = pd.DataFrame(mat_noisy, columns=self.customer_cols)
        out.insert(0, "date", self.timestamps)
        return out
