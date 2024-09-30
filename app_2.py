from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import databases
import sqlalchemy
from contextlib import asynccontextmanager 

DATABASE_URL='mysql+pymysql://root:ULbzggxgRxVDgRhWnEHtyqTPADoqjNnZ@autorack.proxy.rlwy.net:21845/railway'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


items = sqlalchemy.Table(
    "items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(50)),
    sqlalchemy.Column("description", sqlalchemy.String(200))
)


engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine) 

class Item(BaseModel):
    name:str
    description: str = None

app=FastAPI()

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


@app.get('/items/{item_id}')
async def read_item(item_id:int):
    query =items.select().where(items.c.id==item_id)
    item=await database.fetch_one(query)
    if item is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return item
    

@app.post('/items/')
async def create_item(item:Item):
    query =items.insert().values(name=item.name, description=item.description)
    last_record_id = await database.execute(query)
    return {**item.dict(), 'id':last_record_id}

@app.put('/items/{item_id}')
async def update_item(item:Item, item_id:int):
    query =items.update().where(items.c.id==item_id).values(name=item.name, description=item.description)
    await database.execute(query)
    return {**item.dict(), 'id':item_id}

@app.delete('/items/')
async def delete_item(item_id:int):
    query =items.delete().where(items.c.id==item_id)
    await database.execute(query)
    return {'message':'item deleted'}