import pandas as pd

# Read the raw passenger data (semicolon separated, wide format)
input_file = '2026csv/farþegar.csv'
df = pd.read_csv(input_file, sep=';', skiprows=2, encoding='utf-8-sig')

# The first column is "Ríkisfang", rest are months like "2002M03"
# Row contains "Útlendingar alls" with passenger counts

# Get the passenger row (Útlendingar alls)
passenger_row = df[df['Ríkisfang'] == 'Útlendingar alls'].iloc[0]

# Extract month columns (all except 'Ríkisfang')
month_columns = [col for col in df.columns if col != 'Ríkisfang']

# Transform from wide to long format
data = []
for month_col in month_columns:
    # Parse year and month from "2012M01" format
    year = int(month_col[:4])
    month = int(month_col[5:7])
    passengers = passenger_row[month_col]

    data.append({
        'year': year,
        'month': month,
        'passengers': passengers
    })

# Create DataFrame
df_clean = pd.DataFrame(data)

# Filter to 2012-2022
df_filtered = df_clean[(df_clean['year'] >= 2012) & (df_clean['year'] <= 2022)]

# Sort by year and month
df_filtered = df_filtered.sort_values(['year', 'month']).reset_index(drop=True)

# Add date column (first day of each month)
df_filtered['date'] = pd.to_datetime(
    df_filtered['year'].astype(str) + '-' +
    df_filtered['month'].astype(str).str.zfill(2) + '-01'
)

# Reorder columns
df_filtered = df_filtered[['year', 'month', 'date', 'passengers']]

# Save to CSV
output_file = '2026csv/passengers_clean.csv'
df_filtered.to_csv(output_file, index=False)

print(f"Clean passenger data saved to '{output_file}'")
print(f"Total rows: {len(df_filtered)}")
print(f"Date range: {df_filtered['year'].min()}-{df_filtered['month'].min():02d} to {df_filtered['year'].max()}-{df_filtered['month'].max():02d}")
print(f"\nFirst 5 rows:")
print(df_filtered.head())
print(f"\nLast 5 rows:")
print(df_filtered.tail())
