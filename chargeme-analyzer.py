import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64

# Set page configuration
st.set_page_config(
    page_title="ChargeME Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define functions
def load_data():
    """Load and preprocess the CSV data"""
    try:
        # Passe diesen Pfad an die tatsächliche Lage deiner Datei an
        df = pd.read_csv('/Users/olivier/Desktop/ChargeME-transactions.csv', delimiter=';', decimal=',')
        
        # Process date columns
        df['Gestartet'] = pd.to_datetime(df['Gestartet'], errors='coerce')
        df['Beendet'] = pd.to_datetime(df['Beendet'], errors='coerce')
        
        # Convert numeric columns
        numeric_cols = ['meterValueStart (kWh)', 'meterValueStop (kWh)', 'Verbrauch (kWh)']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        
        # Convert duration columns to numeric
        duration_cols = ['Ladedauer (in Minuten)', 'paidDuration', 'parkingDuration']
        for col in duration_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Add useful columns
        df['Year'] = df['Gestartet'].dt.year
        df['Month'] = df['Gestartet'].dt.month
        df['Day'] = df['Gestartet'].dt.day
        df['Weekday'] = df['Gestartet'].dt.weekday
        df['Weekday_name'] = df['Gestartet'].dt.day_name()
        df['Hour'] = df['Gestartet'].dt.hour
        df['YearMonth'] = df['Gestartet'].dt.strftime('%Y-%m')
        
        # Calculate charging rate (kWh per hour)
        df['Charging_Hours'] = df['Ladedauer (in Minuten)'] / 60
        df['Charging_Rate_kWh_per_hour'] = df['Verbrauch (kWh)'] / df['Charging_Hours']
        
        # Calculate cost (€0.49 per kWh)
        df['Cost_EUR'] = df['Verbrauch (kWh)'] * 0.49
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def create_monthly_summary(df):
    """Create monthly summary dataframe"""
    monthly = df.groupby('YearMonth').agg({
        'Verbrauch (kWh)': 'sum',
        'Cost_EUR': 'sum',
        'Ladevorgangs-ID': 'count',
        'Ladedauer (in Minuten)': 'sum'
    }).reset_index()
    
    monthly.columns = ['Month', 'Consumption (kWh)', 'Cost (€)', 'Sessions', 'Duration (min)']
    monthly['Duration (hours)'] = monthly['Duration (min)'] / 60
    monthly['Avg kWh per Session'] = monthly['Consumption (kWh)'] / monthly['Sessions']
    monthly['Avg Charging Rate (kWh/h)'] = monthly['Consumption (kWh)'] / monthly['Duration (hours)']
    
    # Sort by Month
    monthly['Month_dt'] = pd.to_datetime(monthly['Month'] + '-01')
    monthly = monthly.sort_values('Month_dt')
    monthly = monthly.drop('Month_dt', axis=1)
    
    return monthly

def create_location_summary(df):
    """Create location summary dataframe"""
    location = df.groupby('Standort').agg({
        'Verbrauch (kWh)': 'sum',
        'Cost_EUR': 'sum',
        'Ladevorgangs-ID': 'count',
        'Ladedauer (in Minuten)': 'sum'
    }).reset_index()
    
    location.columns = ['Location', 'Consumption (kWh)', 'Cost (€)', 'Sessions', 'Duration (min)']
    location['Duration (hours)'] = location['Duration (min)'] / 60
    location['Avg kWh per Session'] = location['Consumption (kWh)'] / location['Sessions']
    location['Avg Charging Rate (kWh/h)'] = location['Consumption (kWh)'] / location['Duration (hours)']
    
    # Sort by consumption
    location = location.sort_values('Consumption (kWh)', ascending=False)
    
    return location

def create_weekday_summary(df):
    """Create weekday summary dataframe"""
    weekday = df.groupby('Weekday_name').agg({
        'Verbrauch (kWh)': 'sum',
        'Cost_EUR': 'sum',
        'Ladevorgangs-ID': 'count'
    }).reset_index()
    
    weekday.columns = ['Day', 'Consumption (kWh)', 'Cost (€)', 'Sessions']
    weekday['Avg kWh per Session'] = weekday['Consumption (kWh)'] / weekday['Sessions']
    
    # Define correct weekday order
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday['Day_order'] = weekday['Day'].map(lambda x: weekday_order.index(x))
    weekday = weekday.sort_values('Day_order')
    weekday = weekday.drop('Day_order', axis=1)
    
    return weekday

def plot_monthly_consumption(monthly_df, last_n_months=12):
    """Plot monthly consumption with cost overlay"""
    # Get the last N months
    df_plot = monthly_df.iloc[-last_n_months:].copy()
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add consumption bars
    fig.add_trace(
        go.Bar(
            x=df_plot['Month'], 
            y=df_plot['Consumption (kWh)'],
            name='Consumption (kWh)',
            marker_color='#1F77B4'
        )
    )
    
    # Add cost line
    fig.add_trace(
        go.Scatter(
            x=df_plot['Month'], 
            y=df_plot['Cost (€)'],
            name='Cost (€)',
            mode='lines+markers',
            marker=dict(size=8, color='#FF7F0E'),
            line=dict(width=3),
            yaxis='y2'
        )
    )
    
    # Update layout with secondary y-axis
    fig.update_layout(
        title='Monthly Consumption and Cost',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Consumption (kWh)', side='left', showgrid=False),
        yaxis2=dict(title='Cost (€)', side='right', overlaying='y', showgrid=False),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def plot_weekday_distribution(weekday_df):
    """Plot charging sessions by weekday"""
    fig = px.bar(
        weekday_df, 
        x='Day', 
        y='Sessions',
        color='Consumption (kWh)',
        color_continuous_scale='Blues',
        labels={'Sessions': 'Number of Charging Sessions'},
        text_auto=True
    )
    
    fig.update_layout(
        title='Charging Sessions by Day of Week',
        xaxis_title='',
        yaxis_title='Number of Sessions',
        coloraxis_colorbar=dict(title='Total kWh'),
        height=500
    )
    
    return fig

def plot_hourly_distribution(df):
    """Plot charging start times by hour of day"""
    hourly_counts = df.groupby('Hour').size().reset_index(name='Sessions')
    
    fig = px.bar(
        hourly_counts, 
        x='Hour', 
        y='Sessions',
        labels={'Hour': 'Hour of Day (0-23)', 'Sessions': 'Number of Charging Sessions'},
        text_auto=True
    )
    
    fig.update_layout(
        title='Charging Start Times by Hour of Day',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        height=450
    )
    
    return fig

def download_link(df, filename, link_text):
    """Generate a download link for a dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

# Main app
def main():
    st.title("⚡ ChargeME Analyzer")
    st.markdown("### Analyse und Visualisierung der Ladedaten")
    
    # Load data
    df = load_data()
    
    if df is not None:
        # Create summary dataframes
        monthly_df = create_monthly_summary(df)
        location_df = create_location_summary(df)
        weekday_df = create_weekday_summary(df)
        
        # Key metrics
        total_consumption = df['Verbrauch (kWh)'].sum()
        total_cost = df['Cost_EUR'].sum()
        total_sessions = len(df)
        avg_consumption = total_consumption / total_sessions
        total_duration_hours = df['Ladedauer (in Minuten)'].sum() / 60
        avg_rate = total_consumption / total_duration_hours if total_duration_hours > 0 else 0
        
        # Dashboard layout
        st.markdown("## 📊 Dashboard")
        
        # Row 1 - Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Gesamtverbrauch", f"{total_consumption:.2f} kWh")
        with col2:
            st.metric("Gesamtkosten", f"€{total_cost:.2f}")
        with col3:
            st.metric("Ladevorgänge", f"{total_sessions}")
        with col4:
            st.metric("Durchschnitt", f"{avg_consumption:.2f} kWh/Ladung")
        
        # Row 2 - More metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Durchschnittl. Rate", f"{avg_rate:.2f} kWh/h")
        with col2:
            first_date = df['Gestartet'].min().strftime('%d.%m.%Y')
            last_date = df['Gestartet'].max().strftime('%d.%m.%Y')
            st.metric("Zeitraum", f"{first_date} - {last_date}")
        with col3:
            st.metric("Ladedauer gesamt", f"{total_duration_hours:.1f} Stunden")
        with col4:
            cost_per_kwh = 0.49
            st.metric("Strompreis", f"€{cost_per_kwh:.2f}/kWh")
        
        # Row 3 - Monthly chart
        st.plotly_chart(plot_monthly_consumption(monthly_df), use_container_width=True)
        
        # Row 4 - Two charts side by side
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(plot_weekday_distribution(weekday_df), use_container_width=True)
        with col2:
            st.plotly_chart(plot_hourly_distribution(df), use_container_width=True)
        
        # Detailed data tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Monatliche Übersicht", "Standorte", "Einzelne Ladevorgänge", "Analyse"])
        
        # Monthly overview tab
        with tab1:
            st.subheader("Monatliche Übersicht")
            st.dataframe(monthly_df.style.format({
                'Consumption (kWh)': '{:.2f}',
                'Cost (€)': '{:.2f}',
                'Duration (hours)': '{:.1f}',
                'Avg kWh per Session': '{:.2f}',
                'Avg Charging Rate (kWh/h)': '{:.2f}'
            }), use_container_width=True)
            
            st.markdown(download_link(monthly_df, "monthly_charging_data.csv", "📥 Monatliche Daten herunterladen"), unsafe_allow_html=True)
        
        # Locations tab
        with tab2:
            st.subheader("Ladungen nach Standort")
            st.dataframe(location_df.style.format({
                'Consumption (kWh)': '{:.2f}',
                'Cost (€)': '{:.2f}',
                'Duration (hours)': '{:.1f}',
                'Avg kWh per Session': '{:.2f}',
                'Avg Charging Rate (kWh/h)': '{:.2f}'
            }), use_container_width=True)
            
            st.markdown(download_link(location_df, "location_charging_data.csv", "📥 Standort-Daten herunterladen"), unsafe_allow_html=True)
        
        # Individual sessions tab
        with tab3:
            st.subheader("Einzelne Ladevorgänge")
            
            # Date range filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Von Datum", df['Gestartet'].min().date())
            with col2:
                end_date = st.date_input("Bis Datum", df['Gestartet'].max().date())
            
            # Filter data by date range
            filtered_df = df[(df['Gestartet'].dt.date >= start_date) & 
                             (df['Gestartet'].dt.date <= end_date)]
            
            # Display filtered data
            st.dataframe(filtered_df[['Gestartet', 'Beendet', 'Standort', 
                                     'Verbrauch (kWh)', 'Cost_EUR', 'Ladedauer (in Minuten)']].sort_values('Gestartet', ascending=False)
                        .rename(columns={'Verbrauch (kWh)': 'Verbrauch (kWh)', 
                                        'Cost_EUR': 'Kosten (€)', 
                                        'Ladedauer (in Minuten)': 'Dauer (Min)'})
                        .style.format({
                            'Verbrauch (kWh)': '{:.2f}',
                            'Kosten (€)': '{:.2f}'
                        }), use_container_width=True)
            
            st.markdown(download_link(filtered_df, "filtered_charging_data.csv", 
                                     "📥 Gefilterte Daten herunterladen"), unsafe_allow_html=True)
        
        # Analysis tab
        with tab4:
            st.subheader("Erweiterte Analyse")
            
            # Charging rate analysis
            st.write("### Ladegeschwindigkeit")
            
            # Remove outliers for valid analysis
            df_rate = df[(df['Charging_Rate_kWh_per_hour'] > 0) & 
                         (df['Charging_Rate_kWh_per_hour'] < 50)]  # Remove extreme outliers
            
            # Plot charging rate histogram
            fig = px.histogram(
                df_rate, 
                x='Charging_Rate_kWh_per_hour',
                nbins=30,
                labels={'Charging_Rate_kWh_per_hour': 'Charging Rate (kWh/hour)'},
                title='Distribution of Charging Rates'
            )
            
            fig.update_layout(
                xaxis_title='Charging Rate (kWh/hour)',
                yaxis_title='Count',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Charging efficiency metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Durchschnittliche Ladegeschwindigkeit", 
                          f"{df_rate['Charging_Rate_kWh_per_hour'].mean():.2f} kWh/h")
            with col2:
                st.metric("Median Ladegeschwindigkeit", 
                          f"{df_rate['Charging_Rate_kWh_per_hour'].median():.2f} kWh/h")
            
            # Charging duration vs consumption scatter plot
            st.write("### Ladedauer vs. Verbrauch")
            
            fig = px.scatter(
                df, 
                x='Ladedauer (in Minuten)', 
                y='Verbrauch (kWh)',
                color='Charging_Rate_kWh_per_hour',
                color_continuous_scale='Viridis',
                labels={
                    'Ladedauer (in Minuten)': 'Charging Duration (minutes)',
                    'Verbrauch (kWh)': 'Consumption (kWh)',
                    'Charging_Rate_kWh_per_hour': 'Charging Rate (kWh/h)'
                },
                title='Charging Duration vs. Consumption'
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("Keine Daten gefunden. Bitte stelle sicher, dass die Datei 'ChargeMEtransactions.csv' vorhanden ist.")

# Run the app
if __name__ == "__main__":
    main()