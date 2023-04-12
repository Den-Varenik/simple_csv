import csv
import io
from datetime import datetime, date
from typing import List

from app.models.categories import Category
from app.models.users import User


def test_upload_csv(db, client):
    csv_data = '''category,firstname,lastname,email,gender,birthDate
                  toys,Maribel,Towne,dagmar75@gmail.com,female,1972-05-05
                  electronics,Martina,Heller,dreinger@yahoo.com,female,1990-11-27'''
    response = client.post("/upload-csv/", files={"file": ("data.csv", csv_data)})
    assert response.status_code == 200
    assert response.json() == {"message": "File uploaded successfully"}

    users = db.query(User).all()
    assert len(users) == 2
    assert users[0].firstname == 'Maribel'
    assert users[1].lastname == 'Heller'

    categories = db.query(Category.name).all()
    categories_flat = [item for sublist in categories for item in sublist]
    assert len(categories) == 2
    assert 'Toys' in categories_flat
    assert 'Electronics' in categories_flat


def test_dataset_filter_category(db, client, users: List[User]):
    response = client.get("/dataset/?category_id=1")
    users = response.json()['users']
    assert response.status_code == 200
    assert len(users) == 2
    assert all(user_dict["categories"][0]["name"] == "Toys" for user_dict in users)


def test_dataset_filter_gender(db, client, users: List[User]):
    response = client.get("/dataset/?gender=male")
    users = response.json()['users']
    assert response.status_code == 200
    assert len(users) == 2
    assert all(user_dict["gender"] == "male" for user_dict in users)


def test_dataset_filter_birth(db, client, users: List[User]):
    response = client.get("/dataset/?dob=1990-01-01")
    users = response.json()['users']
    assert response.status_code == 200
    assert len(users) == 1
    assert users[0]["firstname"] == "Alice"


def test_dataset_filter_age(db, client, users: List[User]):
    age = 38
    year = datetime.now().year - age
    response = client.get(f"/dataset/?age={age}")
    users = response.json()['users']
    assert response.status_code == 200
    assert len(users) == 1
    for user in response.json()['users']:
        assert datetime.strptime(user['birthDate'], '%Y-%m-%d').year == year


def test_dataset_filter_range(db, client, users: List[User]):
    response = client.get("/dataset/?age_range=18-30")
    users = response.json()['users']
    assert response.status_code == 200
    assert len(users) == 1
    assert users[0]["firstname"] == "Charlie"


def test_get_dataset_file(client):
    response = client.get("/dataset-csv/", params={"age": 30})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=dataset.csv" in response.headers["Content-Disposition"]

    # Read the CSV content from the response body
    csv_content = response.content.decode("utf-8")
    csv_reader = csv.reader(io.StringIO(csv_content))

    # Check the CSV headers
    headers = next(csv_reader)
    assert headers == ["category", "firstname", "lastname", "email", "gender", "birthDate"]

    # Check the CSV rows
    for row in csv_reader:
        assert len(row) == 6
        assert isinstance(row[0], str)  # category
        assert isinstance(row[1], str)  # firstname
        assert isinstance(row[2], str)  # lastname
        assert "@" in row[3]  # email
        assert isinstance(row[4], str)  # gender
        assert date.fromisoformat(row[5]) <= date.today().replace(year=date.today().year - 30)  # birthDate
