from sqlalchemy import Column, Integer, String, Date, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.config.database import Base

user_category = Table(
    'user_category',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    gender = Column(Enum('male', 'female', 'other', name='gender_types'), nullable=False)
    birthDate = Column(Date, nullable=False)
    categories = relationship("Category", secondary=user_category, back_populates="users")
