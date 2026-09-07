from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class Recipe(Base):
    __tablename__ = 'recipe'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dish_name: Mapped[str]
    cook_time: Mapped[int]
    ingredients: Mapped[str]
    description: Mapped[str]

    views: Mapped[int] = mapped_column(default=0, nullable=False)