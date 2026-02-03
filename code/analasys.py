# analysis script for tourism and weather data
# hopverkefni 1

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

plt.rcParams['figure.figsize'] = (12, 8)

print("WEATHER IMPACT ON TOURISM IN ICELAND")
print("=====================================")

# load data
passengers = pd.read_csv('../2026csv/passengers_clean.csv')
weather = pd.read_csv('../2026csv/weather_clean.csv')

# merge on year and month
df = pd.merge(passengers, weather, on=['year', 'month', 'date'])
df['date'] = pd.to_datetime(df['date'])

print("\nDataset info:")
print("Total months: " + str(len(df)))
print("From " + str(df['date'].min()) + " to " + str(df['date'].max()))

# basic stats
print("\nPassenger stats:")
print("Mean: " + str(round(df['passengers'].mean())))
print("Min: " + str(df['passengers'].min()))
print("Max: " + str(df['passengers'].max()))

print("\nWeather stats:")
print("Mean temp: " + str(round(df['mean_temp'].mean(), 1)) + " C")
print("Mean precipitation: " + str(round(df['precipitation'].mean(), 1)) + " mm")

# 1. time series plot
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

axes[0].plot(df['date'], df['passengers'], linewidth=2, color='steelblue')
axes[0].set_title('Tourist Arrivals in Iceland (2012-2022)')
axes[0].set_ylabel('Number of Passengers')
axes[0].grid(True)

ax2 = axes[1]
ax2.plot(df['date'], df['mean_temp'], label='Mean Temperature', linewidth=2, color='orangered')
ax2.set_ylabel('Temperature (C)')

ax3 = ax2.twinx()
ax3.bar(df['date'], df['precipitation'], alpha=0.3, color='steelblue', width=20)
ax3.set_ylabel('Precipitation (mm)')

axes[1].set_title('Weather in Iceland (2012-2022)')
axes[1].set_xlabel('Date')
axes[1].grid(True)

plt.tight_layout()
plt.savefig('1_time_series.png', dpi=300)
print("\nSaved: 1_time_series.png")
plt.close()

# 2. seasonal analysis
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

df['season'] = df['month'].apply(get_season)

monthly_avg = df.groupby('month').agg({
    'passengers': 'mean',
    'mean_temp': 'mean',
    'precipitation': 'mean'
}).reset_index()

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

axes[0, 0].bar(monthly_avg['month'], monthly_avg['passengers'], color='steelblue')
axes[0, 0].set_title('Average Monthly Tourist Arrivals')
axes[0, 0].set_xlabel('Month')
axes[0, 0].set_ylabel('Passengers')

axes[0, 1].plot(monthly_avg['month'], monthly_avg['mean_temp'], marker='o', color='orangered')
axes[0, 1].set_title('Average Monthly Temperature')
axes[0, 1].set_xlabel('Month')
axes[0, 1].set_ylabel('Temperature (C)')
axes[0, 1].grid(True)

seasonal_avg = df.groupby('season').agg({
    'passengers': 'mean',
    'mean_temp': 'mean'
}).reindex(['Winter', 'Spring', 'Summer', 'Fall'])

axes[1, 0].bar(seasonal_avg.index, seasonal_avg['passengers'], color=['lightblue', 'lightgreen', 'gold', 'orange'])
axes[1, 0].set_title('Average Seasonal Tourist Arrivals')
axes[1, 0].set_ylabel('Passengers')

axes[1, 1].bar(seasonal_avg.index, seasonal_avg['mean_temp'], color=['lightblue', 'lightgreen', 'gold', 'orange'])
axes[1, 1].set_title('Average Seasonal Temperature')
axes[1, 1].set_ylabel('Temperature (C)')

plt.tight_layout()
plt.savefig('2_seasonal_patterns.png', dpi=300)
print("Saved: 2_seasonal_patterns.png")
plt.close()

print("\nSeasonal averages:")
for season in ['Winter', 'Spring', 'Summer', 'Fall']:
    s = df[df['season'] == season]
    print(season + ": " + str(round(s['passengers'].mean())) + " passengers, " + str(round(s['mean_temp'].mean(), 1)) + " C")

# 3. correlation
weather_vars = ['mean_temp', 'max_temp', 'min_temp', 'precipitation']
correlation_data = df[['passengers'] + weather_vars]
correlations = correlation_data.corr()['passengers'].drop('passengers')

print("\n\nCorrelations with passengers:")
for var in weather_vars:
    print(var + ": " + str(round(correlations[var], 3)))

# heatmap
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_data.corr(), annot=True, fmt='.3f', cmap='coolwarm', center=0)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig('3_correlation_heatmap.png', dpi=300)
print("\nSaved: 3_correlation_heatmap.png")
plt.close()

# 4. scatter plots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# temp vs passengers
axes[0, 0].scatter(df['mean_temp'], df['passengers'], alpha=0.6)
axes[0, 0].set_xlabel('Mean Temperature (C)')
axes[0, 0].set_ylabel('Passengers')
axes[0, 0].set_title('Temperature vs Tourism (r=' + str(round(correlations["mean_temp"], 3)) + ')')
z = np.polyfit(df['mean_temp'], df['passengers'], 1)
p = np.poly1d(z)
axes[0, 0].plot(df['mean_temp'], p(df['mean_temp']), "r--", linewidth=2)

