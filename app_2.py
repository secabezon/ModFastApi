from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import databases#Usado para interactuar asincronicamente, se puede consultar sin bloqueear la BBDD
import sqlalchemy#Permite interaccion con BBDD con Python, para definir tablas y operaciones
from contextlib import asynccontextmanager #Asegurarnos que se gestionan conexiones a recursos BBDD y asegurarse que se cierra bien la BBDD

DATABASE_URL='mysql+pymysql://root:ULbzggxgRxVDgRhWnEHtyqTPADoqjNnZ@autorack.proxy.rlwy.net:21845/railway'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Definir la tabla items (debes crear explícitamente la tabla si no existe)
items = sqlalchemy.Table(
    "items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(50)),
    sqlalchemy.Column("description", sqlalchemy.String(200))
)

# Crear el motor SQLAlchemy
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine) 

class Item(BaseModel):
    name:str
    description: str = None
    
# @asynccontextmanager #Se ejecutan conexiones en paralelo por eso es asincrona, y puede hacer tareas antes o despues del ciclo de vida de la app
# async def lifespan(app:FastAPI):#Conexión a la bbdd y estara activa cuando este activa la app
#     await database.connect()#Abre conexión a la BBDD cuando se inicia la app en FastApi
#     #await database_v2.connect() para otra bbdd
#     yield #Se para a parte donde la app esta en funcionamiento, no hace nada eso si, solo se deja app corriendo
#     await database.disconnect() #cierra conexion cuando se apaga FastAPI



app=FastAPI()#Se crea app

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# app.add_event_handler('startup',lambda: database.connect())#Añade manejados de eventos cuando la app inicie
# app.add_event_handler('shutdown',lambda: database.disconnect())#Añade manejados de eventos cuando la app termine
# app.dependency_overrides[database]=lifespan#Sobre escribe dependencias de fastapi, como maneja las bbdd con la funcion creada lifespan, elimina las configuraciones por default de FastAPI, Asegurando que las conexiones se manejen asincronamente y correctamente durante el ciclo de vida de la API

#Simular bbdd

@app.get('/health')
def index():
    return{'message': 'hello'}

@app.get('/')#Apenas se levante la api esto se arrojara
def read_root():
    return {'message':'Hello, World'}


@app.get('/items/{item_id}')# Se obtiene un item
async def read_item(item_id:int): #Poruqe mucha gente lo usa por eso esta async, para soportar toda solicitus
    query =items.select().where(items.c.id==item_id)
    item=await database.fetch_one(query)
    if item is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return item
    

@app.post('/items/')# Se obtiene un item
async def create_item(item:Item):
    query =items.insert().values(name=item.name, description=item.description)
    last_record_id = await database.execute(query)
    return {**item.dict(), 'id':last_record_id}

@app.put('/items/{item_id}')# Se obtiene un item
async def update_item(item:Item, item_id:int):
    query =items.update().where(items.c.id==item_id).values(name=item.name, description=item.description)
    await database.execute(query)
    return {**item.dict(), 'id':item_id}

@app.delete('/items/')# Se obtiene un item
async def delete_item(item_id:int):
    query =items.delete().where(items.c.id==item_id)
    await database.execute(query)
    return {'message':'item deleted'}