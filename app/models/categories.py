from sqlalchemy import Column, Integer, String
from app.config.database import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f'Category {self.name.capitalize()}'
