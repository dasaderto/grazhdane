from enum import Enum
from typing import List

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from grazhdane.models import TimeStampedModel


class SocialGroup(TimeStampedModel):
    __tablename__ = 'social_groups'

    name = Column(String(150), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    users = relationship("User", back_populates="social_group")


class SexTypes(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    NOT_CHOSEN = "NOT_CHOSEN"


class UserRoles(str, Enum):
    ADMIN_ROLE = 'ADMIN_ROLE'
    CITY_HEAD_ROLE = 'CITY_HEAD_ROLE'
    CONTROL_ROLE = 'CONTROL_ROLE'
    DEPARTMENT_HEAD_ROLE = 'DEPARTMENT_HEAD_ROLE'
    MODERATOR_ROLE = 'MODERATOR_ROLE'
    EMPLOYEE_ROLE = 'EMPLOYEE_ROLE'
    SIMPLE_USER_ROLE = 'SIMPLE_USER_ROLE'
    BUSINESS_ROLE = 'BUSINESS_ROLE'


class User(TimeStampedModel):
    __tablename__ = 'users'

    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150))
    patronymic = Column(String(150))
    email = Column(EmailType, unique=True)
    email_verified_at = Column(DateTime)
    phone = Column(String(50))
    sex = Column(String)
    position = Column(String)
    password = Column(String)
    activate_token = Column(String)
    is_active = Column(Boolean, default=True)
    social_group_id = Column(Integer, ForeignKey(SocialGroup.id, ondelete="CASCADE"))
    social_group = relationship(SocialGroup, back_populates="users")
    roles = Column(ARRAY(String))
    notify_active = Column(Boolean, default=False)
    birthday = Column(DateTime)
    address = Column(String)

    attachments = relationship("Attachment", back_populates="creator")
    comments = relationship('Comment', back_populates="creator")
    providers = relationship('Provider', back_populates="user")
    service_members = relationship('ServiceMember', back_populates="member")

    def remove_role(self, role: UserRoles):
        del self.roles[self.roles.index(role)]
        return self.roles

    def assign_role(self, role: UserRoles):
        self.roles.append(role)

    def has_role(self, role: UserRoles) -> bool:
        return role in self.roles

    def has_any_role(self, roles: List[UserRoles]) -> bool:
        return bool(set(roles) & set(self.roles))


class Attachment(TimeStampedModel):
    __tablename__ = 'attachments'

    link = Column(String, nullable=False)
    meta = Column(String)
    name = Column(String)
    creator_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    creator = relationship(User, back_populates="attachments")
    owner_type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'attachments',
        'polymorphic_on': owner_type
    }


class Comment(TimeStampedModel):
    __tablename__ = 'comments'

    parent_id = Column(Integer)
    body = Column(String(700))
    is_hidden = Column(Boolean, default=False)
    creator_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    creator = relationship(User, back_populates="comments")
    owner_type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'comments',
        'polymorphic_on': owner_type
    }


class Provider(TimeStampedModel):
    __tablename__ = 'providers'

    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    user = relationship(User, back_populates="providers")
    provider_id = Column(String)
    provider_name = Column(String)


class Department(TimeStampedModel):
    __tablename__ = 'departments'

    name = Column(String(150), nullable=False, unique=True)
    director_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    director = relationship(User, foreign_keys=[director_id])
    control_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    control = relationship(User, foreign_keys=[control_id])

    employees = relationship('Employee', back_populates="department")


class Employee(TimeStampedModel):
    __tablename__ = 'employees'

    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    user = relationship(User)
    department_id = Column(Integer, ForeignKey(Department.id, ondelete="CASCADE"), nullable=False)
    department = relationship(Department, back_populates="employees")
    position = Column(String)


class Deputy(TimeStampedModel):
    __tablename__ = 'deputies'

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=False)
    district = Column(String, nullable=False)
    phone = Column(String)


class ServiceMember(TimeStampedModel):
    __tablename__ = 'service_members'

    name = Column(String, nullable=False)
    director_name = Column(String)
    email = Column(EmailType, unique=True, nullable=False)
    member_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    member = relationship(User, back_populates="service_members")
