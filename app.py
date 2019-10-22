import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

DATA_PATH = 'flats.csv'

def main():
    st.title('Статистика по квартирам в Минске')

    data = load_data(None)
    data = filter_by_user_input(data)

    draw_histograms(data)
    draw_maps(data)
    draw_footer(data)

def filter_by_user_input(data):
    result = filter_by_rooms_number(data)

    include_agents = st.sidebar.checkbox('Включать объявления агентов')
    if not include_agents:
        result = data.query("agent != 't'")

    st.sidebar.markdown('Обявления даны:')
    since_date = st.sidebar.date_input('С', value=min(data['created_at']))
    untill_date = st.sidebar.date_input('По', value=max(data['created_at']))
    format_date = lambda date: str(date).replace('-', '')
    result = result.query(f'created_at >= {format_date(since_date)} and created_at <= {format_date(untill_date)}')

    return result

def filter_by_rooms_number(data):
    one_room_label = 'комната'
    select_values = sorted([str(int(x)) for x in data['rooms_number'].unique()])

    replace_item = lambda items, from_item, to_item: [to_item if (x == from_item) else x for x in items]

    select_values = replace_item(select_values, '0', one_room_label)
    rooms_to_filter = st.sidebar.multiselect('Число комнат', select_values, default=select_values)
    rooms_to_filter = replace_item(rooms_to_filter, one_room_label, '0')

    return data.query(f'rooms_number in {rooms_to_filter}')

def draw_histograms(data):
    st.write(f'{len(data)} квартир проанализировано')

    st.subheader('Распределение цен')
    bin_base = 10
    prices = data['price'].apply(lambda p: (int(round(float(p) / bin_base)) * bin_base))
    prices_set = sorted(set(prices))
    hist_values = np.histogram(prices, bins=len(prices_set))[0]
    price_column = 'Цена'
    count_column = 'Число квартир'
    df = pd.DataFrame(data={price_column: prices_set, count_column: hist_values})
    fig = px.bar(df, x=price_column, y=count_column)
    st.plotly_chart(fig)

    st.subheader('Число добавленных в объявления квартир по часам')
    hour_column = 'Час суток'
    range_limit = 24
    hist_values = np.histogram(data['created_at'].dt.hour, bins=range_limit, range=(0,range_limit))[0]
    df = pd.DataFrame(data={hour_column: range(range_limit), count_column: hist_values})
    fig = px.bar(df, x=hour_column, y=count_column)
    st.plotly_chart(fig)

def draw_maps(data):
    chart_data = data[['lon', 'lat', 'price']]

    minsk_map_options = {
        'latitude': 53.903589,
        'longitude': 27.560685,
        'zoom': 10
    }

    st.subheader('Средние цены по регионам')
    st.deck_gl_chart(viewport=minsk_map_options,
      layers = [{
            'data': chart_data,
            'getColorWeight': 'price',
            'colorAggregation': 'MEAN',
            'radius': 1000,
            'type': 'HexagonLayer',
            'opacity': 0.3,
            'upperPercentile': 98, # hack to remove regions with extremely high and low prices (a lot of
            'lowerPercentile': 3, #  houses or smth). It makes map more colorful
            # 'elevationLowerPercentile': 25, # as aggregation for elevation is sum, it removes cells with low number of flats. But it doesn't affect color of cells, so not used
            # extruded: true, # whether to enable cell elevation
            # pitch: 10,
            # ```javascript
            # pickable: true,
            # // http://deck.gl/#/documentation/developer-guide/adding-interactivity?section=example-display-a-tooltip-for-hovered-object
            # onHover: ({object, x, y}) => {
            #   if (object) {
            #     console.log(`Mean price is ${object.colorValue}. Flats number is ${object.elevationValue}`)
            #     console.log(object.points)
            #   }
            # },
            # ```
        }])

    st.subheader('Число квартир по регионам')
    st.deck_gl_chart(viewport=minsk_map_options,
      layers = [{
            'data': chart_data,
            'radius': 1000,
            'type': 'HexagonLayer',
            'opacity': 0.3,
        }])

def draw_footer(data):
    st.subheader('Общий анализ квартир')
    st.write(data[['price', 'rooms_number', 'lat', 'lon']].describe())

    # st.subheader('Все данные')
    # st.write(data)

    st.write(f'Узнать детали можно здесь https://github.com/alexander-rykhlitskiy/flats_stats')

def remove_blank(data, column_name):
    data[column_name].replace('', np.nan, inplace=True)
    data.dropna(subset=[column_name], inplace=True)

@st.cache
def load_data(nrows=None):
    data = pd.read_csv(DATA_PATH, nrows=nrows)
    data['created_at'] = pd.to_datetime(data['created_at'])
    remove_blank(data, 'lat')
    remove_blank(data, 'lon')
    remove_blank(data, 'rooms_number')
    # Central Belarus borders
    data = data[(data.lat < 54.0) & (data.lat > 53.8) & (data.lon > 27.3) & (data.lon < 27.7)]
    # filter probably fake or incorrect ads
    data = data[(data.price < 2000) & (data.price > 50)]
    data = data[(data.price < np.percentile(data.price, 95)) & (data.price > np.percentile(data.price, 5))]

    # data.groupby(by='address')['address'].size().sort_values().tail(2).index.values # >>> ['Минск', 'Минск, ']
    incomplete_addresses = "['Минск', 'Минск, ']"
    max_real_rooms_number = 4
    query = ' '.join([
        f'address not in {incomplete_addresses}',
        f'and rooms_number <= {max_real_rooms_number}'
        ])
    data = data.query(query)

    data = data.drop_duplicates(['lon', 'lat', 'price', 'rooms_number'])
    return data

if __name__ == "__main__":
    main()
