import os
import pandas as pd
from flask import Flask, render_template, jsonify, send_file, request

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "Online_Retail_Cleaned_Data.csv")
EXCEL_PATH = os.path.join(BASE_DIR, "Online_Retail_Executive_Analytics.xlsx")

# Load cleaned data in memory for fast API responses
df_clean = pd.read_csv(CSV_PATH, low_memory=False)
df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
df_clean['Year'] = df_clean['InvoiceDate'].dt.year
df_clean['Month'] = df_clean['InvoiceDate'].dt.month
df_clean['MonthShort'] = df_clean['InvoiceDate'].dt.strftime('%b')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/kpis')
def get_kpis():
    total_rev = float(df_clean['Revenue'].sum())
    total_orders = int(df_clean['InvoiceNo'].nunique())
    df_cust = df_clean.dropna(subset=['CustomerID'])
    total_cust = int(df_cust['CustomerID'].nunique())
    total_units = int(df_clean['Quantity'].sum())
    aov = total_rev / total_orders if total_orders > 0 else 0

    return jsonify({
        'total_revenue': total_rev,
        'total_orders': total_orders,
        'total_customers': total_cust,
        'total_units': total_units,
        'aov': aov,
        'total_records': len(df_clean)
    })

@app.route('/api/q1-monthly-trend')
def get_q1():
    df_2011 = df_clean[df_clean['Year'] == 2011].copy()
    grouped = df_2011.groupby(['Month', 'MonthShort'])['Revenue'].sum().reset_index()
    grouped.sort_values('Month', inplace=True)
    
    return jsonify({
        'months': grouped['MonthShort'].tolist(),
        'revenue': [round(r, 2) for r in grouped['Revenue'].tolist()]
    })

@app.route('/api/q2-top10-countries')
def get_q2():
    df_ex_uk = df_clean[df_clean['Country'] != 'United Kingdom']
    grouped = df_ex_uk.groupby('Country').agg({
        'Revenue': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    top10 = grouped.sort_values(by='Revenue', ascending=False).head(10)

    return jsonify({
        'countries': top10['Country'].tolist(),
        'revenue': [round(r, 2) for r in top10['Revenue'].tolist()],
        'quantity': [int(q) for q in top10['Quantity'].tolist()]
    })

@app.route('/api/q3-top10-customers')
def get_q3():
    df_cust = df_clean.dropna(subset=['CustomerID']).copy()
    df_cust['CustomerID'] = df_cust['CustomerID'].astype(int).astype(str)
    grouped = df_cust.groupby('CustomerID').agg({
        'Revenue': 'sum',
        'InvoiceNo': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    top10 = grouped.sort_values(by='Revenue', ascending=False).head(10)

    return jsonify({
        'customer_ids': top10['CustomerID'].tolist(),
        'revenue': [round(r, 2) for r in top10['Revenue'].tolist()],
        'orders': top10['InvoiceNo'].tolist(),
        'quantity': top10['Quantity'].tolist()
    })

@app.route('/api/q4-global-map')
def get_q4():
    df_ex_uk = df_clean[df_clean['Country'] != 'United Kingdom']
    grouped = df_ex_uk.groupby('Country').agg({
        'Quantity': 'sum',
        'Revenue': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()
    sorted_df = grouped.sort_values(by='Quantity', ascending=False)

    return jsonify({
        'countries': sorted_df['Country'].tolist(),
        'quantity': sorted_df['Quantity'].tolist(),
        'revenue': [round(r, 2) for r in sorted_df['Revenue'].tolist()],
        'orders': sorted_df['InvoiceNo'].tolist()
    })

@app.route('/download/excel')
def download_excel():
    return send_file(EXCEL_PATH, as_attachment=True, download_name="Online_Retail_Executive_Analytics.xlsx")

@app.route('/download/csv')
def download_csv():
    return send_file(CSV_PATH, as_attachment=True, download_name="Online_Retail_Cleaned_Data.csv")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
