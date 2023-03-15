# !pip install plotly plotly-express
# !pip install hvplot holoviews

import panel as pn
import pandas as pd
import datetime as dt
import requests
import param
import plotly.express as px

pn.extension(sizing_mode="stretch_width")

# Получаем id и symbol для каждого актива
response = requests.get('https://api.coincap.io/v2/assets')
if response.status_code == 200:
    data = response.json()['data']
    df = pd.DataFrame(data)
    assets = df[['id', 'symbol']]
    symbols = assets['symbol'].unique()
else:
    print('Error occurred with status code:', response.status_code)


class BitcoinDashboard(param.Parameterized):
    
    symbol_input = pn.widgets.Select(name='Select and asset', options=list(symbols), width=100)

    datetime_range_input = pn.widgets.DatetimeRangeInput(
        name='Datetime Range Input',
        value=(dt.datetime(2022, 5, 1), dt.datetime(2022, 6, 1)),
        width=200
    )
    
    @param.depends('symbol_input.value', 'datetime_range_input.value')
    def plot_data(self):
        symbol = self.symbol_input.value
        asset_id = assets.loc[assets['symbol'] == symbol, 'id'].values[0]
        start_date, end_date = self.datetime_range_input.value
        response = requests.get(f'https://api.coincap.io/v2/assets/{asset_id}/history?interval=d1')
        if response.status_code == 200:
            data = response.json()['data']
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S.%fZ')
            df.drop(['time'], axis=1, inplace=True) # Удаляем столбец time
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            filtered_df = df.loc[mask]
            fig = px.histogram(filtered_df, x='date', y='priceUsd', nbins=50)
            fig.update_layout(bargap=0.2)
            fig.update_yaxes(title='Price, USD')
            fig.update_xaxes(title='Date')
            return pn.pane.Plotly(fig)
        else:
            print('Error occurred with status code:', response.status_code)
    
    def view(self):
        return pn.Row(
            pn.Column(
                self.symbol_input,
                self.datetime_range_input,
                sizing_mode='fixed', align='center',
                background='WhiteSmoke',
                height=450
            ),
            pn.Column(
                self.plot_data,
                background='WhiteSmoke',
                height=450
            )
        )
        

dashboard = BitcoinDashboard()
dashboard.view().servable()
