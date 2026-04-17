"""
Modelos de base de datos SQLAlchemy
Define estructura de tablas
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Crear base
Base = declarative_base()

# Configurar engine
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/radar_bot.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if 'sqlite' in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Usuario(Base):
    """Modelo de usuario/suscriptor"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    nombre = Column(String)
    email = Column(String, unique=True, index=True)
    saldo = Column(Float, default=1000.0)
    roi = Column(Float, default=0.0)
    creado_en = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    apuestas = relationship("Apuesta", back_populates="usuario")
    bank_movimientos = relationship("BankMovimiento", back_populates="usuario")


class Partido(Base):
    """Modelo de partido deportivo"""
    __tablename__ = "partidos"
    
    id = Column(Integer, primary_key=True, index=True)
    partido_id = Column(String, unique=True, index=True)
    deporte = Column(String)  # Fútbol, Tenis, Basquet
    liga = Column(String)
    local = Column(String)
    visitante = Column(String)
    fecha = Column(DateTime, index=True)
    estado = Column(String, default='pendiente')  # pendiente, en_vivo, finalizado
    resultado = Column(String, nullable=True)  # 1, X, 2
    creado_en = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    cuotas = relationship("CuotaMercado", back_populates="partido")
    picks = relationship("Pick", back_populates="partido")


class CuotaMercado(Base):
    """Modelo de cuota en mercado específico"""
    __tablename__ = "cuotas_mercado"
    
    id = Column(Integer, primary_key=True, index=True)
    partido_id = Column(Integer, ForeignKey("partidos.id"), index=True)
    mercado = Column(String)  # 1, X, 2, Over/Under, Handicap
    cuota = Column(Float)
    probabilidad_implicita = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relación
    partido = relationship("Partido", back_populates="cuotas")


class Pick(Base):
    """Modelo de análisis/pick"""
    __tablename__ = "picks"
    
    id = Column(Integer, primary_key=True, index=True)
    partido_id = Column(Integer, ForeignKey("partidos.id"), index=True)
    mercado = Column(String)
    probabilidad_real = Column(Float)
    probabilidad_implicita = Column(Float)
    valor_detectado = Column(Float)  # Porcentaje de valor
    expected_value = Column(Float)
    recomendacion = Column(String)  # FUERTE, MEDIA, DÉBIL
    confianza = Column(Float, default=0.0)  # 0-1
    creado_en = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relación
    partido = relationship("Partido", back_populates="picks")


class Apuesta(Base):
    """Modelo de apuesta registrada"""
    __tablename__ = "apuestas"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True)
    partido_id = Column(Integer, ForeignKey("partidos.id"), nullable=True)
    mercado = Column(String)
    monto = Column(Float)
    cuota = Column(Float)
    resultado = Column(Boolean, nullable=True)  # True=ganó, False=perdió, None=pendiente
    ganancia = Column(Float, nullable=True)
    creada_en = Column(DateTime, default=datetime.utcnow, index=True)
    resuelta_en = Column(DateTime, nullable=True)
    
    # Relación
    usuario = relationship("Usuario", back_populates="apuestas")


class BankMovimiento(Base):
    """Modelo de movimiento de bankroll"""
    __tablename__ = "bank_movimientos"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True)
    tipo = Column(String)  # apuesta, ganancia, recarga
    monto = Column(Float)
    saldo_antes = Column(Float)
    saldo_despues = Column(Float)
    descripcion = Column(String, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relación
    usuario = relationship("Usuario", back_populates="bank_movimientos")


class Analytics(Base):
    """Modelo de estadísticas y analítica"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), index=True, nullable=True)
    fecha = Column(DateTime, index=True)
    suscriptores_total = Column(Integer, default=0)
    picks_generados = Column(Integer, default=0)
    picks_con_valor = Column(Integer, default=0)
    apuestas_realizadas = Column(Integer, default=0)
    apuestas_ganadas = Column(Integer, default=0)
    roi_promedio = Column(Float, default=0.0)
    yield_promedio = Column(Float, default=0.0)
    metadata = Column(JSON, nullable=True)
    
    creado_en = Column(DateTime, default=datetime.utcnow, index=True)


# Crear todas las tablas
def init_db():
    """Inicializa la base de datos"""
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada")


def get_db():
    """Obtiene sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

