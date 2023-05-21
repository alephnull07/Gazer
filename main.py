from flask import Flask, redirect, url_for, render_template, request, flash
import pandas as pd 
import math
import requests
import csv 
import sklearn
import joblib
import json

app = Flask(__name__)

star_points = ""
location = ""

@app.route("/")
@app.route("/home")
def home_page():
    global star_points 
    global location 
    location = request.args.get("location", "")
    # machine is here 
    # use pickle  to pass location through the machine 
    machine = joblib.load('model.joblib')
    if location:
        star_points = calculate_star_points(location)
        # star_points = machine.predict(location)
        return redirect("/results")
    else:
        return render_template('home.html')

LM = 3
AQ = 19

CityCoor = pd.read_csv("worldcities.csv")
CityCoor = CityCoor.drop(columns = ['city_ascii','iso2','iso3','admin_name','capital','population','id'])
CityCoor = pd.read_csv("worldcities.csv")
CityCoor = CityCoor.drop(columns = ['city_ascii','iso2','iso3','admin_name','capital','population','id'])
CityCoor = CityCoor.sort_values(['city'])
cols = list(CityCoor.columns.values)
CityCoor = CityCoor[cols[1:3] + [cols[0]] + [cols[3]]]

def search_city(city):
  low = 0
  high = len(CityCoor.index)-1

  while low < high:
    mid = low + (high-low)//2
    if CityCoor.iloc[mid,2] < city:
      low = mid + 1
    else:
      high = mid

  if CityCoor.iloc[low,2] == city:
    global lat 
    global lng 
    lat = CityCoor.iloc[low,0]
    lng = CityCoor.iloc[low,1]
  else:
    return (0,0)


def calculate_star_points(input):
    print(search_city(input))
    
    with open("data.csv",'r') as file:
        csvreader = csv.reader(file)
        print('LM','AQ')
        print(LM,AQ)
    
    data = pd.read_csv("Data.csv")

    loaded_model = joblib.load("model.joblib")
    pred_cols = list(data.columns.values)
    SQM = loaded_model.predict(data[pred_cols].values)
    
    star_points = round(SQM * 0.3125)

coordinatesList = search_city(location)
latitude = coordinatesList[0]
longitude = coordinatesList[1]
api_token = 'oxGvZawYkOVvhVWBQFmXWdkdgqXBZomI'

url = f'https://api.weather.gov/points/{latitude},{longitude}'

#new york 45, -70
#topeka, Kansas 39,-97
headers = {'token': api_token}

response = requests.get(url, headers=headers)
data = json.loads(response.text)
print(data)
gridX = 0
gridY = 0
forecastList = []
timeofDay = []

gridX = data['properties']['gridX']
gridY = data['properties']['gridY']
gridID = data['properties']['gridId']

api_token = 'oxGvZawYkOVvhVWBQFmXWdkdgqXBZomI'
url2 = f'https://api.weather.gov/gridpoints/{gridID}/{gridX},{gridY}/forecast'


headers = {'token': api_token}

response2 = requests.get(url2, headers=headers)
data2 = json.loads(response2.text)
for s in data2['properties']['periods']:
    forecast = s['shortForecast']
    forecastList.append(forecast)
    if len(forecastList) == 2:
        break
for s in data2['properties']['periods']:
    time = s['isDaytime']
    timeofDay.append(time)
    if len(timeofDay) == 2:
        break

print(forecastList)
print(timeofDay)

# use API for getting the weather
# Check if weather clear. If cloudy, star points = 0. Else, no change 

api_token3 = 'd5c84af6cbe75868e801b8757861b235'

url3 = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={api_token3}'

response3 = requests.get(url3)
data3 = json.loads(response3.text)

AQ = data3['list'][0]['main']['aqi']

# use the API to get LM and AQI 
    # add to CSV 2x2
    # feed CSV into the machine and get the output. Save to final star index num 
    # convert long and lat into x and y  


    # output starpoints


@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/results")
def results_page():
    star_amount = math.ceil(star_points/20)
    global star_img
    star_img = f'/static/star{star_amount}.png'
    return render_template('results.html', value1=location, value2=star_points, value3 = star_img, latt=lat, longg=lng) 