# precip vs passengers
axes[0, 1].scatter(df['precipitation'], df['passengers'], alpha=0.6)
axes[0, 1].set_xlabel('Precipitation (mm)')
axes[0, 1].set_ylabel('Passengers')
axes[0, 1].set_title('Precipitation vs Tourism (r=' + str(round(correlations["precipitation"], 3)) + ')')
z = np.polyfit(df['precipitation'], df['passengers'], 1)
p = np.poly1d(z)
axes[0, 1].plot(df['precipitation'], p(df['precipitation']), "r--", linewidth=2)

# max temp
axes[1, 0].scatter(df['max_temp'], df['passengers'], alpha=0.6)
axes[1, 0].set_xlabel('Max Temperature (C)')
axes[1, 0].set_ylabel('Passengers')
axes[1, 0].set_title('Max Temp vs Tourism (r=' + str(round(correlations["max_temp"], 3)) + ')')
z = np.polyfit(df['max_temp'], df['passengers'], 1)
p = np.poly1d(z)
axes[1, 0].plot(df['max_temp'], p(df['max_temp']), "r--", linewidth=2)

# min temp
axes[1, 1].scatter(df['min_temp'], df['passengers'], alpha=0.6)
axes[1, 1].set_xlabel('Min Temperature (C)')
axes[1, 1].set_ylabel('Passengers')
axes[1, 1].set_title('Min Temp vs Tourism (r=' + str(round(correlations["min_temp"], 3)) + ')')
z = np.polyfit(df['min_temp'], df['passengers'], 1)
p = np.poly1d(z)
axes[1, 1].plot(df['min_temp'], p(df['min_temp']), "r--", linewidth=2)

plt.tight_layout()
plt.savefig('4_scatter_plots.png', dpi=300)
print("Saved: 4_scatter_plots.png")
plt.close()

# 5. statistical tests
print("\n\nStatistical tests (Pearson):")
for var in weather_vars:
    r, p_value = stats.pearsonr(df[var], df['passengers'])
    print(var + ": r=" + str(round(r, 3)) + ", p=" + str(round(p_value, 4)))

# 6. regression
X = df[weather_vars].values
y = df['passengers'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = LinearRegression()
model.fit(X_scaled, y)

y_pred = model.predict(X_scaled)
r2 = model.score(X_scaled, y)

# adjusted r2
n = len(y)
p = len(weather_vars)
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)

print("\n\nRegression results:")
print("R2: " + str(round(r2, 4)))
print("Adjusted R2: " + str(round(adj_r2, 4)))
print("RMSE: " + str(round(np.sqrt(np.mean((y - y_pred)**2)))))

print("\nCoefficients:")
for i in range(len(weather_vars)):
    print(weather_vars[i] + ": " + str(round(model.coef_[i])))

# regression plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].scatter(y, y_pred, alpha=0.6)
axes[0].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
axes[0].set_xlabel('Actual Passengers')
axes[0].set_ylabel('Predicted Passengers')
axes[0].set_title('Actual vs Predicted (R2=' + str(round(r2, 3)) + ')')
axes[0].grid(True)

residuals = y - y_pred
axes[1].scatter(y_pred, residuals, alpha=0.6)
axes[1].axhline(y=0, color='r', linestyle='--')
axes[1].set_xlabel('Predicted Passengers')
axes[1].set_ylabel('Residuals')
axes[1].set_title('Residual Plot')
axes[1].grid(True)

plt.tight_layout()
plt.savefig('5_regression_analysis.png', dpi=300)
print("\nSaved: 5_regression_analysis.png")
plt.close()

# 7. monthly breakdown
print("\n\nMonthly analysis:")
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for month in range(1, 13):
    month_data = df[df['month'] == month]
    if len(month_data) > 2:
        corr, _ = stats.pearsonr(month_data['mean_temp'], month_data['passengers'])
        print(months[month-1] + ": avg passengers=" + str(round(month_data['passengers'].mean())) + ", avg temp=" + str(round(month_data['mean_temp'].mean(), 1)) + ", corr=" + str(round(corr, 3)))

# 8. yearly stats
print("\n\nYearly totals:")
yearly = df.groupby('year').agg({'passengers': 'sum', 'mean_temp': 'mean'})
for year in yearly.index:
    print(str(year) + ": " + str(yearly.loc[year, 'passengers']) + " passengers, avg temp " + str(round(yearly.loc[year, 'mean_temp'], 1)) + " C")

# summary
print("\n\n========== SUMMARY ==========")
print("\nMain findings:")
print("1. Temperature correlation: " + str(round(correlations['mean_temp'], 3)))
print("2. Precipitation correlation: " + str(round(correlations['precipitation'], 3)))

summer = df[df['season'] == 'Summer']['passengers'].mean()
winter = df[df['season'] == 'Winter']['passengers'].mean()
print("3. Summer has " + str(round(summer/winter, 1)) + "x more tourists than winter")
print("4. Weather explains " + str(round(r2*100, 1)) + "% of tourism variation")

print("\nConclusion:")
if correlations['mean_temp'] > 0.5:
    print("Weather has a significant effect on tourism in Iceland.")
    print("Warmer temperatures = more tourists")
elif correlations['mean_temp'] > 0.3:
    print("Weather has a moderate effect on tourism.")
else:
    print("Weather has a weak direct effect on tourism.")

print("\nDone!")
