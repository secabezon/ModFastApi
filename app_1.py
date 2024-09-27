from fastapi import FastAPI, HTTPException

app=FastAPI()#Se crea app

#Simular bbdd

fakedb={
    1:{'name':'item 1', 'description':'This is item 1'},
    2:{'name':'item 2', 'description':'This is item 2'}
}

@app.get('/')#Apenas se levante la api esto se arrojara
def read_root():
    return {'message':'Hello, World'}


@app.get('/items/{item_id}')# Se obtiene un item
def read_item(item_id:int):
    if item_id in fakedb:
        return fakedb[item_id]
    else:
        raise HTTPException(status_code=404, detail='Item not found')
    

@app.post('/items/')# Se obtiene un item
def create_item(item_id:int, name:str, description:str):
    if item_id in fakedb:
        raise HTTPException(status_code=404, detail='Item already exists')
    else:
        fakedb[item_id]={'name':name,'description':description}
        return fakedb['item_id']