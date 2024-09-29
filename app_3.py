from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
import databases#Usado para interactuar asincronicamente, se puede consultar sin bloqueear la BBDD
import sqlalchemy#Permite interaccion con BBDD con Python, para definir tablas y operaciones
from contextlib import asynccontextmanager

import sqlalchemy.orm #Asegurarnos que se gestionan conexiones a recursos BBDD y asegurarse que se cierra bien la BBDD


DATABASE_URL = 'sqlite:///./test.db'# Se generara un archivo que guardara la BBDD
database =databases.Database(DATABASE_URL)#Maneja conexiones y trx a la BBDD de la URL
metadata=sqlalchemy.MetaData()#coleccion de info de la info de la tabla de la BBDD. Obeto que almacenara el esquema de la tabla, se debe meter en las tablas para que entre en esta coleccion

items=sqlalchemy.Table(
    'items',#nombre de tabla
    metadata, #Objeto que tendra la metadata de la abla
    sqlalchemy.Column('id',sqlalchemy.Integer, primary_key=True),#columna ID
    sqlalchemy.Column('name',sqlalchemy.String), #Columna Nombre
    sqlalchemy.Column('description',sqlalchemy.String) #Columna Descripcion
)

engine=sqlalchemy.create_engine(DATABASE_URL)#Crea motor de bbdd que permite ejecutar SQL, para ejecutar consultar y crea tablas
metadata.create_all(engine)#Usa el motor de la bbdd para crear las coleccion definida en la bbdd

SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
#autocommit=False, quiere decir que se debe confirmar cambios con commit
#Autoflosh Los cambios nose envian automaticamente antes de una consulta, se debe hacer manualmente
#bind=engine, se asocia al motor de bbdd, permitiendo ue esa session interactue con la bbdd

class Item(BaseModel):
    name:str
    description: str

class ItemCreate(BaseModel):
    name:str
    description: str

class ItemUpdate(BaseModel):
    pass
    

app=FastAPI()#Se crea app

#Simular bbdd

fakedb={
    1:{'name':'item 1', 'description':'This is item 1'},
    2:{'name':'item 2', 'description':'This is item 2'}
}

@app.get('/')#Apenas se levante la api esto se arrojara
def read_root():
    return {'message':'Hello, World'}


@app.get('/health')
def index():
    return{'message': 'hello'}

@app.get('/items/{item_id}', response_model=Item)# Se obtiene un item
def read_item(item_id:int): 
    with SessionLocal() as session:
        query =items.select().where(items.c.id==item_id)
        db_item=session.execute(query).fetchone()
        if db_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')
        return db_item._mapping
        

@app.post('/items/', response_model=Item)# Se obtiene un item
def create_item(item:ItemCreate):
    with SessionLocal() as session:
        try:
            newitem =items.insert().values(name=item.name, description=item.description)
            result = session.execute(newitem)#Ejecuto la insersion
            session.commit()#guardo cambios
            created_item_id=result.inserted_primary_key[0]#obtengo el ID
            created_item=session.execute(items.select().where(items.c.id==created_item_id)).fetchone()#consulto el elemento recien creado
            return created_item._mapping
        except Exception as e:
            session.rollback()#devuelvo el error en caso de error
            raise HTTPException(status_code=400, detailr=str(e))

@app.patch('/items/{item_id}',response_model=Item)# Se obtiene un item
def update_item(item_id:int, item: ItemUpdate):
    with SessionLocal() as session:
        update_values ={k: v for k, v in item.dict().items if v is not None}
        updated_item = items.update().where(items.c.id==item_id).values(**update_values)
        session.execute(updated_item)
        session.commit()
        updated_item = session.execute(items.select().where(items.c.id == item_id)).fetchone()
        return updated_item._mapping

@app.delete('/items/',response_model=Item)# Se obtiene un item
def delete_item(item_id:int):
    with SessionLocal() as session:
        query =items.select().where(items.c.id==item_id)
        deleted_item = session.execute(query).fetchone()
        if delete_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')
        session.execute(items.delete().where(items.c.id==item_id))
        session.commit()
        return deleted_item._mapping
    
@app.get('/items/search/{query}', response_model=List[Item])# Se obtiene un item
def search_items(query:str): 
    with SessionLocal() as session:
        query =items.select().where(items.c.name.ilike(f'%{query}%'))
        db_items=session.execute(query).fetchall()
        if db_items is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')
        return [db_item._mapping for db_item in db_items]

@app.get('/items/', response_model=List[Item])# Se obtiene un item
def get_items(skip:int=0, limit:int=10): 
    with SessionLocal() as session:
        query =items.select().offset(skip).limit(limit)
        db_items=session.execute(query).fetchall()
        if db_items is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')
        return [db_item._mapping for db_item in db_items]