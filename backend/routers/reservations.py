from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from backend.models import Reservation

from backend import crud, models, schemas
from backend.database import get_db

router = APIRouter()

# Slot configuration
department_slots = {
    "it": {"days": ["Saturday", "Tuesday"], "start": 9, "duration": 2, "slots": 3},
    "industrial": {"days": ["Sunday", "Wednesday"], "start": 9, "duration": 1, "slots": 6},
    "health": {"days": ["Monday", "Thursday"], "start": 9, "duration": 1, "slots": 6},
}


# Generate slots for a given department and date
def generate_slots(department: str, date_str: str, db: Session) -> List[str]:
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    config = department_slots.get(department)
    if not config:
        return []

    day_name = date.strftime("%A")
    if day_name not in config["days"]:
        return []

    slots = []
    for i in range(config["slots"]):
        start_hour = config["start"] + i * config["duration"]
        end_hour = start_hour + config["duration"]
        slots.append(f"{start_hour}:00 - {end_hour}:00")

    # Check reserved slots from database
    reserved = db.query(models.Reservation).filter_by(department=department, date=date_str).all()
    reserved_slots = {r.slot for r in reserved}

    return [slot for slot in slots if slot not in reserved_slots]


# Endpoint to get available slots
@router.get("/slots/available", response_model=List[str])
def get_available_slots(
    department: str = Query(...),
    date: str = Query(...),
    db: Session = Depends(get_db)
):
    return generate_slots(department, date, db)


# Endpoint to book a slot
@router.post("/slots/book")
def book_slot(
    reservation: schemas.ReservationCreate,
    db: Session = Depends(get_db)
):
    existing = crud.get_reservation(db, reservation.department, reservation.date, reservation.slot)
    if existing:
        raise HTTPException(status_code=400, detail="This time slot is already booked.")

    created = crud.create_reservation(db, reservation)
    return {
        "message": f"{created.name}, you have successfully booked {created.slot} on {created.date}"
    }


# Endpoint to view all reservations
@router.get("/slots/reservations", response_model=List[schemas.Reservation])
def view_reservations(db: Session = Depends(get_db)):
    return crud.get_reservations(db)


# Endpoint to export reservations to Excel
@router.get("/slots/export_excel")
def export_excel(db: Session = Depends(get_db)):
    reservations = crud.get_reservations(db)
    if not reservations:
        raise HTTPException(status_code=404, detail="No reservations found.")

    # Convert to DataFrame
    data = [
        {
            "name": r.name,
            "subject": r.subject,
            "department": r.department,
            "date": r.date,
            "slot": r.slot
        }
        for r in reservations
    ]
    df = pd.DataFrame(data)

    # Write to Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Reservations")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=reservations.xlsx"}
    )


@router.delete("/slots/reservations/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    db.delete(reservation)
    db.commit()
    return {"message": "Reservation deleted successfully"}
    

@router.delete("/reservations")
def delete_all_reservations(db: Session = Depends(get_db)):
    deleted_count = db.query(Reservation).delete()
    db.commit()
    return {"message": f"Deleted {deleted_count} reservations."}