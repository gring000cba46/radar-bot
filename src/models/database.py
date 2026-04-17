"""
Modelos de base de datos con SQLAlchemy
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurar base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/radar_bot.db')

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Usuario(Base):
    """Modelo de usuario"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    nombre = Column(String)
    bank_inicial = Column(Float, default=1000.0)
    bank_actual = Column(Float, default=1000.0)
    roi = Column(Float, default=0.0)
    apuestas_totales = Column(Integer, default=0)
    apuestas_ganadas = Column(Integer, default=0)
    plan = Column(String, default="gratis")
    activo = Column(Boolean, default=True)
    creado = Column(DateTime, default=datetime.utcnow)
    actualizado = Column(DateTime, default=datetime.utcnow)


class Pick(Base):
    """Modelo de pick (recomendación)"""
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, index=True)
    partido = Column(String)
    deporte = Column(String, nullable=True)
    liga = Column(String, nullable=True)
    fecha_hora = Column(DateTime, nullable=True)
    mercado = Column(String)
    opcion = Column(String, nullable=True)
    cuota = Column(Float)
    probabilidad_real = Column(Float)
    probabilidad_implicita = Column(Float)
    valor = Column(String)
    nivel_valor = Column(String, nullable=True)
    confianza = Column(Float)
    expected_value = Column(Float)
    resultado = Column(String, nullable=True)  # GANADO, PERDIDO, PENDIENTE
    alerta_enviada = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_resultado = Column(DateTime, nullable=True)


class Combinada(Base):
    """Modelo de apuesta combinada del usuario"""
    __tablename__ = "combinadas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), index=True)
    picks_ids = Column(Text)    # JSON: [1, 2, 3]
    picks_data = Column(Text)   # JSON: full pick data for history
    cuota_total = Column(Float)
    prob_total = Column(Float)
    monto = Column(Float, nullable=True)
    resultado = Column(String, default='PENDIENTE')  # GANADA, PERDIDA, PENDIENTE
    ganancia = Column(Float, nullable=True)
    creado = Column(DateTime, default=datetime.utcnow)
    finalizado = Column(DateTime, nullable=True)


class Apuesta(Base):
    """Modelo de apuesta individual del usuario"""
    __tablename__ = "apuestas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, index=True)
    pick_id = Column(Integer, nullable=True)
    partido = Column(String)
    mercado = Column(String)
    monto = Column(Float)
    cuota = Column(Float)
    ganada = Column(Boolean, nullable=True)
    ganancia = Column(Float, default=0)
    fecha_apuesta = Column(DateTime, default=datetime.utcnow)
    fecha_resultado = Column(DateTime, nullable=True)


class Movimiento(Base):
    """Modelo de movimiento de bankroll"""
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, index=True)
    tipo = Column(String)  # APUESTA, RECARGA, RETIRO
    monto = Column(Float)
    saldo_anterior = Column(Float)
    saldo_nuevo = Column(Float)
    descripcion = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)


class Estadistica(Base):
    """Modelo de estadísticas diarias"""
    __tablename__ = "estadisticas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, unique=True)
    total_usuarios = Column(Integer)
    usuarios_activos = Column(Integer)
    picks_generados = Column(Integer)
    picks_con_valor = Column(Integer)
    total_apuestas = Column(Integer)
    apuestas_ganadas = Column(Integer)
    roi_promedio = Column(Float)
    yield_promedio = Column(Float)


def init_db():
    """Inicializa la base de datos"""
    os.makedirs('data', exist_ok=True)
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente")


def get_db():
    """Obtiene sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

