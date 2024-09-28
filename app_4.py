import uvicorn
from fastapi import FastAPI
from Car import Car
from joblib import load


app=FastAPI()

regressor = load('pipeline.joblib')

@app.get('/')
def index():
    return{'message': 'hello'}

@app.post('/predict')
def predict_car_price(data:House):

    prediction = regressor.predict()

    return {'predict':prediction.to_list()}