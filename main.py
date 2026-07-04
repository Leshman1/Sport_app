from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal, engine, Base
import models
import schemas
import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Привет! Это приложение для тренировок"}


@app.post("/register")
def register(user: schemas.User, db: Session = Depends(get_db)):
    existing_user = db.query(models.UserDB).filter(models.UserDB.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.UserDB(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.UserDB).filter(models.UserDB.username == form_data.username).first()
    if not db_user or not pwd_context.verify(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    access_token = auth.create_access_token(data={"sub": db_user.username, "user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/workouts")
def get_workouts(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    return db.query(models.WorkoutDB).filter(models.WorkoutDB.user_id == current_user["user_id"]).all()


@app.post("/workouts")
def create_workout(workout: schemas.Workout, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    db_workout = models.WorkoutDB(**workout.dict(), user_id=current_user["user_id"])
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@app.get("/workouts/{workout_id}")
def get_workout(workout_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    workout = db.query(models.WorkoutDB).filter(
        models.WorkoutDB.id == workout_id,
        models.WorkoutDB.user_id == current_user["user_id"]
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    return workout


@app.put("/workouts/{workout_id}")
def update_workout(workout_id: int, workout: schemas.Workout, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    db_workout = db.query(models.WorkoutDB).filter(
        models.WorkoutDB.id == workout_id,
        models.WorkoutDB.user_id == current_user["user_id"]
    ).first()
    if not db_workout:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    db_workout.type = workout.type
    db_workout.duration = workout.duration
    db_workout.calories = workout.calories
    db.commit()
    db.refresh(db_workout)
    return db_workout


@app.delete("/workouts/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
    workout = db.query(models.WorkoutDB).filter(
        models.WorkoutDB.id == workout_id,
        models.WorkoutDB.user_id == current_user["user_id"]
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    db.delete(workout)
    db.commit()
    return {"message": "Тренировка удалена"}