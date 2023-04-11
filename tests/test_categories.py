from app.models.categories import Category


def test_get_all_categories(db, client):
    category = Category(name='Test Category')
    db.add(category)
    db.commit()
    response = client.get('/categories/')
    assert response.status_code == 200
    assert response.json() == [{'id': category.id, 'name': 'Test Category'}]


def test_create_category(db, client):
    category_data = {'name': 'Test Category'}
    response = client.post('/categories/', json=category_data)
    assert response.status_code == 201
    category = db.query(Category).filter_by(name='Test Category').first()
    assert category is not None
    assert category.name == 'Test Category'


def test_get_category(db, client):
    category = Category(name='Test Category')
    db.add(category)
    db.commit()
    response = client.get(f'/categories/{category.id}/')
    assert response.status_code == 200
    assert response.json() == {'id': category.id, 'name': 'Test Category'}


def test_update_category(db, client):
    category = Category(name='Test Category')
    db.add(category)
    db.commit()
    category_data = {'name': 'Updated Category'}
    response = client.put(f'/categories/{category.id}/', json=category_data)
    assert response.status_code == 200
    updated_category = db.query(Category).filter_by(id=category.id).first()
    assert updated_category.name == 'Updated Category'


def test_delete_category(db, client):
    category = Category(name='Test Category')
    db.add(category)
    db.commit()
    response = client.delete(f'/categories/{category.id}/')
    assert response.status_code == 204
    deleted_category = db.query(Category).filter_by(id=category.id).first()
    assert deleted_category is None
