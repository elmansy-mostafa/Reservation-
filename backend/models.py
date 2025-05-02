from sqlalchemy import Column, Integer, String
from backend.database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    department = Column(String, nullable=False)
    date = Column(String, nullable=False)  # Format: YYYY-MM-DD
    slot = Column(String, nullable=False)