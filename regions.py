import pandas as pd
import json

df = pd.read_csv('/home/ntt/cleandata/cleaned_stackoverflow_2025.csv')
countries = df['Country'].dropna().unique().tolist()
print(f"Total unique countries: {len(countries)}")
