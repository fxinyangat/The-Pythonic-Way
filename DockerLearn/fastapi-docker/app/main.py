from fastapi import FastAPI, HTTPException
from typing import Optional
import uvicorn


app = FastAPI()

items = {
    1: {"item_id": 1, "desc": "first item 1"},
    2: {"item_id": 2, "desc": "second item 2"},
    3: {"item_id": 3, "desc": "third item 3"},
    4: {"item_id": 4, "desc": "fourth item 4"},
    5: {"item_id": 5, "desc": "fifth item 5"},
}


@app.get("/")
def read_root():
    return {"Hello World"}

@app.get('/items')
def read_items():
    return list(items.values())

@app.get("/items/{item_id}")
def read_item(item_id:int, q:Optional[int] = None):
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    result = items[item_id]
    
    if q:
        result = {**result, "q": q}
    return result


if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")