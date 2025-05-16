from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func

# Socios
class Socio(Base):
    __tablename__ = 'socios'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    dni = Column(String(20), nullable=True)
    contrasenya = Column(String(255), nullable=True)

    # Relaciones
    reservas_hotel = relationship("ReservaHotel", back_populates="socio")
    reservas_pistas = relationship("ReservaPista", back_populates="socio")
    reservas_restaurante = relationship("ReservaRestaurante", back_populates="socio")
    reservas_spa = relationship("ReservaSpa", back_populates="socio")
    favoritos = relationship("Favorito", back_populates="socio")


# Hoteles
class Hotel(Base):
    __tablename__ = 'hoteles'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    ubicacion = Column(Text, nullable=True)
    disponibilidad = Column(Boolean, default=True)
    valoracion = Column(Float, nullable=True)
    img_url = Column(String(255), nullable=True)  # Añadido campo img_url
    descripcion = Column(Text, nullable=True)     # Añadido campo descripcion
    detalles = Column(Text, nullable=True)        # NUEVO: campo detalles

    # Relaciones
    habitaciones = relationship("Habitacion", back_populates="hotel")
    reservas_hotel = relationship("ReservaHotel", back_populates="hotel")


class Habitacion(Base):
    __tablename__ = 'habitaciones'

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey('hoteles.id'))
    tipo = Column(String(50), nullable=True)
    disponibilidad = Column(Boolean, default=True)

    # Relaciones
    hotel = relationship("Hotel", back_populates="habitaciones")
    reservas_hotel = relationship("ReservaHotel", back_populates="habitacion")


# Restaurantes
class Restaurante(Base):
    __tablename__ = 'restaurantes'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    ubicacion = Column(Text, nullable=True)
    valoracion = Column(Float, nullable=True)
    descripcion = Column(Text, nullable=True)     # Ya existente
    disponibilidad = Column(Boolean, default=True)
    img_url = Column(String(255), nullable=True)  # Ya existente
    detalles = Column(Text, nullable=True)        # NUEVO: campo detalles

    # Relaciones
    servicios = relationship("ServicioRestaurante", back_populates="restaurante")
    reservas_restaurante = relationship("ReservaRestaurante", back_populates="restaurante")


class ServicioRestaurante(Base):
    __tablename__ = 'servicio_restaurante'

    id = Column(Integer, primary_key=True, index=True)
    restaurante_id = Column(Integer, ForeignKey('restaurantes.id'))
    tipo_menu = Column(String(50), nullable=True)
    tipo_cocina = Column(String(100), nullable=True)
    ambiente = Column(String(100), nullable=True)
    terraza = Column(Boolean, default=False)

    # Relación con Restaurante
    restaurante = relationship("Restaurante", back_populates="servicios")


# Pistas
class Pista(Base):
    __tablename__ = 'pistas'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    ubicacion = Column(Text, nullable=True)
    disponibilidad = Column(Boolean, default=True)
    valoracion = Column(Float, nullable=True)
    img_url = Column(String(255), nullable=True)  # Añadido campo img_url
    descripcion = Column(Text, nullable=True)     # Añadido campo descripcion
    detalles = Column(Text, nullable=True)        # NUEVO: campo detalles

    # Relaciones
    servicios = relationship("ServicioPistas", back_populates="pista")
    reservas_pistas = relationship("ReservaPista", back_populates="pista")


class ServicioPistas(Base):
    __tablename__ = 'servicio_pistas'

    id = Column(Integer, primary_key=True, index=True)
    pista_id = Column(Integer, ForeignKey('pistas.id'))
    tipo_pista = Column(String(50), nullable=True)
    numero_personas = Column(Integer, nullable=True)
    material = Column(String(100), nullable=True)
    tiempo_disponible = Column(String(50), nullable=True)

    # Relación con Pista
    pista = relationship("Pista", back_populates="servicios")


