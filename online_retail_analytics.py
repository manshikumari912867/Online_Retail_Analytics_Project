import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set style for matplotlib charts
plt.style.use('ggplot')
plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

DATA_PATH = r"C:\Users\manuk\OneDrive\Documents\Online Retail Data Set (1).xlsx"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_OUTPUT = os.path.join(OUTPUT_DIR, "Online_Retail_Executive_Analytics.xlsx")
CSV_OUTPUT = os.path.join(OUTPUT_DIR, "Online_Retail_Cleaned_Data.csv")
STATIC_IMG_DIR = os.path.join(OUTPUT_DIR, "static", "images")
os.makedirs(STATIC_IMG_DIR, exist_ok=True)

def run_analytics():
    print("Step 1: Loading raw dataset...")
    df = pd.read_excel(DATA_PATH, sheet_name='Online Retail')
    print(f"Raw shape: {df.shape}")

    print("\nStep 2: Cleaning dataset according to CEO/CMO rules...")
    # Clean checks: Quantity >= 1 and UnitPrice > 0
    df_clean = df[(df['Quantity'] >= 1) & (df['UnitPrice'] > 0)].copy()
    
    # Revenue calculated field
    df_clean['Revenue'] = df_clean['Quantity'] * df_clean['UnitPrice']
    
    # Date processing
    df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
    df_clean['Year'] = df_clean['InvoiceDate'].dt.year
    df_clean['Month'] = df_clean['InvoiceDate'].dt.month
    df_clean['YearMonth'] = df_clean['InvoiceDate'].dt.to_period('M')
    df_clean['MonthName'] = df_clean['InvoiceDate'].dt.strftime('%b %Y')
    df_clean['MonthShort'] = df_clean['InvoiceDate'].dt.strftime('%b')

    print(f"Cleaned shape: {df_clean.shape} ({len(df) - len(df_clean)} bad/cancelled rows removed)")
    print(f"Total Clean Revenue: £{df_clean['Revenue'].sum():,.2f}")

    # ==========================================
    # Question 1: CEO Monthly Revenue Trend (2011)
    # ==========================================
    print("\nProcessing Question 1: 2011 Monthly Revenue Trend...")
    df_2011 = df_clean[df_clean['Year'] == 2011].copy()
    q1_summary = df_2011.groupby(['Month', 'MonthShort'])['Revenue'].sum().reset_index()
    q1_summary.sort_values('Month', inplace=True)
    q1_summary['Revenue_Formatted'] = q1_summary['Revenue'].apply(lambda x: f"£{x:,.2f}")
    print(q1_summary[['MonthShort', 'Revenue_Formatted']])

    # Q1 Chart
    plt.figure(figsize=(10, 5), dpi=300)
    plt.plot(q1_summary['MonthShort'], q1_summary['Revenue']/1e6, marker='o', color='#2563eb', linewidth=2.5, markersize=8)
    plt.fill_between(q1_summary['MonthShort'], q1_summary['Revenue']/1e6, color='#2563eb', alpha=0.15)
    plt.title('Question 1: 2011 Monthly Revenue Trend (£ Millions)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Month (2011)', fontsize=11)
    plt.ylabel('Revenue (£ Millions)', fontsize=11)
    for i, txt in enumerate(q1_summary['Revenue']):
        plt.annotate(f"£{txt/1e6:.2f}M", (q1_summary['MonthShort'].iloc[i], txt/1e6 + 0.03), 
                     ha='center', fontsize=9, fontweight='bold', color='#1e3a8a')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    q1_chart_path = os.path.join(STATIC_IMG_DIR, "q1_monthly_revenue_2011.png")
    plt.savefig(q1_chart_path)
    plt.close()

    # ==========================================
    # Question 2: CMO Top 10 Countries (Excl. UK)
    # ==========================================
    print("\nProcessing Question 2: Top 10 Countries by Revenue (Excluding UK)...")
    df_ex_uk = df_clean[df_clean['Country'] != 'United Kingdom'].copy()
    q2_group = df_ex_uk.groupby('Country').agg({
        'Revenue': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    
    q2_top10 = q2_group.sort_values(by='Revenue', ascending=False).head(10).reset_index(drop=True)
    q2_top10['Revenue_Formatted'] = q2_top10['Revenue'].apply(lambda x: f"£{x:,.2f}")
    q2_top10['Quantity_Formatted'] = q2_top10['Quantity'].apply(lambda x: f"{x:,}")
    print(q2_top10[['Country', 'Revenue_Formatted', 'Quantity_Formatted']])

    # Q2 Chart: Clustered / Side-by-Side Bar Chart
    plt.figure(figsize=(12, 6), dpi=300)
    x = np.arange(len(q2_top10))
    width = 0.38

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
    ax2 = ax1.twinx()

    rects1 = ax1.bar(x - width/2, q2_top10['Revenue']/1000, width, label='Revenue (£k)', color='#2563eb')
    rects2 = ax2.bar(x + width/2, q2_top10['Quantity']/1000, width, label='Quantity Sold (k Units)', color='#10b981')

    ax1.set_xlabel('Country', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Revenue (£ Thousands)', color='#2563eb', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Quantity Sold (Thousands of Units)', color='#10b981', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(q2_top10['Country'], rotation=30, ha='right', fontsize=10)
    plt.title('Question 2: Top 10 International Markets - Revenue & Quantity Sold (Excl. UK)', fontsize=13, fontweight='bold', pad=15)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    plt.tight_layout()
    q2_chart_path = os.path.join(STATIC_IMG_DIR, "q2_top10_countries.png")
    plt.savefig(q2_chart_path)
    plt.close()

    # ==========================================
    # Question 3: CMO Top 10 Customers (Excl. Null CustomerID)
    # ==========================================
    print("\nProcessing Question 3: Top 10 Customers by Revenue (Excluding Nulls)...")
    df_cust = df_clean.dropna(subset=['CustomerID']).copy()
    df_cust['CustomerID'] = df_cust['CustomerID'].astype(int).astype(str)

    q3_group = df_cust.groupby('CustomerID').agg({
        'Revenue': 'sum',
        'InvoiceNo': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    q3_group.rename(columns={'InvoiceNo': 'TotalOrders'}, inplace=True)
    
    q3_top10 = q3_group.sort_values(by='Revenue', ascending=False).head(10).reset_index(drop=True)
    q3_top10['CustomerRank'] = [f"#{i+1} (ID: {cid})" for i, cid in enumerate(q3_top10['CustomerID'])]
    q3_top10['Revenue_Formatted'] = q3_top10['Revenue'].apply(lambda x: f"£{x:,.2f}")
    print(q3_top10[['CustomerRank', 'CustomerID', 'Revenue_Formatted', 'TotalOrders']])

    # Q3 Chart: Vertical Column Plot sorted descending
    plt.figure(figsize=(11, 5.5), dpi=300)
    bars = plt.bar(q3_top10['CustomerID'], q3_top10['Revenue']/1000, color='#8b5cf6', width=0.6)
    plt.title('Question 3: Top 10 Customers by Revenue (Descending Order)', fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Customer ID', fontsize=11, fontweight='bold')
    plt.ylabel('Total Revenue (£ Thousands)', fontsize=11, fontweight='bold')
    plt.xticks(rotation=0, fontsize=10)
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f"£{height:.1f}k",
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=9, fontweight='bold', color='#4c1d95')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    q3_chart_path = os.path.join(STATIC_IMG_DIR, "q3_top10_customers.png")
    plt.savefig(q3_chart_path)
    plt.close()

    # ==========================================
    # Question 4: CEO Global Demand Map Data (Excl. UK)
    # ==========================================
    print("\nProcessing Question 4: Global Product Demand by Country (Excluding UK)...")
    q4_group = df_ex_uk.groupby('Country').agg({
        'Quantity': 'sum',
        'Revenue': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()
    q4_sorted = q4_group.sort_values(by='Quantity', ascending=False).reset_index(drop=True)
    q4_sorted['Revenue_Formatted'] = q4_sorted['Revenue'].apply(lambda x: f"£{x:,.2f}")
    q4_sorted['Quantity_Formatted'] = q4_sorted['Quantity'].apply(lambda x: f"{x:,}")
    print("Top 10 High Demand International Regions:")
    print(q4_sorted[['Country', 'Quantity_Formatted', 'Revenue_Formatted']].head(10))

    # Q4 Chart: Horizontal Bar Chart of Global Demand
    plt.figure(figsize=(10, 8), dpi=300)
    top15_q4 = q4_sorted.head(15).iloc[::-1]
    plt.barh(top15_q4['Country'], top15_q4['Quantity']/1000, color='#06b6d4', height=0.65)
    plt.title('Question 4: International Product Demand - Units Sold (Thousands)', fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Quantity Sold (Thousands of Units)', fontsize=11, fontweight='bold')
    plt.ylabel('Country', fontsize=11, fontweight='bold')
    for i, val in enumerate(top15_q4['Quantity']):
        plt.text(val/1000 + 1, i, f"{val:,.0f}", va='center', fontsize=9, fontweight='bold', color='#0e7490')
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    q4_chart_path = os.path.join(STATIC_IMG_DIR, "q4_global_demand.png")
    plt.savefig(q4_chart_path)
    plt.close()

    # Executive Summary Metrics
    total_rev = df_clean['Revenue'].sum()
    total_orders = df_clean['InvoiceNo'].nunique()
    total_cust = df_cust['CustomerID'].nunique()
    total_units = df_clean['Quantity'].sum()
    aov = total_rev / total_orders

    exec_summary = pd.DataFrame([{
        'Metric': 'Total Valid Revenue (£)',
        'Value': f"£{total_rev:,.2f}"
    }, {
        'Metric': 'Total Valid Orders',
        'Value': f"{total_orders:,}"
    }, {
        'Metric': 'Total Unique Identified Customers',
        'Value': f"{total_cust:,}"
    }, {
        'Metric': 'Total Units Sold',
        'Value': f"{total_units:,}"
    }, {
        'Metric': 'Average Order Value (AOV)',
        'Value': f"£{aov:,.2f}"
    }, {
        'Metric': 'Cleaned Record Count',
        'Value': f"{len(df_clean):,}"
    }, {
        'Metric': 'Removed Bad/Cancelled Records',
        'Value': f"{len(df) - len(df_clean):,}"
    }])

    # Export to Excel with multiple tabs
    print(f"\nWriting deliverables to Multi-Tab Excel Workbook: {EXCEL_OUTPUT}...")
    with pd.ExcelWriter(EXCEL_OUTPUT, engine='openpyxl') as writer:
        exec_summary.to_excel(writer, sheet_name='Executive Summary', index=False)
        q1_summary.to_excel(writer, sheet_name='Question 1 - Monthly 2011', index=False)
        q2_top10.to_excel(writer, sheet_name='Question 2 - Top 10 Countries', index=False)
        q3_top10.to_excel(writer, sheet_name='Question 3 - Top 10 Customers', index=False)
        q4_sorted.to_excel(writer, sheet_name='Question 4 - Global Demand', index=False)

    print(f"Exporting cleaned dataset to CSV: {CSV_OUTPUT}...")
    df_clean[['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country', 'Revenue']].to_csv(CSV_OUTPUT, index=False)
    
    print("\nAnalytics ETL Pipeline completed successfully!")

if __name__ == '__main__':
    run_analytics()
