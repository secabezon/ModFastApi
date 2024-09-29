import uvicorn
from fastapi import FastAPI, UploadFile, File
from Car import Car
from joblib import load
import pandas as pd
from io import StringIO
import numpy as np

app=FastAPI()

regressor = load('pipeline.joblib')

x_train=pd.read_csv('test.csv')

x_train['running']=x_train['running'].apply(lambda x: float(x.replace('km','')) if x[-2:]=='km' else float(x.replace('miles',''))*1.609344)
x_train.drop(['Id','wheel'], axis=1, inplace=True)

@app.get('/')
def index():
    return{'message': 'hello'}

@app.get('/health')
def index():
    return{'message': 'hello'}

@app.post('/predict')
def predict_car_price():
    prediction = regressor.predict(x_train)
    prediction=np.exp(prediction)
    return {'predict':prediction.tolist()}

@app.post('/predict_upload')
async def predict_cars_price(file:UploadFile = File(...)):

    prediction = regressor.predict(x_train)
    contents = await file.read()
    df=pd.read_csv(StringIO(contents.decode('utf-8')))
    df['running']=df['running'].apply(lambda x: float(x.replace('km','')) if x[-2:]=='km' else float(x.replace('miles',''))*1.609344)
    df.drop(['Id','wheel'], axis=1, inplace=True)
    prediction = regressor.predict(df)
    prediction=np.exp(prediction)
    return {'predict':prediction.tolist()}