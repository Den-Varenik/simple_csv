from datetime import datetime

from app.models.categories import Category
from app.models.users import User


def test_read_users(db, client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user(db, client):
    category = Category(name="Test Category")
    db.add(category)
    db.commit()
    db.refresh(category)

    user_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "gender": "male",
        "birthDate": "1990-01-01",
    }
    response = client.post("/users/", json=user_data, params={"category_id": category.id})
    assert response.status_code == 201
    assert response.json()["firstname"] == user_data["firstname"]
    assert response.json()["lastname"] == user_data["lastname"]
    assert response.json()["email"] == user_data["email"]
    assert response.json()["gender"] == user_data["gender"]
    assert response.json()["birthDate"] == user_data["birthDate"]

    db_user = db.query(User).filter(User.email == user_data["email"]).first()
    assert db_user is not None
    assert db_user.firstname == user_data["firstname"]
    assert db_user.lastname == user_data["lastname"]
    assert db_user.email == user_data["email"]
    assert db_user.gender == user_data["gender"]
    assert str(db_user.birthDate) == user_data["birthDate"]
    assert len(db_user.categories) == 1

    db.delete(db_user)
    db.delete(category)
    db.commit()


def test_read_user(db, client):
    birth_date = datetime.strptime("1990-01-01", "%Y-%m-%d").date()
    user = User(firstname="Test", lastname="User", email="testuser@example.com",
                gender="male", birthDate=birth_date)
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.get(f"/users/{user.id}/")
    assert response.status_code == 200
    assert response.json()["id"] == user.id
    assert response.json()["firstname"] == user.firstname
    assert response.json()["lastname"] == user.lastname
    assert response.json()["email"] == user.email
    assert response.json()["gender"] == user.gender
    assert response.json()["birthDate"] == str(user.birthDate)

    db.delete(user)
    db.commit()


def test_update_user(db, client):
    user_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "gender": "male",
        "birthDate": "1990-01-01",
    }

    response = client.post("/users/", json=user_data)
    user_id = response.json()["id"]

    updated_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": "newemail@example.com",
        "gender": "male",
        "birthDate": "1990-01-01",
    }
    response = client.put(f"/users/{user_id}/", json=updated_data)
    assert response.status_code == 200
    assert response.json()["email"] == updated_data["email"]

    response = client.delete(f"/users/{user_id}/")
    assert response.status_code == 200


def test_patch_user(db, client):
    user_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "gender": "male",
        "birthDate": "1990-01-01",
    }

    response = client.post("/users/", json=user_data)
    user_id = response.json()["id"]

    patch_data = {"email": "newemail@example.com"}
    response = client.patch(f"/users/{user_id}/", json=patch_data)
    assert response.status_code == 200
    assert response.json()["email"] == patch_data["email"]

    response = client.delete(f"/users/{user_id}/")
    assert response.status_code == 200


def test_delete_user(db, client):
    user_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "gender": "male",
        "birthDate": "1990-01-01",
    }

    response = client.post("/users/", json=user_data)
    user_id = response.json()["id"]

    response = client.delete(f"/users/{user_id}/")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    response = client.get(f"/users/{user_id}/")
    assert response.status_code == 404
