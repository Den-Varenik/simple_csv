from app.models.users import User, user_category
from app.models.categories import Category


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

    categories = db.query(Category).all()
    assert len(categories) == 2
    assert categories[0].name == 'toys'
    assert categories[1].name == 'electronics'

    user_categories = db.query(user_category).all()
    assert len(user_categories) == 2
    assert user_categories[0].user_id == users[0].id
    assert user_categories[0].category_id == categories[0].id
    assert user_categories[1].user_id == users[1].id
    assert user_categories[1].category_id == categories[1].id
