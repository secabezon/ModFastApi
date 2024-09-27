import uvicorn
from fastapi import FastAPI
from Houses import House
from joblib import load
import pandas as pd


app=FastAPI()

classifier = load('linear_regression.joblib')

x_train=pd.read_csv('x_train.csv')
features=pd.read_csv('selected_features.csv')
features=features['0'].tolist()
x_train=x_train[features]


@app.get('/')
def index():
    return{'message': 'hello'}

@app.post('/predict')
def predict_house_price(data:House):

    prediction = classifier.predict(x_train)

    return {'predict':prediction.to_list()}