from sqlalchemy import Column, String, Boolean

from grazhdane.models import TimeStampedModel


class MenuItem(TimeStampedModel):
    __tablename__ = 'menu_items'

    name = Column(String, nullable=False)
    link = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)