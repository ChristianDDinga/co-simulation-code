import pandas as pd

df_old = pd.read_csv("data/combined_active_power.csv", index_col=0)
df_new = pd.read_csv("data/combined_profiles_one_year.csv", index_col=0)

print("OLD shape:", df_old.shape)
print("NEW shape:", df_new.shape)

