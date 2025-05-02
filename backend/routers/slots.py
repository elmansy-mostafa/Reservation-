from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
from pydantic import BaseModel
import io
import pandas as pd
from fastapi.responses import StreamingResponse
from backend.database import bookings_collection  # adjust this path if needed

router = APIRouter()

# Slot configuration
department_slots = {
    "it": {"days": ["Saturday", "Tuesday"], "start": 9, "duration": 2, "slots": 3},
    "industrial": {"days": ["Sunday", "Wednesday"], "start": 9, "duration": 1, "slots": 6},
    "health": {"days": ["Monday", "Thursday"], "start": 9, "duration": 1, "slots": 6},
}

class BookingRequest(BaseModel):
    name: str
    subject: str
    department: str
    date: str  # "YYYY-MM-DD"
    slot: str  # "HH:00 - HH:00"

# Generate slots for a given department and date
def generate_slots(department: str, date_str: str) -> List[str]:
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

    # Check booked slots from MongoDB
    booked_cursor = bookings_collection.find({"department": department, "date": date_str})
    booked_slots = [booking["slot"] for booking in booked_cursor]

    available = [slot for slot in slots if slot not in booked_slots]
    return available

# Endpoint to get available slots
@router.get("/slots/available", response_model=List[str])
async def get_available_slots(
    department: str = Query(...),
    date: str = Query(...)
):
    return generate_slots(department, date)

# Endpoint to book a slot
@router.post("/slots/book")
async def book_slot(request: BookingRequest):
    # Check for existing booking in MongoDB
    existing = bookings_collection.find_one({
        "department": request.department,
        "date": request.date,
        "slot": request.slot
    })

    if existing:
        raise HTTPException(status_code=400, detail="This time slot is already booked.")

    # Save booking to MongoDB
    bookings_collection.insert_one(request.dict())

    return {
        "message": f"{request.name}, you have successfully booked {request.slot} on {request.date}"
    }

# Endpoint to export bookings to Excel
@router.get("/slots/export_excel")
async def export_excel():
    all_bookings = list(bookings_collection.find({}, {"_id": 0}))  # Exclude MongoDB _id
    if not all_bookings:
        raise HTTPException(status_code=404, detail="No bookings found.")

    df = pd.DataFrame(all_bookings)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Bookings")

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=bookings.xlsx"}
    )
