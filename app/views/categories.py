from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.categories import Category
from app.schemas.categories import CategoryUpdate, CategorySchema, CategoryCreate
from app.config.database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/categories",
    tags=["category"],
)


@router.get("/", response_model=List[CategorySchema])
def get_all_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    print('From view', categories)
    print(db)
    return categories


@router.post('/', status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get('/{category_id}/', response_model=CategorySchema)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')
    return category


@router.put('/{category_id}/', response_model=CategorySchema)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail='Category not found')
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category


@router.patch('/{category_id}/', response_model=CategorySchema)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail='Category not found')
    if category.name:
        db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete('/{category_id}/', status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail='Category not found')
    db.delete(db_category)
    db.commit()
