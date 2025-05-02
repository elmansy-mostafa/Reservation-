import pandas as pd
from fastapi.responses import FileResponse
from typing import List
from backend.models import Reservation

def export_to_excel(reservations: List[Reservation]):
    data = [{
        "Name": r.name,
        "Subject": r.subject,
        "Department": r.department,
        "Date": r.date,
        "Slot": r.slot
    } for r in reservations]

    df = pd.DataFrame(data)
    file_path = "reservations_export.xlsx"
    df.to_excel(file_path, index=False)

    return FileResponse(path=file_path, filename=file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')