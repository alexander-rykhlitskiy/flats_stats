import streamlit as st
import pandas as pd
import numpy as np

st.title('Flats stats')

DATA_URL = 'flats.csv'
ROOMS_NUMBER_COLUMN = 'rooms_number'
DATE_COLUMN = 'updated_at'
LAT_COLUMN = 'lat'
LON_COLUMN = 'lon'

def remove_blank(data, column_name):
    data[column_name].replace('', np.nan, inplace=True)
    data.dropna(subset=[column_name], inplace=True)

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    remove_blank(data, LAT_COLUMN)
    remove_blank(data, LON_COLUMN)
    remove_blank(data, ROOMS_NUMBER_COLUMN)
    return data

data = load_data(10000)

st.subheader('Raw data')
st.write(data)

st.subheader('Number of new flats by hour')
hist_values = np.histogram(
    data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

rooms_to_filter = st.slider('rooms number', 0, int(data[ROOMS_NUMBER_COLUMN].max()), 2) # min, max, default
st.subheader(f'Map of all flats, {rooms_to_filter} rooms')
st.map(data[data[ROOMS_NUMBER_COLUMN] == rooms_to_filter])
