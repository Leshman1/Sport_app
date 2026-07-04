from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)


class WorkoutDB(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    duration = Column(Integer)
    calories = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
