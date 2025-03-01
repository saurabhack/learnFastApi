from typing import List
from fastapi import FastAPI,Depends,status,Response,HTTPException
from pydantic import BaseModel
from . import schemas,model,hashing
from .database import engine,SessionLocal
from sqlalchemy.orm import Session

app=FastAPI()

model.Base.metadata.create_all(bind=engine)

async def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/blog")
async def create(request:schemas .Blog,db:Session=Depends(get_db)):
    new_blog=model.Blog(title=request.title,body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get("/blogs",response_model=List[schemas.ShowBlog])
def allBolgs(db:Session=Depends(get_db)):
    blogs=db.query(model.Blog).all()
    return blogs

@app.get("/blogs/{id}",status_code=200,response_model=schemas.ShowBlog)
def show(id,response:Response,db:Session=Depends(get_db)):
    blog=db.query(model.Blog).filter(model.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="not found")
    return blog

@app.delete("/Blog/{id}",status_code=status.HTTP_204_NO_CONTENT)
def deleteData(id,db:Session=Depends(get_db)):
    blog=db.query(model.Blog).filter(model.Blog.id==id).delete(synchronize_session=False)
    db.commit()
    print(blog)
    return {'message':'deleted successfully'}

@app.put("/blog/{id}",status_code=status.HTTP_202_ACCEPTED)
def update(id,request:schemas.Blog,db:Session=Depends(get_db)):
    updateBlog=db.query(model.Blog).filter(model.Blog.id==id).update({model.Blog.title:request.title,model.Blog.body:request.body})
    db.commit()
    print(updateBlog)
    return "updated successfully"

@app.post('/user',response_model=schemas.showUser)
def create_user(request:schemas.User,db:Session=Depends(get_db)):
    new_user=model.User(name=request.name,email=request.email,password=hashing.Hash.encrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/user/{id}",response_model=schemas.showUser,tags=['user'])
def get_users(id:int,db:Session=Depends(get_db)):
    user=db.query(model.User).filter(model.User.id==id).first()
    if not user:
        return {"message":"user does not exists"}
    else:
        return user