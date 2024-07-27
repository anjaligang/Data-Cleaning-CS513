#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd


# In[4]:



dish_df = pd.read_csv('Main_project/NYPL-menus_clean/Dish1.csv')
menu_df = pd.read_csv('Main_project/NYPL-menus_clean/Menu-csv.csv')
item_df = pd.read_csv('Main_project/NYPL-menus_clean/MenuItem-csv.csv')
page_df = pd.read_csv('Main_project/NYPL-menus_clean/MenuPage-csv.csv')


# ## Historical Trend analysis after cleaning of NYPL data set.

# In[5]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def clean_and_analyze_pricing_trends(menu_df, dish_df, menu_item_df, menu_page_df):
    # 1. Merge relevant dataframes
    merged_df = pd.merge(menu_item_df, menu_page_df[['id', 'menu_id']], left_on='menu_page_id', right_on='id')
    merged_df = pd.merge(merged_df, menu_df[['id', 'date', 'currency', 'currency_symbol']], left_on='menu_id', right_on='id')
    merged_df = pd.merge(merged_df, dish_df[['id', 'name']], left_on='dish_id', right_on='id')

    # 2. Clean and convert dates
    merged_df['date'] = pd.to_datetime(merged_df['date'], errors='coerce')
    merged_df = merged_df.dropna(subset=['date'])

    # 3. Handle price data
    # Use 'high_price' if available, otherwise use 'price'
    merged_df['final_price'] = merged_df['high_price'].fillna(merged_df['price'])
    merged_df = merged_df.dropna(subset=['final_price'])

    # 4. Handle currency conversion (simplified example)
    # In a real scenario, you'd need historical exchange rates
    currency_conversion = {'$': 1, '£': 1.25, '€': 1.1}  # Simplified conversion rates
    merged_df['price_usd'] = merged_df.apply(lambda row: row['final_price'] * currency_conversion.get(row['currency_symbol'], 1), axis=1)

    # 5. Remove outliers
    merged_df = merged_df[merged_df['price_usd'] < merged_df['price_usd'].quantile(0.99)]

    # 6. Adjust for inflation (simplified)
    # In a real scenario, you'd use actual inflation data
    current_year = merged_df['date'].max().year
    merged_df['inflation_factor'] = (current_year - merged_df['date'].dt.year) * 0.02 + 1  # Assume 2% annual inflation
    merged_df['price_adjusted'] = merged_df['price_usd'] * merged_df['inflation_factor']

    # 7. Group by year and calculate average price
    yearly_prices = merged_df.groupby(merged_df['date'].dt.year)['price_adjusted'].mean().reset_index()

    # 8. Analyze trends
    slope, intercept, r_value, p_value, std_err = stats.linregress(yearly_prices['date'], yearly_prices['price_adjusted'])

    # 9. Visualize results
    plt.figure(figsize=(12, 6))
    plt.scatter(yearly_prices['date'], yearly_prices['price_adjusted'], alpha=0.5)
    plt.plot(yearly_prices['date'], intercept + slope * yearly_prices['date'], color='red', label='Trend line')
    plt.title('Historical Pricing Trends of Dishes')
    plt.xlabel('Year')
    plt.ylabel('Average Price (Adjusted for Inflation)')
    plt.legend()
    plt.show()

    print(f"Trend analysis:")
    print(f"Slope: {slope:.4f}")
    print(f"R-squared: {r_value**2:.4f}")
    print(f"P-value: {p_value:.4f}")

    return merged_df, yearly_prices

# Assuming you have already loaded your dataframes
# menu_df, dish_df, menu_item_df, menu_page_df

# Run the analysis
cleaned_data, trend_data = clean_and_analyze_pricing_trends(menu_df, dish_df, item_df, page_df)

