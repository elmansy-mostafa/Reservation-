from datetime import datetime, timedelta

# minutes per slot for each department
DEPARTMENT_SLOT_DURATION = {
    "it": 120,           # IT dept: 2-hour slots
    "industrial": 60,    # Fac. of Industrial: 1-hour slots
    "health": 60,        # Fac. of Health Sci.: 1-hour slots
}

def generate_slots_for_department(department: str):
    """
    Always returns all possible slots between 09:00 and 15:00
    for the given department.
    """
    # parse a dummy date so we can loop on times
    start = datetime.strptime("09:00", "%H:%M")
    end   = datetime.strptime("15:00", "%H:%M")
    duration = DEPARTMENT_SLOT_DURATION.get(department, 60)

    slots = []
    while start + timedelta(minutes=duration) <= end:
        end_time = start + timedelta(minutes=duration)
        slots.append(f"{start.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        start = end_time

    return slots