import uvicorn
from fastapi import FastAPI
from Car import Car
from joblib import load
import numpy as np
import pandas as pd
import feature_engine


app=FastAPI()

regressor = load('pipeline.joblib')


@app.get('/')
def index():
    return{'message':'hello'}

@app.post('/predict')
def predict_car_price(data:Car):
    Id=data.Id
    model=data.model
    year=data.year
    motor_type=data.motor_type
    running=data.running
    wheel=data.wheel
    color=data.color
    types=data.type
    status=data.status
    motor_volume=data.motor_volume
    running=float(running.replace('km','')) if running[-2:]=='km' else float(running.replace('miles',''))*1.609344
    datas=[[model,year,motor_type,running,color,types,status,motor_volume]]
    df = pd.DataFrame(datas, columns=['model', 'year', 'motor_type', 'running','color', 'type', 'status', 'motor_volume'])
    prediction = regressor.predict(df)
    prediction=np.exp(prediction)
    return {'predict':prediction[0]}