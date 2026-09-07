from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import async_session, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    yield


app = FastAPI(lifespan=lifespan)


async def get_db():
    async with async_session() as session:
        yield session


@app.post(
    "/recipes/",
    response_model=schemas.RecipeOut,
    description="Add new recipe to database",
)
async def recipes(
    book: schemas.RecipeIn, db: AsyncSession = Depends(get_db)
) -> models.Recipe:
    new_recipe = models.Recipe(**book.model_dump())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)

    return new_recipe


@app.get(
    "/recipes/",
    response_model=List[schemas.RecipeListOut],
    description="Get all recipes from database "
    "sorted first by views, than by cooking time",
)
async def recipes_sorted(db: AsyncSession = Depends(get_db)) -> List[models.Recipe]:
    query = select(
        models.Recipe.dish_name, models.Recipe.views, models.Recipe.cook_time
    ).order_by(desc(models.Recipe.views), models.Recipe.cook_time)
    res = await db.execute(query)
    return res.mappings().all()


@app.get(
    "/recipes/{recipe_id}",
    response_model=schemas.RecipeOut,
    description="Get recipe by id",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.NotFoundResponse,
            "description": "Recipe with specified id is missing in database",
        }
    },
)
async def recipes_sorted(
    recipe_id: int, db: AsyncSession = Depends(get_db)
) -> models.Recipe:
    res = await db.execute(select(models.Recipe).where(recipe_id == models.Recipe.id))
    target_recipe = res.scalars().one_or_none()
    if target_recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )
    target_recipe.views += 1
    await db.commit()
    await db.refresh(target_recipe)

    return target_recipe
