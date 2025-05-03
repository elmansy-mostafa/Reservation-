from openpyxl import Workbook
from collections import defaultdict
from fastapi.responses import FileResponse
from typing import List
from backend.models import Reservation

def export_reservations_by_date(reservations: List[Reservation]):
    grouped = defaultdict(list)
    for r in reservations:
        grouped[str(r.date)].append({
            "Name": r.name,
            "Subject": r.subject,
            "Department": r.department,
            "Date": str(r.date),
            "Slot": r.slot
        })

    wb = Workbook()
    wb.remove(wb.active)

    for date, data in grouped.items():
        ws = wb.create_sheet(title=date)
        headers = list(data[0].keys())
        ws.append(headers)
        for row in data:
            ws.append(list(row.values()))

        # Optional: Add Excel filter
        ws.auto_filter.ref = ws.dimensions

    file_path = "reservations_by_date.xlsx"
    wb.save(file_path)

    return FileResponse(path=file_path, filename=file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')