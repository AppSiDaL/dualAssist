# main.py

from fastapi import FastAPI


from pydantic import BaseModel

class Item(BaseModel):
    lastname: str
    time: str
app = FastAPI()

@app.post("/")
async def root(item: Item):
    return {
        "numeroControl": item.lastname,
        "time": item.time
    }