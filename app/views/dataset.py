from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.categories import Category
from app.models.users import User

router = APIRouter(
    prefix="",
    tags=["dataset"],
)


def parse_csv_data(data):
    rows = data.strip().split('\n')
    header = rows[0].strip().split(',')
    data = []
    for row in rows[1:]:
        values = row.strip().split(',')
        data.append(dict(zip(header, values)))
    return data


@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    try:
        content = await file.read()
        data = parse_csv_data(content.decode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error parsing CSV data.")

    required_fields = ['category', 'firstname', 'lastname', 'email', 'gender', 'birthDate']
    if not all(field in data[0] for field in required_fields):
        raise HTTPException(status_code=400, detail="Invalid column headers in CSV data.")

    for row in data:
        user = User(
            firstname=row['firstname'],
            lastname=row['lastname'],
            email=row['email'],
            gender=row['gender'],
            birthDate=datetime.strptime(row['birthDate'], '%Y-%m-%d').date()
        )
        db.add(user)
        db.flush()  # flush the session to get the user ID
        categories = [c.strip() for c in row['category'].split(',')]
        for cat_name in categories:
            category = db.query(Category).filter_by(name=cat_name).first()
            if not category:
                category = Category(name=cat_name)
                db.add(category)
            category.users.append(user)
    db.commit()
    return {"message": "File uploaded successfully"}
