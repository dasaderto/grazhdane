from geoalchemy2 import Geography
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from gis.models import MapObject
from grazhdane.models import TimeStampedModel
from users.models import User


class Initiative(TimeStampedModel):
    __tablename__ = "initiatives"

    creator_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    creator = relationship(User)
    address_to = Column(String, nullable=False)
    locate_address = Column(String)
    locate = Column(Geography(geometry_type="POINT", srid=4326))
    task = Column(String(700), nullable=False)
    importance = Column(String, nullable=False)
    like = Column(Integer, default=0)
    dislike = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    users_voted = Column(JSONB)
    is_hidden = Column(Boolean, default=False)


class InitiativeConsideration(TimeStampedModel):
    __tablename__ = "initiative_considerations"

    published_by_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    published_by = relationship(User)
    responsible_person_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    responsible_person = relationship(User)
    initiative_id = Column(Integer, ForeignKey(Initiative.id, ondelete="CASCADE"))
    initiative = relationship(Initiative)
    result = Column(String(700))
    comment = Column(String(50))
