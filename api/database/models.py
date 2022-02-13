from sqlalchemy import Column, Integer, String, DateTime, Float, Time, ForeignKey, UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Field(Base):
    __tablename__ = 'fields'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False)
    __table_args__ = (UniqueConstraint('name', name='uix_name'),)


class FieldData(Base):
    __tablename__ = 'field_data'
    id = Column(Integer(), primary_key=True)
    start_datetime = Column(DateTime(), nullable=False)
    value = Column(Float(), nullable=False)
    duration = Column(Time(), nullable=False)
    field_id = Column(Integer(), ForeignKey('fields.id'))
    field = relationship("Field", backref="data")
    __table_args__ = (
        UniqueConstraint('start_datetime', 'field_id', name='uix_time_and_field'),
    )

    def __repr__(self):
        return str([getattr(self, c.name, None) for c in self.__table__.c])
