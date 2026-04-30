"""
Heroes Router — Full CRUD for heroes.

GET    /heroes          → list all heroes (with pagination)
POST   /heroes          → create a new hero
GET    /heroes/{id}     → get one hero
PATCH  /heroes/{id}     → partial update
DELETE /heroes/{id}     → delete a hero
"""

from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, SessionDep
from app.models.hero import Hero
from app.schemas.hero import HeroCreate, HeroOut, HeroUpdate
from sqlmodel import select

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.get("", response_model=list[HeroOut])
def list_heroes(session: SessionDep, skip: int = 0, limit: int = 20):
    """List heroes with pagination."""
    heroes = session.exec(select(Hero).offset(skip).limit(limit)).all()
    return heroes


@router.post("", response_model=HeroOut, status_code=status.HTTP_201_CREATED)
def create_hero(data: HeroCreate, session: SessionDep, user: CurrentUser):
    """Create a new hero. Requires authentication."""
    hero = Hero(**data.model_dump())
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.get("/{hero_id}", response_model=HeroOut)
def get_hero(hero_id: int, session: SessionDep):
    """Get a single hero by ID."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hero not found")
    return hero


@router.patch("/{hero_id}", response_model=HeroOut)
def update_hero(
    hero_id: int,
    patch: HeroUpdate,
    session: SessionDep,
    user: CurrentUser,
):
    """
    Partial update: only provided fields are changed.
    Requires authentication.
    """
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hero not found")
    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(hero, field, value)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(hero_id: int, session: SessionDep, user: CurrentUser):
    """Delete a hero. Requires authentication."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hero not found")
    session.delete(hero)
    session.commit()
