import enum

from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, SmallInteger, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from grazhdane.models import TimeStampedModel
from users.models import User, Department, Deputy, Attachment


class AppealStatuses(str, enum.Enum):
    MODERATION = 'MODERATION'
    CONSIDERATION = 'CONSIDERATION'
    IN_WORK = 'IN_WORK'
    CLOSE_BOSS_CONFIRMATION = 'CLOSE_BOSS_CONFIRMATION'
    CLOSE_CONTROL_CONFIRMATION = 'CLOSE_CONTROL_CONFIRMATION'
    REJECTED = 'REJECTED'
    RESOLVED = 'RESOLVED'
    NEED_READ = 'NEED_READ'


class AppealStatus(TimeStampedModel):
    __tablename__ = 'appeal_statuses'

    title = Column(String, nullable=False)
    status_const: Column = Column(Enum(AppealStatuses), nullable=False)


class AppealTheme(TimeStampedModel):
    __tablename__ = 'appeal_themes'

    theme = Column(String)
    department_id = Column(Integer, ForeignKey(Department.id, ondelete="CASCADE"))
    department = relationship(Department)
    is_hidden = Column(Boolean, default=False)


class UserAppealAttachment(Attachment):
    __tablename__ = 'user_appeal_attachments'
    id = Column(Integer, ForeignKey(Attachment.id), primary_key=True)
    user_appeal_id = Column(Integer, ForeignKey("user_appeals.id"))
    user_appeal = relationship("UserAppeal", back_populates='attachments')

    __mapper_args__ = {
        'polymorphic_identity': 'user_appeal_attachments',
    }


class UserAppeal(TimeStampedModel):
    __tablename__ = "user_appeals"

    attachments = relationship(UserAppealAttachment, back_populates="user_appeal")

    creator_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    creator = relationship(User, foreign_keys=[creator_id])

    appeal_theme_id = Column(Integer, ForeignKey(AppealTheme.id, ondelete="CASCADE"))
    appeal_theme = relationship(AppealTheme)

    executor_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    executor = relationship(User, foreign_keys=[executor_id])

    deputy_id = Column(Integer, ForeignKey(Deputy.id, ondelete="CASCADE"))
    deputy = relationship(Deputy)

    status_id = Column(Integer, ForeignKey(AppealStatus.id, ondelete="CASCADE"))
    status = relationship(AppealStatus)

    problem_body = Column(String(700), nullable=False)
    address = Column(String)
    post_address = Column(String)
    note = Column(String)
    is_active = Column(Boolean, default=False)
    rate = Column(SmallInteger, default=0)
    dispatcher_create = Column(Integer)
    is_hidden = Column(Boolean, default=False)
    expired_at = Column(DateTime)
    users_voted = Column(ARRAY(Integer))
    locate = Column(Geometry('POINT'))


class AppealUser(TimeStampedModel):
    __tablename__ = 'appeal_users'

    appeal_id = Column(Integer, ForeignKey(UserAppeal.id, ondelete="CASCADE"), nullable=False)
    appeal = relationship(UserAppeal)

    employee_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    employee = relationship(User, foreign_keys=[employee_id])

    creator_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    creator = relationship(User, foreign_keys=[creator_id])
    comment = Column(String)
    closed_date = Column(DateTime)
    is_private = Column(Boolean, default=False)


class AppealHistoryAttachment(Attachment):
    __tablename__ = 'appeal_history_attachments'
    id = Column(Integer, ForeignKey(Attachment.id), primary_key=True)
    appeal_history_id = Column(Integer, ForeignKey("appeal_history.id"))
    appeal_history = relationship("AppealHistory", back_populates='attachments')

    __mapper_args__ = {
        'polymorphic_identity': 'appeal_history_attachments',
    }


class AppealHistoryTypes(str, enum.Enum):
    APPEAL_CREATED = 'APPEAL_CREATED'
    APPEAL_TO_WORK = 'APPEAL_TO_WORK'
    APPEAL_MODERATION = 'APPEAL_MODERATION'
    DEPARTMENT_ASSIGNED = 'DEPARTMENT_ASSIGNED'
    APPEAL_DELEGATE = 'APPEAL_DELEGATE'
    APPEAL_RESOLVED = 'APPEAL_RESOLVED'
    APPEAL_REJECTED = 'REJECTED'
    APPEAL_READ = 'APPEAL_READ'
    GOROD_CLOSED = 'GOROD_CLOSED'
    BOSS_CLOSED = 'BOSS_CLOSED'
    BOSS_REJECTED = 'BOSS_REJECTED'
    CONTROL_REJECTED = 'CONTROL_REJECTED'
    DEPARTMENT_CONNECTED = 'DEPARTMENT_CONNECTED'
    ORGANIZATION_CONNECTED = 'ORGANIZATION_CONNECTED'
    DEPUTY_CONNECTED = 'DEPUTY_CONNECTED'
    NEW_MESSAGE = 'NEW_MESSAGE'
    COMPANY_CONNECTED = 'COMPANY_CONNECTED'


class AppealHistory(TimeStampedModel):
    __tablename__ = 'appeal_history'

    appeal_id = Column(Integer, ForeignKey(UserAppeal.id, ondelete="CASCADE"), nullable=False)
    appeal = relationship(UserAppeal)

    creator_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    creator = relationship(User, foreign_keys=[creator_id])

    connected_person_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    connected_person = relationship(User, foreign_keys=[connected_person_id])

    comment = Column(String, nullable=False)
    type = Column(Enum(AppealHistoryTypes))

    attachments = relationship(AppealHistoryAttachment, back_populates="appeal_history")

    meta = Column(String)
    is_private = Column(Boolean, default=False)


class AppealChat(TimeStampedModel):
    __tablename__ = 'appeal_chats'

    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    user = relationship(User, foreign_keys=[user_id])

    creator_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    creator = relationship(User, foreign_keys=[creator_id])

    appeal_id = Column(Integer, ForeignKey(UserAppeal.id, ondelete="CASCADE"), nullable=False)
    appeal = relationship(UserAppeal)

    message = Column(String(700), nullable=False)
    is_public = Column(Boolean, default=False)

    parent = Column(Integer)
    is_hidden = Column(Boolean, default=False)
