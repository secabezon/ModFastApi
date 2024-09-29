from pydantic import BaseModel

class Car(BaseModel):
    Id:int
    model:str
    year:int
    motor_type:str
    running:str
    wheel:str
    color:str
    type:str
    status:str
    motor_volume:float


    