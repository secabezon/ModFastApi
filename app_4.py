import uvicorn
from fastapi import FastAPI
from Houses import House
from joblib import load


app=FastAPI()

classifier = load('linear_regression.joblib')

@app.get('/')
def index():
    return{'message': 'hello'}

@app.post('/predict')
def predict_house_price(data:House):

    prediction = classifier.predict()

    return {'predict':prediction.to_list()}