# Spa
class Spa(Base):
    __tablename__ = 'spa'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    descripcion = Column(Text, nullable=True)     # Ya existente
    ubicacion = Column(Text, nullable=True)
    disponibilidad = Column(Boolean, default=True)
    valoracion = Column(Float, nullable=True)
    img_url = Column(String(255), nullable=True)  # Añadido campo img_url
    detalles = Column(Text, nullable=True)        # NUEVO: campo detalles

    # Relaciones
    servicios = relationship("ServicioSpa", back_populates="spa")
    reservas_spa = relationship("ReservaSpa", back_populates="spa")


class ServicioSpa(Base):
    __tablename__ = 'servicio_spa'

    id = Column(Integer, primary_key=True, index=True)
    spa_id = Column(Integer, ForeignKey('spa.id'))
    tipo_servicio = Column(String(100), nullable=True)
    duracion = Column(Integer, nullable=True)

    # Relación con Spa
    spa = relationship("Spa", back_populates="servicios")


# Reservas
class ReservaHotel(Base):
    __tablename__ = 'reservas_hotel'

    id = Column(Integer, primary_key=True, index=True)
    socio_id = Column(Integer, ForeignKey('socios.id'))
    hotel_id = Column(Integer, ForeignKey('hoteles.id'))  # Nueva columna para el ID del hotel
    habitacion_id = Column(Integer, ForeignKey('habitaciones.id'))
    fecha_entrada = Column(Date, nullable=True)
    fecha_salida = Column(Date, nullable=True)

    # Relaciones
    socio = relationship("Socio", back_populates="reservas_hotel")
    hotel = relationship("Hotel", back_populates="reservas_hotel")  # Relación directa con Hotel
    habitacion = relationship("Habitacion", back_populates="reservas_hotel")

class ReservaPista(Base):
    __tablename__ = 'reservas_pistas'

    id = Column(Integer, primary_key=True, index=True)
    socio_id = Column(Integer, ForeignKey('socios.id'))
    pista_id = Column(Integer, ForeignKey('pistas.id'))  # Nueva columna para el ID de la pista
    servicio_pista_id = Column(Integer, ForeignKey('servicio_pistas.id'))
    fecha = Column(Date, nullable=True)

    # Relaciones
    socio = relationship("Socio", back_populates="reservas_pistas")
    pista = relationship("Pista", back_populates="reservas_pistas")  # Relación directa con Pista

class ReservaRestaurante(Base):
    __tablename__ = 'reservas_restaurante'

    id = Column(Integer, primary_key=True, index=True)
    socio_id = Column(Integer, ForeignKey('socios.id'))
    restaurante_id = Column(Integer, ForeignKey('restaurantes.id'))  # Nueva columna para el ID del restaurante
    servicio_restaurante_id = Column(Integer, ForeignKey('servicio_restaurante.id'))
    fecha = Column(Date, nullable=True)
    hora = Column(Time, nullable=True)

    # Relaciones
    socio = relationship("Socio", back_populates="reservas_restaurante")
    restaurante = relationship("Restaurante", back_populates="reservas_restaurante")  # Relación directa con Restaurante

class ReservaSpa(Base):
    __tablename__ = 'reservas_spa'

    id = Column(Integer, primary_key=True, index=True)
    socio_id = Column(Integer, ForeignKey('socios.id'))
    spa_id = Column(Integer, ForeignKey('spa.id'))  # Nueva columna para el ID del spa
    servicio_spa_id = Column(Integer, ForeignKey('servicio_spa.id'))
    fecha = Column(Date, nullable=True)
    hora = Column(Time, nullable=True)

    # Relaciones
    socio = relationship("Socio", back_populates="reservas_spa")
    spa = relationship("Spa", back_populates="reservas_spa")  # Relación directa con Spa

# Favoritos
class Favorito(Base):
    __tablename__ = 'favoritos'

    id = Column(Integer, primary_key=True, index=True)
    socio_id = Column(Integer, ForeignKey('socios.id'))
    tipo = Column(String(50), nullable=True)
    referencia_id = Column(Integer, nullable=True)
    fecha_agregado = Column(Date, default=func.current_date())
    
# Relación con Socio
    socio = relationship("Socio", back_populates="favoritos")


# Locales Populares
class LocalPopular(Base):
    __tablename__ = 'locales_populares'

    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, nullable=False)
    popularidad = Column(Float, nullable=False)  # Cambiado a FLOAT
