from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import databases
import sqlalchemy
from contextlib import asynccontextmanager

DATABASE_URL = 'sqlite:///./test.db'
database =databases.Database(DATABASE_URL)
metadata=sqlalchemy.MetaData()#toda la metadata de los proceso se vaya a una libreria

items=sqlalchemy.Table(
    'items',
    metadata,
    sqlalchemy.Column('id',sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name',sqlalchemy.String),
    sqlalchemy.Column('description',sqlalchemy.String)
)

engine=sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)#crea la bbdd

class Item(BaseModel):
    name:str
    description: str = None
    
@asynccontextmanager #Se ejecutan conexiones en paralelo por eso es asincrona
async def lifespan(app:FastAPI):#Conexión a la bbdd y estara activa cuando este activa la app
    await database.connect()
    #await database_v2.connect() para otra bbdd
    yield #Cuando termine el despliegue de la API termine, cerrara toda la conexión
    await database.disconnect()

app=FastAPI()#Se crea app

app.add_event_handler('startup',lambda: database.connect())
app.add_event_handler('shutdown',lambda: database.disconnect())
app.dependency_overrides[database]=lifespan

#Simular bbdd

fakedb={
    1:{'name':'item 1', 'description':'This is item 1'},
    2:{'name':'item 2', 'description':'This is item 2'}
}

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