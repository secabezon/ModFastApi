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
    # year=data.year
    # running=data.running
    # status=data.status
    # motor_volume=data.motor_volume
    # price=data.price
    # model_hyundai=data.model_hyundai
    # model_kia=data.model_kia
    # model_mercedes_benz=data.model_mercedes_benz
    # model_nissan=data.model_nissan
    # model_toyota=data.model_toyota
    # motor_type_diesel=data.motor_type_diesel
    # motor_type_gas=data.motor_type_gas
    # motor_type_hybrid=data.motor_type_hybrid
    # motor_type_petrol=data.motor_type_petrol
    # color_beige=data.color_beige
    # color_black=data.color_black
    # color_blue=data.color_blue
    # color_brown=data.color_brown
    # color_cherry=data.color_cherry
    # color_clove=data.color_clove
    # color_golden=data.color_golden
    # color_gray=data.color_gray
    # color_green=data.color_green
    # color_orange=data.color_orange
    # color_other=data.color_other
    # color_pink=data.color_pink
    # color_purple=data.color_purple
    # color_red=data.color_red
    # color_silver=data.color_silver
    # color_skyblue=data.color_skyblue
    # color_white=data.color_white
    # type_Coupe=data.type_Coupe
    # type_Universal=data.type_Universal
    # type_hatchback=data.type_hatchback
    # type_pickup=data.type_pickup
    # type_sedan=data.type_sedan
    # type_suv=data.type_suv

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