from sqlalchemy.orm import Session
from backend import models, schemas

def get_reservation(db: Session, department: str, date: str, slot: str):
    return db.query(models.Reservation).filter_by(
        department=department,
        date=date,
        slot=slot
    ).first()

def create_reservation(db: Session, reservation: schemas.ReservationCreate):
    db_reservation = models.Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def get_reservations(db: Session):
    return db.query(models.Reservation).all()