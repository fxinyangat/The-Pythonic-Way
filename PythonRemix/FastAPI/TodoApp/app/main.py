from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

import crud,models,schemas
from database import sessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = sessionLocal()

    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/users/",response_model=schemas.User)
def post_user(user:schemas.UserCreate, db:db_dependency):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db,user=user)


@app.get("/users/", response_model=list[schemas.User])
def get_users(*, skip:int=0, limit:int=0, db:db_dependency):
    users = crud.get_users(db,skip=skip,limit=limit)
    return users


@app.get("/users/{user_id}/",response_model=schemas.User)
def get_user(user_id:int, db:db_dependency):
    db_user = crud.get_user(db,user_id =user_id )
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/todos/",response_model=schemas.Todo)
def post_todo_for_user(user_id:int, todo:schemas.TodoCreate, db:db_dependency):
    return crud.create_user_todo(db=db,user_id=user_id, todo=todo)


@app.get("/todos/", response_model=list[schemas.Todo])
def get_todos(*, skip:int=0,limit:int=100,db:db_dependency):
    todos = crud.get_todos(db,skip=skip,limit=limit)
    return todos
