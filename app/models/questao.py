from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base


class Questao(Base):
    __tablename__ = "questoes"

    id = Column(Integer, primary_key=True, index=True)
    ano = Column(Integer, index=True, nullable=False)
    titulo = Column(String, nullable=False)
    area = Column(String(4), index=True, nullable=True)  # LC, CN, CH, MT
    contexto = Column(Text, nullable=True)
    pergunta = Column(Text, nullable=False)
    alternativa_correta = Column(String(1), nullable=False)
    codigo_competencia = Column(Integer, nullable=True)
    descricao_competencia = Column(Text, nullable=True)
    subarea = Column(String, nullable=True, index=True)

    alternativas = relationship(
        "QuestaoAlternativa", back_populates="questao",
        cascade="all, delete-orphan", lazy="selectin",
    )
    arquivos = relationship(
        "QuestaoArquivo", back_populates="questao",
        cascade="all, delete-orphan", lazy="selectin",
    )


class QuestaoAlternativa(Base):
    __tablename__ = "questao_alternativas"

    id = Column(Integer, primary_key=True, index=True)
    questao_id = Column(Integer, ForeignKey("questoes.id", ondelete="CASCADE"), index=True)
    letra = Column(String(1), nullable=False)
    texto = Column(Text, nullable=True)
    arquivo_base64 = Column(Text, nullable=True)

    questao = relationship("Questao", back_populates="alternativas")


class QuestaoArquivo(Base):
    __tablename__ = "questao_arquivos"

    id = Column(Integer, primary_key=True, index=True)
    questao_id = Column(Integer, ForeignKey("questoes.id", ondelete="CASCADE"), index=True)
    arquivo_base64 = Column(Text, nullable=False)

    questao = relationship("Questao", back_populates="arquivos")
