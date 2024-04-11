import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Uber pickups in NYC",
    page_icon=":car:",
    layout="wide"

)

def load_data(nrows=100):
    return (
    pd.read_csv("https://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz", nrows=nrows)
    .rename(columns=lambda x: x.lower())
    .assign(
        datetime=lambda df: pd.to_datetime(df["date/time"]),
        weekday=lambda df: df.datetime.dt.day_name())
    )


with st.sidebar:
    st.image("https://www.cidaen.es/assets/img/cidaen.png", use_column_width=True)

    nrows_selected = st.slider("Número de filas", 0, 100000, 10000, step=1000)

    df = load_data(nrows_selected)
    
    weekday_selected = st.selectbox("Día de la semana", options=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    hour_selected = st.slider("Hora", 0, 23, 12)

st.title("Uber pickups en NYC")

checkbox = st.checkbox("Show raw data")

if checkbox:
    st.markdown("## Raw Data")
    st.dataframe(df.head(5))


col1, col2 = st.columns(2)

with col1:

    mean_pickups_weekday_selected = (
        df
        .loc[lambda df: df.weekday == weekday_selected]
        .assign(
            date=lambda df: df.datetime.dt.date
        )
        .groupby("date")
        .agg(
            total_pickups=('base', 'count')
        )
        .total_pickups
        .mean()
    )   

    global_mean_pickups = (
        df
        .assign(
            date=lambda df: df.datetime.dt.date
        )
        .groupby(["date", "weekday"])
        .agg(
            total_pickups=('base', 'count')
        )
        .reset_index()
        .groupby("weekday")
        .agg(
            total_pickups=("total_pickups", "mean")
        )
        .total_pickups
        .mean()
    )

    st.metric(f"Pickups on {weekday_selected}", mean_pickups_weekday_selected,
              f"{mean_pickups_weekday_selected / global_mean_pickups - 1:.2%}")

with col2:
    mean_pickups_hour_selected = (
        df
        .assign(
            hour=lambda df: df.datetime.dt.hour,
            date=lambda df: df.datetime.dt.date
        )
        .loc[lambda df: df.hour == hour_selected]
        .groupby("date")
        .agg(
            total_pickups=('date', 'count')
        )
        .total_pickups
        .mean()
    )

    global_mean_pickups_hour = (
        df
        .assign(
            hour=lambda df: df.datetime.dt.hour,
            date=lambda df: df.datetime.dt.date
        )
        .groupby(["date", "hour"])
        .agg(
            total_pickups=('base', 'count')
        )
        .reset_index()
        .groupby("hour")
        .agg(
            total_pickups=("total_pickups", "mean")
        )
        .total_pickups
        .mean()
    )
    
    st.metric(f"Pickups at {hour_selected}", mean_pickups_hour_selected,
              f"{mean_pickups_hour_selected / global_mean_pickups_hour - 1:.2%}")
    

st.map((
    df
    .loc[lambda df: df.weekday == weekday_selected]
    .loc[lambda df: df.datetime.dt.hour == hour_selected]
), use_container_width=True)