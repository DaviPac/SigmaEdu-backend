from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from app.database.session import Base


class Desempenho(Base):
    __tablename__ = "desempenhos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    questao_id = Column(Integer, nullable=False)
    acertou = Column(Boolean, nullable=False)
    area = Column(String(4), nullable=True, index=True)
    subarea = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
