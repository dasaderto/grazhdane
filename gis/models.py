from enum import Enum

from geoalchemy2 import Geography
from sqlalchemy import ForeignKey, String, Column, Integer, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from grazhdane.models import TimeStampedModel
from users.models import User


class GkhUkCompany(TimeStampedModel):
    __tablename__ = "gkh_uk_companies"

    company_form = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    director = Column(String)
    address = Column(String)
    phones = Column(String)
    inn = Column(String)
    ogrn = Column(String)
    email = Column(EmailType)
    data = Column(Text)
    member_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    member = relationship(User)


class GkhData(TimeStampedModel):
    __tablename__ = "gkh_data"

    address = Column(String)
    city = Column(String)
    street = Column(String)
    house = Column(String)
    flat_count = Column(Integer)
    square = Column(String)
    floors = Column(String)
    cad_num = Column(String)
    company_name = Column(String)
    coords_lat = Column(String)
    coords_lng = Column(String)
    company_id = Column(Integer, ForeignKey(GkhUkCompany.id, ondelete="CASCADE"), nullable=False)
    company = relationship(GkhUkCompany)
    link = Column(String)


class MarkerType(TimeStampedModel):
    __tablename__ = "marker_types"

    marker_type = Column(String, nullable=False)


class MapLayer(TimeStampedModel):
    __tablename__ = "map_layers"

    class LayerTypes(str, Enum):
        PUBLIC_TYPE = "PUBLIC_TYPE"
        PRIVATE_TYPE = "PRIVATE_TYPE"

    title = Column(String, nullable=False)
    name = Column(String, nullable=False, unique=True)
    object_attrs = Column(JSONB)
    layer_type = Column(String, default=LayerTypes.PRIVATE_TYPE)
    styles = Column(JSONB)
    visible = Column(Boolean, default=True)
    is_hidden = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)


class MapObject(TimeStampedModel):
    __tablename__ = "map_objects"

    point = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    name = Column(String, unique=True, nullable=False)
    marker_type_id = Column(Integer, ForeignKey(MarkerType.id, ondelete="CASCADE"))
    marker_type = relationship(MarkerType)
    map_layer_id = Column(Integer, ForeignKey(MapLayer.id, ondelete="CASCADE"))
    map_layer = relationship(MapLayer)
    json_data = Column(JSONB)
    styles = Column(JSONB)
    object_uid = Column(String, unique=True)


class MarkerHistory(TimeStampedModel):
    __tablename__ = "marker_histories"

    marker_id = Column(Integer, ForeignKey(MapObject.id, ondelete="CASCADE"))
    marker = relationship(MapObject)
    coords = Column(Geography(geometry_type="POINT", srid=4326))
    locate_time = Column(DateTime)
    json_data = Column(JSONB)


class Vehicle(TimeStampedModel):
    __tablename__ = "vehicles"

    sensor_id = Column(Integer)
    category = Column(String)
    vehicle_mark = Column(String)
    vehicle_model = Column(String)
    government_number = Column(String)
