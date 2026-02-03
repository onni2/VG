import pandas as pd

# Read the raw weather data (tab-separated, skip header line)
input_file = 'weather.txt'
df = pd.read_csv(input_file, sep='\t', skiprows=1)

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# Columns: stöð (station), ár (year), mán (month), t (mean temp),
#          tx (max temp), tn (min temp), r (precipitation)

# Filter to 2012-2022
df = df[(df['ár'] >= 2012) & (df['ár'] <= 2022)]

# Select and rename relevant columns
df_clean = df[['ár', 'mán', 't', 'tx', 'tn', 'r']].copy()
df_clean.columns = ['year', 'month', 'mean_temp', 'max_temp', 'min_temp', 'precipitation']

# Sort by year and month
df_clean = df_clean.sort_values(['year', 'month']).reset_index(drop=True)

# Add date column (first day of each month)
df_clean['date'] = pd.to_datetime(
    df_clean['year'].astype(str) + '-' +
    df_clean['month'].astype(str).str.zfill(2) + '-01'
)

# Reorder columns
df_clean = df_clean[['year', 'month', 'date', 'mean_temp', 'max_temp', 'min_temp', 'precipitation']]

# Save to CSV
output_file = '2026csv/weather_clean.csv'
df_clean.to_csv(output_file, index=False)

print(f"Clean weather data saved to '{output_file}'")
print(f"Total rows: {len(df_clean)}")
print(f"Date range: {df_clean['year'].min()}-{df_clean['month'].min():02d} to {df_clean['year'].max()}-{df_clean['month'].max():02d}")
print(f"\nFirst 5 rows:")
print(df_clean.head())
print(f"\nLast 5 rows:")
print(df_clean.tail())
