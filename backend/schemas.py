from pydantic import BaseModel

class ReservationBase(BaseModel):
    name: str
    subject: str
    department: str
    date: str
    slot: str

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int

    class Config:
        orm_mode = True