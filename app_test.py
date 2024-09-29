from databases import Database
from fastapi import FastAPI

# Configura la URL de la base de datos
DATABASE_URL = "mysql+pymysql://root:ULbzggxgRxVDgRhWnEHtyqTPADoqjNnZ@autorack.proxy.rlwy.net:21845/railway"

# Crear una instancia de la base de datos
database = Database(DATABASE_URL)

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Conectar a la base de datos al iniciar el servidor
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    # Desconectar la base de datos al apagar el servidor
    await database.disconnect()

@app.get("/items/")
async def read_items():
    query = "SELECT * FROM items"
    results = await database.fetch_all(query)
    return results
