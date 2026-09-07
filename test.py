import pytest

import models

pytestmark = pytest.mark.anyio


async def test_get_sorted_recipes(client, test_db):

    async with test_db() as session:
        recipe1 = models.Recipe(
            dish_name="Eggs",
            views=10,
            cook_time=30,
            ingredients="...",
            description=".....",
        )
        recipe2 = models.Recipe(
            dish_name="Soup",
            views=50,
            cook_time=60,
            ingredients="...",
            description=".....",
        )
        recipe3 = models.Recipe(
            dish_name="Pie",
            views=10,
            cook_time=5,
            ingredients="...",
            description=".....",
        )

        session.add_all([recipe1, recipe2, recipe3])
        await session.commit()

    response = await client.get("/recipes/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    assert data[0]["dish_name"] == "Soup"

    # Вторым должна быть Яичница (10 просмотров, но готовится всего 5 минут)
    assert data[1]["dish_name"] == "Pie"

    # Третьей должна быть Пицца (10 просмотров, но готовится 30 минут)
    assert data[2]["dish_name"] == "Eggs"


async def test_get_recipe_by_id(client, test_db):
    async with test_db() as session:
        recipe1 = models.Recipe(
            dish_name="Eggs", cook_time=5, ingredients="...", description="....."
        )
        session.add(recipe1)
        await session.commit()
        await session.refresh(recipe1)
        recipe_id = recipe1.id

    response = await client.get(f"/recipes/{recipe_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["dish_name"] == "Eggs"


async def test_post_recipe(client, test_db):
    valid_recipe_data = {
        "dish_name": "Omelette",
        "cook_time": 10,
        "ingredients": "Eggs, milk, butter, salt",
        "description": "Beat eggs with milk, pour into a pan with butter and fry.",
    }
    response = await client.post(f"/recipes/", json=valid_recipe_data)

    assert response.status_code == 200

    data = response.json()
    assert data["dish_name"] == valid_recipe_data["dish_name"]
    assert data["cook_time"] == valid_recipe_data["cook_time"]
    assert data["id"] is not None

    async with test_db() as session:
        from sqlalchemy.future import select

        res = await session.execute(
            select(models.Recipe).where(models.Recipe.id == data["id"])
        )
        db_recipe = res.scalars().one_or_none()

        assert db_recipe is not None
        assert db_recipe.dish_name == "Omelette"
        assert db_recipe.views == 0
