from datetime import date, timedelta
from typing import List

from app.models.categories import Category
from app.models.users import User, user_category


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

    user_categories = db.query(user_category).all()
    categories = db.query(Category).all()
    assert len(user_categories) == 2
    assert user_categories[0].user_id == users[0].id
    assert user_categories[0].category_id == categories[0].id
    assert user_categories[1].user_id == users[1].id
    assert user_categories[1].category_id == categories[1].id


# def test_dataset_filter_category(db, client, users: List[User]):
#     response = client.get("/dataset/?category=1")
#     assert response.status_code == 200
#     assert len(response.json()) == 2
#     assert all(user_dict["categories"][0]["name"] == "toys" for user_dict in response.json())
#
#
# def test_dataset_filter_gender(db, client, users: List[User]):
#     response = client.get("/dataset/?gender=male")
#     assert response.status_code == 200
#     assert len(response.json()) == 2
#     assert all(user_dict["gender"] == "male" for user_dict in response.json())
#
#
# def test_dataset_filter_birth(db, client, users: List[User]):
#     response = client.get("/dataset/?birth_date=1990-01-01")
#     assert response.status_code == 200
#     assert len(response.json()) == 1
#     assert response.json()[0]["firstname"] == "Alice"
#
#
# def test_dataset_filter_age(db, client, users: List[User]):
#     response = client.get("/dataset/?age=35")
#     assert response.status_code == 200
#     assert len(response.json()) == 2
#     assert all(user_dict["birthDate"] <= date.today() - timedelta(days=35 * 365) for user_dict in response.json())
#
#
# def test_dataset_filter_range(db, client, users: List[User]):
#     response = client.get("/dataset/?age_range=18-30")
#     assert response.status_code == 200
#     assert len(response.json()) == 1
#     assert response.json()[0]["firstname"] == "Charlie"
