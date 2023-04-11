from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.config.database import Base
from app.models.users import user_category


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    users = relationship("User", secondary=user_category, back_populates="categories")

    def __repr__(self):
        return f'Category {self.name.capitalize()}'
