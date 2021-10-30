from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, SmallInteger
from sqlalchemy.orm import relationship

from grazhdane.models import TimeStampedModel
from users.models import User, SocialGroup


class Poll(TimeStampedModel):
    __tablename__ = "polls"

    title = Column(String, nullable=False)
    description = Column(String(700), nullable=False)
    creator_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    creator = relationship(User)
    legally_significant = Column(Boolean, default=False)
    closed_at = Column(DateTime)
    news_notify = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)


class PollGroup(TimeStampedModel):
    __tablename__ = "poll_groups"

    poll_id = Column(Integer, ForeignKey(Poll.id, ondelete="CASCADE"), nullable=False)
    poll = relationship(Poll)
    group_id = Column(Integer, ForeignKey(SocialGroup.id, ondelete="CASCADE"), nullable=False)
    group = relationship(SocialGroup)


class PollQuiz(TimeStampedModel):
    __tablename__ = "poll_quizzes"

    poll_id = Column(Integer, ForeignKey(Poll.id, ondelete="CASCADE"), nullable=False)
    poll = relationship(Poll)
    text = Column(String(700), nullable=False)
    parent_id = Column(Integer)
    quiz_type = Column(String, nullable=False)


class PollAnswer(TimeStampedModel):
    __tablename__ = "poll_answers"

    question_id = Column(Integer, ForeignKey(PollQuiz.id, ondelete="CASCADE"), nullable=False)
    question = relationship(PollQuiz)
    answer_id = Column(Integer, ForeignKey(PollQuiz.id, ondelete="CASCADE"), nullable=False)
    answer = relationship(PollQuiz)
    vote = Column(SmallInteger)
    creator_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    creator = relationship(User)