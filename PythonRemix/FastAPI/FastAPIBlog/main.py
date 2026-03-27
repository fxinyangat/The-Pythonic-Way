from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
# data validation
class PostsBase(BaseModel):
    title: str
    content: str
    user_id: int

class UserBase(BaseModel):
    username: str

# create db connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create annoation for db for dependency injection

db_dependency = Annotated[Session, Depends(get_db)]

# CRUD on Posts Table
@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post:PostsBase, db: db_dependency): # type: ignore
    db_post = models.Post(**post.model_dump())
    db.add(db_post)
    db.commit()

@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post Not Found")
    return post

@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post Not Found")
    db.delete(db_post)
    db.commit()


# CRUD Operations on the users table.

# Get all students
@app.post("/users/")
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()

@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user


