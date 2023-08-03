import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

import pandas as pd
import json

"""
# Weather prediction 🌡️
"""

def get_data_from_json(input_file):
    with open(input_file) as json_file:
        return json.load(json_file)

def json_to_value(weather):
    data = []
    for item in weather:
        new_item = dict()
        for key, value in item.items():
            if "Wind" in key:
                new_item[f"{key} ({value['Speed']['Unit']})"] = value['Speed']['Value']
            elif key == 'EpochDateTime':
                date = datetime.fromtimestamp(value)
                new_item['Hour'] = date.hour
                new_item['Date'] = date.strftime("%d/%m/%Y")
                new_item[key] = value
            elif "Feel" in key:
                new_item[f"{key} ({value['Unit']})"] = value['Value']
                new_item[f"{key}Type"] = value['Phrase']
            elif type(value) is dict:
                new_item[f"{key} ({value['Unit']})"] = value['Value']
            else:
                new_item[key] = value
        data.append(new_item)

    return data

def temp_plot(df):
    fig = go.Figure()
    x = df['Hour']
    y1 = df['Temperature (C)']
    y2 = df['RealFeelTemperature (C)']
    y3 = df['PrecipitationProbability']
    hover = df['RealFeelTemperatureType']

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=x, y=y3, 
            name="Precipitation Probability",
            hovertemplate = '<b>Chance:</b> %{y}%',
            
        ),
        secondary_y=False
    )

    fig.update_traces(marker_color='rgba(0, 180, 216, 0.5)')

    fig.add_trace(
        go.Scatter(
            x=x, y=y2,
            mode='lines+markers',
            name='Real Feel Temperature (C)',
            hovertemplate = '<b>%{text}</b><br>' + '<b>Temp:</b> %{y:.1f}°C',
            text=hover,
            line=dict(color='firebrick', width=2, dash='dash')
        ),
        secondary_y=True)

    fig.add_trace(
        go.Scatter(
            x=x, y=y1,
            mode='lines+markers',
            name='Temperature (C)',
            hovertemplate = '<b>Temp:</b> %{y:.1f}°C',
            line=dict(color='red', width=2)
        ),
        secondary_y=True)

    fig.update_xaxes(type='category', title_text="Hour")

    fig.update_yaxes(title_text="Chance of rain", secondary_y=False, range=[0,100])
    fig.update_yaxes(title_text="Temperature (C)", secondary_y=True, range=[-10,42])

    return fig

def gethourlyforecast(location_key, output_file):
    hourly_forecastURL = "https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/"+location_key+"?apikey="+API+"&details=true&metric=true"
    print("Requesting information from", hourly_forecastURL)
    
    response = requests.get(hourly_forecastURL)

    with open(output_file, mode="w+") as out_file:
        text = json.dumps(response.json(), indent=4)
        out_file.write(text)

    return response.json()
            

# Choose the city to display
city = st.selectbox('Choose city:', options=["Hanoi", "HCM"])

API='mBuY4aPdL9UDYjpwaUy9lYTcHfbrZZIf' #your API name
countrycode='VN'
location_key = {"hanoi": "353412", "hcm": "3-433307_1_AL"}

# Run API for fresh data 
if st.button('Get new prediction data'):
    output_file = f'output/{city.lower()}_weather.json'
    gethourlyforecast(location_key[city.lower()], output_file)

input_file = f'output/{city.lower()}_weather.json'
weather = get_data_from_json(input_file)
data = json_to_value(weather)
df = pd.DataFrame(data)
fig = temp_plot(df)

# Write description
st.write(f"Weather prediction for {city} from *{df['Hour'][0]}:00 {df['Date'][0]}* to *{df['Hour'].iloc[-1]}:00 {df['Date'].iloc[-1]}*.")

# Plot!
st.plotly_chart(fig)

# Dataframe 
columns = ['Hour', 'IconPhrase', 'IsDaylight', 'Temperature (C)',
       'RealFeelTemperature (C)',
       'RealFeelTemperatureShade (C)', 'Wind (km/h)',
       'WindGust (km/h)', 'UVIndex', 'UVIndexText',
       'PrecipitationProbability', 'ThunderstormProbability',
       'RainProbability']

df2 = df[columns].set_index('Hour')

st.data_editor(
    df2,
    column_config={
        "PrecipitationProbability": st.column_config.ProgressColumn(
            "PrecipitationProbability",
            help="PrecipitationProbability",
            format="%f%%",
            min_value=0,
            max_value=100,
        ),
        "ThunderstormProbability": st.column_config.ProgressColumn(
            "ThunderstormProbability",
            help="ThunderstormProbability",
            format="%f%%",
            min_value=0,
            max_value=100,
        ),
        "RainProbability": st.column_config.ProgressColumn(
            "RainProbability",
            help="RainProbability",
            format="%f%%",
            min_value=0,
            max_value=100,
        ),
    }
)
