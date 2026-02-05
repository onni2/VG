import pandas as pd
import pyodbc
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get connection details
db_username = os.getenv('db_username')
db_password = os.getenv('db_password')
db_server = os.getenv('db_server')
db_name = os.getenv('db_name')

# Read CSV files
df_passengers = pd.read_csv('../2026csv/passengers_clean.csv')
df_weather = pd.read_csv('../2026csv/weather_clean.csv')

# Calculate checksums BEFORE loading
print("=== CHECKSUMS BEFORE (from CSV) ===")
print(f"Passengers rows: {len(df_passengers)}")
print(f"Passengers SUM: {df_passengers['passengers'].sum():,}")
print(f"Weather rows: {len(df_weather)}")
print(f"Weather temp SUM: {df_weather['mean_temp'].sum():.2f}")
print(f"Weather precip SUM: {df_weather['precipitation'].sum():.2f}")
print()

# Connect to Azure SQL
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={db_server};"
    f"DATABASE={db_name};"
    f"UID={db_username};"
    f"PWD={db_password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
)

print(f"Connecting to {db_server}...")
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
print("Connected!")

# Create tables (drop if exist)
print("\nCreating tables...")
cursor.execute("IF OBJECT_ID('Passengers', 'U') IS NOT NULL DROP TABLE Passengers;")
cursor.execute("IF OBJECT_ID('Weather', 'U') IS NOT NULL DROP TABLE Weather;")

cursor.execute("""
CREATE TABLE Passengers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    date DATE NOT NULL,
    passengers INT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE Weather (
    id INT IDENTITY(1,1) PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    date DATE NOT NULL,
    mean_temp FLOAT,
    max_temp FLOAT,
    min_temp FLOAT,
    precipitation FLOAT
);
""")
conn.commit()
print("Tables created!")

# Insert data
print("\nLoading Passengers data...")
for _, row in df_passengers.iterrows():
    cursor.execute(
        "INSERT INTO Passengers (year, month, date, passengers) VALUES (?, ?, ?, ?)",
        int(row['year']), int(row['month']), row['date'], int(row['passengers'])
    )
conn.commit()
print(f"  Inserted {len(df_passengers)} rows")

print("Loading Weather data...")
for _, row in df_weather.iterrows():
    cursor.execute(
        "INSERT INTO Weather (year, month, date, mean_temp, max_temp, min_temp, precipitation) VALUES (?, ?, ?, ?, ?, ?, ?)",
        int(row['year']), int(row['month']), row['date'],
        float(row['mean_temp']), float(row['max_temp']), float(row['min_temp']), float(row['precipitation'])
    )
conn.commit()
print(f"  Inserted {len(df_weather)} rows")

# Verify checksums AFTER loading
print("\n=== CHECKSUMS AFTER (from database) ===")
cursor.execute("SELECT COUNT(*), SUM(passengers) FROM Passengers")
p_count, p_sum = cursor.fetchone()
print(f"Passengers rows: {p_count}")
print(f"Passengers SUM: {p_sum:,}")

cursor.execute("SELECT COUNT(*), ROUND(SUM(mean_temp), 2), ROUND(SUM(precipitation), 2) FROM Weather")
w_count, w_temp, w_precip = cursor.fetchone()
print(f"Weather rows: {w_count}")
print(f"Weather temp SUM: {w_temp}")
print(f"Weather precip SUM: {w_precip}")

# Close connection
cursor.close()
conn.close()
print("\nDone!")




