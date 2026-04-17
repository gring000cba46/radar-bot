"""
Modelos de base de datos con SQLAlchemy
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
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
    saldo = Column(Float, default=0.0)          # bank_actual (saldo corriente)
    saldo_inicial = Column(Float, default=0.0)  # bank_inicial (capital configurado)
    plan = Column(String, default="gratis")
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    ultima_actividad = Column(DateTime, default=datetime.utcnow)

    @property
    def bank_configurado(self) -> bool:
        return self.saldo_inicial > 0

    @property
    def roi(self) -> float:
        if self.saldo_inicial == 0:
            return 0.0
        return ((self.saldo - self.saldo_inicial) / self.saldo_inicial) * 100


class Pick(Base):
    """Modelo de pick (recomendación)"""
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, index=True)
    partido = Column(String)
    liga = Column(String)
    deporte = Column(String, default="Fútbol")
    mercado = Column(String)
    opcion = Column(String, nullable=True)
    cuota = Column(Float)
    probabilidad_real = Column(Float)
    probabilidad_implicita = Column(Float)
    valor = Column(String)
    confianza = Column(Float)
    expected_value = Column(Float)
    hora_partido = Column(String, nullable=True)    # "18:00"
    resultado = Column(String, nullable=True)       # GANADO, PERDIDO, PENDIENTE
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_resultado = Column(DateTime, nullable=True)


class Apuesta(Base):
    """Modelo de apuesta del usuario"""
    __tablename__ = "apuestas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(String, index=True)   # telegram_id
    pick_id = Column(Integer, nullable=True)
    partido = Column(String)
    mercado = Column(String)
    monto = Column(Float)
    cuota = Column(Float)
    resultado = Column(String, nullable=True)  # GANADO, PERDIDO, PENDIENTE
    ganancia = Column(Float, default=0.0)
    fecha_apuesta = Column(DateTime, default=datetime.utcnow)
    fecha_resultado = Column(DateTime, nullable=True)


class Combo(Base):
    """Modelo de apuesta combinada"""
    __tablename__ = "combos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(String, index=True)   # telegram_id
    picks_json = Column(Text)                  # JSON list of pick data
    cuota_combo = Column(Float)
    monto = Column(Float, nullable=True)
    resultado = Column(String, nullable=True)  # GANADO, PERDIDO, PENDIENTE
    ganancia = Column(Float, default=0.0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_resultado = Column(DateTime, nullable=True)


class Movimiento(Base):
    """Modelo de movimiento de bankroll"""
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(String, index=True)   # telegram_id
    tipo = Column(String)                      # APUESTA, RECARGA, RETIRO
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


def get_or_create_usuario(db, telegram_id: str, nombre: str = "") -> Usuario:
    """Obtiene o crea un usuario"""
    usuario = db.query(Usuario).filter(Usuario.telegram_id == str(telegram_id)).first()
    if not usuario:
        usuario = Usuario(
            telegram_id=str(telegram_id),
            nombre=nombre,
            saldo=0.0,
            saldo_inicial=0.0,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario

