import streamlit as st
import pandas as pd
import numpy as np

st.title('Flats stats')

DATA_PATH = 'flats.csv'
ROOMS_NUMBER_COLUMN = 'rooms_number'
DATE_COLUMN = 'updated_at'
LAT_COLUMN = 'lat'
LON_COLUMN = 'lon'

def remove_blank(data, column_name):
    data[column_name].replace('', np.nan, inplace=True)
    data.dropna(subset=[column_name], inplace=True)

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_PATH, nrows=nrows)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    remove_blank(data, LAT_COLUMN)
    remove_blank(data, LON_COLUMN)
    remove_blank(data, ROOMS_NUMBER_COLUMN)
    # Central belarus borders
    data = data[(data.lat < 54.0) & (data.lat > 53.8) & (data.lon > 27.3) & (data.lon < 27.7)]
    data = data[(data.price < 2000) & (data.price > 50)]
    return data

data = load_data(10000)

select_values = list(map(str, range(0, int(data[ROOMS_NUMBER_COLUMN].max()))))
rooms_to_filter = st.multiselect('Rooms number', select_values, default=select_values)

filtered_data = data[data.rooms_number.isin(rooms_to_filter)]

st.write(f'{len(filtered_data)} flats analyzed')

st.subheader('Number of newly added for rent flats by hour')
hist_values = np.histogram(
    filtered_data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

minsk_map_options = {
    'latitude': 53.903589,
    'longitude': 27.560685,
    'zoom': 10
}

st.subheader('Mean prices by regions')
st.deck_gl_chart(viewport=minsk_map_options,
  layers = [{
        'data': filtered_data,
        'getColorWeight': 'price',
        'colorAggregation': 'MEAN',
        'radius': 1000,
        'type': 'HexagonLayer',
        'opacity': 0.3,
        'upperPercentile': 96,
        'lowerPercentile': 4,
    }])

st.subheader('Number of flats by regions')
st.deck_gl_chart(viewport=minsk_map_options,
  layers = [{
        'data': filtered_data,
        'radius': 1000,
        'type': 'HexagonLayer',
        'opacity': 0.3,
        # 'upperPercentile': 99.9,
        'lowerPercentile': 4,
    }])

st.subheader('Some analysis')
st.write(filtered_data[['price', 'rooms_number', 'lat', 'lon']].describe())

st.subheader('Raw data')
st.write(filtered_data)

st.write(f'More details here https://github.com/alexander-rykhlitskiy/flats_stats')
