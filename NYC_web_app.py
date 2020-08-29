import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL=(
"./Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Collisions in NYC")
st.markdown("This application is a streamlit dashboard coded in python that can be used to Analyze Motor Vehicle Collisions in NYC")

@st.cache(persist=True)
def load_data(nrows):
    data=pd.read_csv(DATA_URL,nrows=nrows,parse_dates=[["CRASH_DATE","CRASH_TIME"]])
    data.dropna(subset=["LATITUDE","LONGITUDE"],inplace=True)
    lowercase=lambda x : str(x).lower()
    data.rename(lowercase,axis=1,inplace=True)
    data.rename(columns={"crash_date_crash_time":"date/time"},inplace=True)
    return data

data=load_data(100000)
original_data=data.copy()
st.header("Where are the most people injured in NYC?")
injured_people=st.slider("Move the slider to select #people injured in vechile collisions",0,19,3)


midpoint=(np.average(data['latitude']),np.average(data["longitude"]))
st.deck_gl_chart(
            viewport={
                'latitude': midpoint[0],
                'longitude':  midpoint[1],
                'zoom': 9
            },
            layers=[{
                'type': 'ScatterplotLayer',
                'data': data.query("injured_persons>=@injured_people")[["latitude","longitude"]].dropna(how="any"),
                'radiusScale': 2,
   'radiusMinPixels': 1,
                'getFillColor': [248, 24, 100],
            }]
        )




st.header("How many collisions occur during a given time of day")
hour=st.slider("Hour to look at",1,25,17)
data=data[data["date/time"].dt.hour==hour]

st.markdown("Vechile collisions between %i:00 and %i:00"%(hour,(hour+1)%24))

midpoint=(np.average(data['latitude']),np.average(data["longitude"]))
layers=[
pdk.Layer(
"HexagonLayer",
data=data[["date/time","latitude","longitude"]],
get_position=["longitude","latitude"],
radius=100,
extruded=True,
pickabele=True,
elevation_scale=4,
elevation_range=[0,1000],

),
]

fig=pdk.Deck(
map_style="mapbox://styles/mapbox/light-v9",
initial_view_state={
"latitude":midpoint[0],
"longitude":midpoint[1],
"zoom":10,
"pitch":50
},layers=layers
)
st.write(fig)


st.subheader("Breakdown of collisions between %i:00 and %i:00"%(hour,(hour+1)%24))
filtered_data=data.loc[(data["date/time"].dt.hour>=hour)&(data["date/time"].dt.hour<hour+1)]
hist=np.histogram(filtered_data["date/time"].dt.minute,bins=60,range=(0,60))[0]
chart_data=pd.DataFrame({"minute":range(60),"crashes":hist})
fig=px.bar(chart_data,x='minute',y='crashes',hover_data=["minute","crashes"],height=400)
st.write(fig)

st.header("Top 5 dangerous streets by type")
select = st.selectbox("Affected type of people",["Pedestrians","Cyclists","Motorists"])

if select=="Pedestrians":
    st.write(original_data.query("injured_pedestrians>=1")\
    [["on_street_name","injured_pedestrians"]]\
    .sort_values(by=["injured_pedestrians"],ascending=False).dropna(how="any")[:5])
elif select=="Cyclists":
    st.write(original_data.query("injured_cyclists>=1")\
    [["on_street_name","injured_cyclists"]]\
    .sort_values(by=["injured_cyclists"],ascending=False).dropna(how="any")[:5])
else :
    st.write(original_data.query("injured_motorists>=1")\
    [["on_street_name","injured_motorists"]]\
    .sort_values(by=["injured_motorists"],ascending=False).dropna(how="any")[:5])




if st.checkbox("Click to Show Raw Data",False):
    st.subheader("Raw Data")
    st.write(data)
