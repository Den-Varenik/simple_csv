from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.config.database import get_db, create_or_update, get_or_create
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

    # print(set_categories)
    # print(database_categories)
    # print(new_categories)

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

        # print(set_emails)
        # print(database_emails)
        # print(new_emails)



    # user_objects = []
    #
    # category_names = []
    # category_users = []
    # for row in data:
    #     category_name = row.pop('category').lower().capitalize()
    #
    #     row['birthDate'] = datetime.strptime(row['birthDate'], '%Y-%m-%d').date()
    #     user = User(**row)
    #     user_objects.append(user)
    #
        # try:
        #     index = category_names.index('category_name')
        # except ValueError:
        #     category_names.append(category_name)
        #     users = [user]
        #     category_users.append(users)
        #     continue
        #
        # users = category_users[index]
        # users.append(user)

    # db.bulk_save_objects(user_objects)
    # db.bulk_save_objects(category_objects)

    # db.commit()

    # for user in iter(user_objects):
    # db.refresh(user_objects)

    # result = db.query(Category.name).filter(Category.name.in_(category_names)).all()
    # flat_result = [item for sublist in result for item in sublist]
    # print(flat_result)
    # print(category_names)

    # for num, name in enumerate(category_names):
    #     category, created = create_or_update(db, Category, name=name)
        # user.categories.append(category_objects[num])

    # db.bulk_save_objects(user_objects)
    # db.commit()

    return {"message": "File uploaded successfully"}


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
    )

    # Apply filters
    if category_id is not None:
        query = query.filter(Category.id == category_id)
    if gender:
        query = query.filter(User.gender == gender)
    if dob:
        query = query.filter(User.birthDate == dob)
    if age is not None:
        birth_date = date.today() - timedelta(days=age * 365)
        query = query.filter(User.birthDate >= birth_date)
    if age_range:
        age_range_start, age_range_end = map(int, age_range.split("-"))
        birth_date_start = date.today() - timedelta(days=age_range_end * 365)
        birth_date_end = date.today() - timedelta(days=age_range_start * 365 + 1)
        query = query.filter(User.birthDate >= birth_date_start)
        query = query.filter(User.birthDate <= birth_date_end)

    # Calculate total number of users and pages
    total_users = query.count()
    total_pages = (total_users - 1) // page_size + 1

    # Apply pagination
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
