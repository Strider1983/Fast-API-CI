from pydantic import BaseModel, Field


class NotFoundResponse(BaseModel):
    detail: str


class BaseRecipe(BaseModel):
    dish_name: str = Field(
        ..., description="Dish full name", min_length=2, max_length=100
    )
    cook_time: int = Field(..., description="Cooking time in minutes", ge=1, le=480)
    ingredients: str = Field(
        ..., description="Full list of ingredients", min_length=2, max_length=200
    )
    description: str = Field(
        ..., description="Description of cooking process", min_length=5, max_length=400
    )


class RecipeIn(BaseRecipe): ...


class RecipeOut(BaseRecipe):
    id: int = Field(..., description="Unique id in database")

    class Config:
        from_attributes = True


class RecipeListOut(BaseModel):
    dish_name: str
    views: int
    cook_time: int

    class Config:
        from_attributes = True
