from pydantic import BaseModel


class Workout(BaseModel):
    type: str
    duration: int
    calories: int


class User(BaseModel):
    username: str
    password: str
