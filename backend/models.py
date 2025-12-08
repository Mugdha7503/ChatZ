# backend/models.py
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class FileInfo(Base):
    __tablename__ = "file_info"

    file_id = Column(String, primary_key=True)
    file_name = Column(String, unique=True, nullable=False)
    embedding_status = Column(Boolean, default=False)
