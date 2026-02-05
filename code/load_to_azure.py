"""
Load CSV data into Azure SQL Database
- Creates tables
- Loads data from CSV files
- Verifies checksums (row count, sums)
"""

import pyodbc
import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERVER = os.getenv('db_server')
DATABASE = os.getenv('db_name')
USERNAME = os.getenv('db_username')
PASSWORD = os.getenv('db_password')

# Connection string for Azure SQL
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
)

# Expected checksums (calculated from CSV before loading)
EXPECTED = {
    'passengers_rows': 132,
    'passengers_sum': 14790715,
    'weather_rows': 132,
    'weather_temp_sum': 707.50,
    'weather_precip_sum': 10233.90,
}

# SQL statements
SQL_DROP_TABLES = """
-- Drop tables if they exist (for re-running)
IF OBJECT_ID('Passengers', 'U') IS NOT NULL DROP TABLE Passengers;
IF OBJECT_ID('Weather', 'U') IS NOT NULL DROP TABLE Weather;
"""

SQL_CREATE_PASSENGERS = """
CREATE TABLE Passengers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    date DATE NOT NULL,
    passengers INT NOT NULL
);
"""

SQL_CREATE_WEATHER = """
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
"""

SQL_INSERT_PASSENGER = """
INSERT INTO Passengers (year, month, date, passengers)
VALUES (?, ?, ?, ?);
"""

SQL_INSERT_WEATHER = """
INSERT INTO Weather (year, month, date, mean_temp, max_temp, min_temp, precipitation)
VALUES (?, ?, ?, ?, ?, ?, ?);
"""

SQL_VERIFY = """
-- Verification queries
SELECT
    'Passengers' as table_name,
    COUNT(*) as row_count,
    SUM(passengers) as sum_passengers,
    NULL as sum_mean_temp,
    NULL as sum_precipitation
FROM Passengers
UNION ALL
SELECT
    'Weather' as table_name,
    COUNT(*) as row_count,
    NULL as sum_passengers,
    ROUND(SUM(mean_temp), 2) as sum_mean_temp,
    ROUND(SUM(precipitation), 2) as sum_precipitation
FROM Weather;
"""


def main():
    print("=" * 60)
    print("AZURE SQL DATA LOADER")
    print("=" * 60)

    # Show connection info
    print(f"\nConnecting to: {SERVER}")
    print(f"Database: {DATABASE}")
    print(f"User: {USERNAME}")

    # Connect
    print("\n[1/5] Connecting to Azure SQL...")
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connected!")

    # Drop existing tables
    print("\n[2/5] Dropping existing tables (if any)...")
    print("-" * 40)
    print(SQL_DROP_TABLES)
    cursor.execute(SQL_DROP_TABLES)
    conn.commit()
    print("Done!")

    # Create tables
    print("\n[3/5] Creating tables...")
    print("-" * 40)
    print(SQL_CREATE_PASSENGERS)
    cursor.execute(SQL_CREATE_PASSENGERS)
    print(SQL_CREATE_WEATHER)
    cursor.execute(SQL_CREATE_WEATHER)
    conn.commit()
    print("Tables created!")

    # Load Passengers data
    print("\n[4/5] Loading data from CSV files...")
    print("-" * 40)

    csv_dir = os.path.join(os.path.dirname(__file__), '..', '2026csv')

    # Load passengers
    passengers_file = os.path.join(csv_dir, 'passengers_clean.csv')
    print(f"Loading: {passengers_file}")
    with open(passengers_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        for row in rows:
            cursor.execute(SQL_INSERT_PASSENGER,
                int(row['year']),
                int(row['month']),
                row['date'],
                int(row['passengers'])
            )
    conn.commit()
    print(f"  Inserted {len(rows)} rows into Passengers")

    # Load weather
    weather_file = os.path.join(csv_dir, 'weather_clean.csv')
    print(f"Loading: {weather_file}")
    with open(weather_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        for row in rows:
            cursor.execute(SQL_INSERT_WEATHER,
                int(row['year']),
                int(row['month']),
                row['date'],
                float(row['mean_temp']),
                float(row['max_temp']),
                float(row['min_temp']),
                float(row['precipitation'])
            )
    conn.commit()
    print(f"  Inserted {len(rows)} rows into Weather")

    # Verify checksums
    print("\n[5/5] Verifying checksums...")
    print("-" * 40)
    print("SQL Query:")
    print(SQL_VERIFY)

    cursor.execute(SQL_VERIFY)
    results = cursor.fetchall()

    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)

    all_passed = True

    for row in results:
        table_name = row[0]
        row_count = row[1]

        if table_name == 'Passengers':
            sum_passengers = row[2]
            print(f"\n{table_name}:")
            print(f"  Row count:      {row_count:>10} (expected: {EXPECTED['passengers_rows']})")
            print(f"  SUM(passengers): {sum_passengers:>10,} (expected: {EXPECTED['passengers_sum']:,})")

            if row_count != EXPECTED['passengers_rows']:
                print("  ❌ ROW COUNT MISMATCH!")
                all_passed = False
            if sum_passengers != EXPECTED['passengers_sum']:
                print("  ❌ SUM MISMATCH!")
                all_passed = False

        elif table_name == 'Weather':
            sum_temp = row[3]
            sum_precip = row[4]
            print(f"\n{table_name}:")
            print(f"  Row count:         {row_count:>10} (expected: {EXPECTED['weather_rows']})")
            print(f"  SUM(mean_temp):    {sum_temp:>10.2f} (expected: {EXPECTED['weather_temp_sum']:.2f})")
            print(f"  SUM(precipitation): {sum_precip:>10.2f} (expected: {EXPECTED['weather_precip_sum']:.2f})")

            if row_count != EXPECTED['weather_rows']:
                print("  ❌ ROW COUNT MISMATCH!")
                all_passed = False
            if abs(sum_temp - EXPECTED['weather_temp_sum']) > 0.01:
                print("  ❌ TEMP SUM MISMATCH!")
                all_passed = False
            if abs(sum_precip - EXPECTED['weather_precip_sum']) > 0.01:
                print("  ❌ PRECIP SUM MISMATCH!")
                all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL CHECKSUMS PASSED - Data loaded successfully!")
    else:
        print("✗ SOME CHECKSUMS FAILED - Check the data!")
    print("=" * 60)

    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()
