from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends

from app.config.database import get_db
from app.models.categories import Category
from app.models.users import User
from app.schemas.users import UserSchema, UserCreate, UserUpdate, UserPatch

router = APIRouter(
    prefix="/users",
    tags=["user"],
)


@router.get("/", response_model=List[UserSchema])
def get_all_users(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/", status_code=201)
def create_user(user: UserCreate, category_id: Optional[int] = None, db=Depends(get_db)):
    db_user = User(**user.dict())

    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_user.categories.append(category)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{user_id}/", response_model=UserSchema)
def get_user(user_id: int, db=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}/", response_model=UserSchema)
def update_user(user_id: int, user: UserUpdate, category_id: Optional[int] = None, db=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_user.categories = [category]
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch("/{user_id}/", response_model=UserSchema)
def patch_user(user_id: int, user: UserPatch, db=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}/")
def delete_user(user_id: int, db=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
