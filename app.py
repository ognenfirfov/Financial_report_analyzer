import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

def analyze_data(df):
    df['Profit'] = df['Revenue'] - df['Expenses']
    return df

def plot_chart(df):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['Date'], df['Revenue'], label='Revenue', marker='o')
    ax.plot(df['Date'], df['Expenses'], label='Expenses', marker='o')
    ax.plot(df['Date'], df['Profit'], label='Profit', marker='o')
    ax.set_xlabel('Date')
    ax.set_ylabel('Amount ($)')
    ax.set_title('Monthly Financial Overview')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

def generate_pdf(df, chart_path):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Financial Report Summary", ln=True, align='C')

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Total Revenue: ${df['Revenue'].sum():,.2f}", ln=True)
    pdf.cell(200, 10, f"Total Expenses: ${df['Expenses'].sum():,.2f}", ln=True)
    pdf.cell(200, 10, f"Net Profit: ${df['Profit'].sum():,.2f}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Top 5 Profitable Months", ln=True)
    pdf.set_font("Arial", size=11)
    top_months = df.sort_values('Profit', ascending=False).head()
    for _, row in top_months.iterrows():
        date_str = row['Date'].strftime('%Y-%m')
        pdf.cell(200, 8, f"{date_str}: ${row['Profit']:,.2f}", ln=True)

    pdf.ln(5)
    if os.path.exists(chart_path):
        pdf.image(chart_path, w=180)

    output_path = os.path.join(tempfile.gettempdir(), "report.pdf")
    pdf.output(output_path)
    return output_path

st.set_page_config(page_title="Financial Report Analyzer", layout="centered")
st.title("📊 Financial Report Analyzer")

uploaded_file = st.file_uploader("Upload your financial report (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        required_cols = {'Date', 'Revenue', 'Expenses'}
        if not required_cols.issubset(df.columns):
            st.error(f"File must contain columns: {required_cols}")
        else:
            df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m')
            df = analyze_data(df)

            st.success("Report successfully analyzed!")
            st.subheader("Summary")
            st.write(f"**Total Revenue:** ${df['Revenue'].sum():,.2f}")
            st.write(f"**Total Expenses:** ${df['Expenses'].sum():,.2f}")
            st.write(f"**Net Profit:** ${df['Profit'].sum():,.2f}")

            st.subheader("📈 Financial Chart")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                chart_path = tmpfile.name
                df_plot = df.copy()
                fig, ax = plt.subplots()
                ax.plot(df_plot['Date'], df_plot['Revenue'], label='Revenue')
                ax.plot(df_plot['Date'], df_plot['Expenses'], label='Expenses')
                ax.plot(df_plot['Date'], df_plot['Profit'], label='Profit')
                ax.legend()
                plt.savefig(chart_path)
                st.pyplot(fig)

            pdf_path = generate_pdf(df, chart_path)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=f,
                    file_name="financial_report_summary.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error processing file: {e}")