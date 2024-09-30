from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import databases
import sqlalchemy
from contextlib import asynccontextmanager 
import pandas as pd
from joblib import load
from io import StringIO
import numpy as np
from datetime import datetime
import pytz


DATABASE_URL='mysql+pymysql://root:ULbzggxgRxVDgRhWnEHtyqTPADoqjNnZ@autorack.proxy.rlwy.net:21845/railway'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


prediccion = sqlalchemy.Table(
    "prediccion",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("file", sqlalchemy.String(50)),
    sqlalchemy.Column("prediction", sqlalchemy.Float),
    sqlalchemy.Column("created_at", sqlalchemy.TIMESTAMP)
)

estadisticosprediccion = sqlalchemy.Table(
    "estadisticosprediccion",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("file", sqlalchemy.String(50)),
    sqlalchemy.Column("estadistico", sqlalchemy.String(20)),
    sqlalchemy.Column("valor", sqlalchemy.Float),
    sqlalchemy.Column("created_at", sqlalchemy.TIMESTAMP)
)


engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine) 

app=FastAPI()

regressor = load('pipeline.joblib')

x_train=pd.read_csv('test.csv')

x_train['running']=x_train['running'].apply(lambda x: float(x.replace('km','')) if x[-2:]=='km' else float(x.replace('miles',''))*1.609344)
x_train.drop(['Id','wheel'], axis=1, inplace=True)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/health')
def index():
    return{'message': 'hello'}

@app.get('/')
def read_root():
    return {'message':'Hello, World'}

@app.post('/predict_upload')
async def predict_cars_price(file:UploadFile = File(...)):

    prediction = regressor.predict(x_train)
    contents = await file.read()
    df=pd.read_csv(StringIO(contents.decode('utf-8')))
    df['running']=df['running'].apply(lambda x: float(x.replace('km','')) if x[-2:]=='km' else float(x.replace('miles',''))*1.609344)
    df.drop(['Id','wheel'], axis=1, inplace=True)
    prediction = regressor.predict(df)
    prediction=np.exp(prediction)
    now=datetime.now(pytz.timezone('America/Santiago')) 
    for i in prediction:
        query =prediccion.insert().values(file=file.filename, prediction=i,created_at=now)
        last_record_id = await database.execute(query)
    return {'prediction': prediction.tolist()}


@app.post('/calculate_estadisticos_last_batch')
async def predict_cars_price():

    query = sqlalchemy.select(sqlalchemy.func.max(prediccion.c.created_at))
    last_upload_date = await database.fetch_one(query)
    if last_upload_date is None:
        raise HTTPException(status_code=404, detail='Sin datos cargados')
    query =prediccion.select().where(prediccion.c.created_at==last_upload_date['max_1'])
    predicts=await database.fetch_all(query)
    predicciones=[]
    for i in predicts:
        predicciones.append(i['prediction'])
    file=i['file']+str(i['created_at'])
    estadisticos = {
    'sum': np.sum,
    'mean': np.mean,
    'median': np.median,
    'max': np.max,
    'min': np.min,
    'std': np.std
    }
    print(predicciones)
    esta=[]
    for i,j in estadisticos.items():
        query =estadisticosprediccion.insert().values(file=file, estadistico=i,valor=j(predicciones),created_at=datetime.now(pytz.timezone('America/Santiago')))
        last_record_id = await database.execute(query)
        fila={}
        fila['file']=file
        fila['estadistico']=i
        fila['valor']=j(predicciones)
        fila['created_at']=datetime.now(pytz.timezone('America/Santiago'))
        esta.append(fila)
    return {'predict':esta}