from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import extract

from app.config.database import get_db
from app.models.categories import Category
from app.models.users import User
from app.schemas.users import UserWithCategories

router = APIRouter(
    prefix="",
    tags=["dataset"],
)


def parse_csv_data(data):
    rows = data.strip().split('\n')
    header = rows[0].strip().split(',')
    for row in iter(rows[1:]):
        values = row.strip().split(',')
        yield dict(zip(header, values))


@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    content = await file.read()

    unique_categories = []
    category_users_emails = []
    users_additional_info = []
    for row in parse_csv_data(content.decode('utf-8')):
        category_name = row.pop('category').lower().capitalize()
        row['birthDate'] = datetime.strptime(row['birthDate'], '%Y-%m-%d').date()

        try:
            index = unique_categories.index(category_name)
        except ValueError:
            unique_categories.append(category_name)
            category_users_emails.append([row.pop('email').lower()])
            users_additional_info.append([row])
            continue

        users_emails = category_users_emails[index]
        users_emails.append(row.pop('email').lower())

        users_info = users_additional_info[index]
        users_info.append(row)

    set_categories = set(unique_categories)
    result = db.query(Category.name).filter(Category.name.in_(set_categories)).all()
    database_categories = {item for sublist in result for item in sublist}
    new_categories = set_categories - database_categories

    if new_categories:
        db.bulk_save_objects([Category(name=name) for name in new_categories])
        db.commit()

    for num, category_name in enumerate(unique_categories):
        category = db.query(Category).filter_by(name=category_name).first()

        emails = category_users_emails[num]
        info = users_additional_info[num]

        set_emails = set(emails)
        result = db.query(User.email).filter(User.email.in_(set_emails)).all()
        database_emails = {item for sublist in result for item in sublist}
        new_emails = set_emails - database_emails

        if new_emails:
            users = list()
            for email in new_emails:
                index = emails.index(email)
                user_data = info[index]
                users.append(User(email=email, **user_data))

            if users:
                db.bulk_save_objects(users)
                db.commit()

        users = db.query(User).filter(User.email.in_(set_emails)).all()
        for user in users:
            user.categories.append(category)
        db.add_all(users)
        db.commit()
    return {"message": "File uploaded successfully"}


def query_filter(
        query,
        category_id: int = None,
        gender: str = None,
        dob: date = None,
        age: int = None,
        age_range: str = None
):
    if category_id is not None:
        query = query.join(User.categories).filter(Category.id == category_id)
    if gender:
        query = query.filter(User.gender == gender)
    if dob:
        query = query.filter(User.birthDate == dob)
    if age is not None:
        year = datetime.now().year - age
        query = query.filter(extract('year', User.birthDate) == year)
    if age_range:
        age_range_start, age_range_end = map(int, age_range.split("-"))
        birth_date_start = date.today() - timedelta(days=age_range_end * 365)
        birth_date_end = date.today() - timedelta(days=age_range_start * 365 + 1)
        query = query.filter(User.birthDate >= birth_date_start)
        query = query.filter(User.birthDate <= birth_date_end)
    return query


@router.get("/dataset/", status_code=200)
def get_dataset(
        db: Session = Depends(get_db),
        page: int = Query(1, gt=0),
        page_size: int = Query(10, ge=1, le=20),
        category_id: int = Query(None),
        gender: str = Query(None, max_length=6),
        dob: date = Query(None),
        age: int = Query(None, ge=0),
        age_range: str = Query(None, max_length=7),
):
    query = db.query(User).options(
        joinedload(User.categories)
    ).join(User.categories)
    query = query_filter(query, category_id, gender, dob, age, age_range)

    # Calculate total number of users and pages
    total_users = query.count()

    # Apply pagination
    total_pages = (total_users - 1) // page_size + 1
    query = query.limit(page_size).offset((page - 1) * page_size)

    # Retrieve the filtered and paginated users
    users = query.all()

    response = {
        "users": [UserWithCategories.from_orm(user).dict() for user in users],
        "page": page,
        "page_size": page_size,
        "total_users": total_users,
        "total_pages": total_pages,
    }
    return response


@router.get("/dataset-csv/", status_code=200, name="Get Dataset CSV")
def get_dataset_file(
        db: Session = Depends(get_db),
        category_id: int = Query(None),
        gender: str = Query(None, max_length=6),
        dob: date = Query(None),
        age: int = Query(None, ge=0),
        age_range: str = Query(None, max_length=7),
):
    query = db.query(User).options(
        joinedload(User.categories)
    ).join(User.categories)
    users = query_filter(query, category_id, gender, dob, age, age_range)

    csv_string = "category,firstname,lastname,email,gender,birthDate\n"
    for user in users:
        if category_id is not None:
            category_name = db.query(Category.name).filter(Category.id == category_id).first()[0]
            csv_string += f"{category_name},{user.firstname},{user.lastname},{user.email},{user.gender},{user.birthDate.strftime('%Y-%m-%d')}\n"
            continue

        for category in user.categories:
            csv_string += f"{category.name},{user.firstname},{user.lastname},{user.email},{user.gender},{user.birthDate.strftime('%Y-%m-%d')}\n"

    return Response(content=csv_string, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=dataset.csv"})
