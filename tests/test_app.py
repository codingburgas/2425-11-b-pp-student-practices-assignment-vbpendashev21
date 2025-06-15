import pytest
from app import create_app, db
from app.models import User
from flask import url_for

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Avoid IntegrityError if rerun
            if not User.query.filter_by(username='testuser').first():
                user = User(username='testuser', email='test@example.com')
                user.set_password('password123')
                db.session.add(user)
                db.session.commit()
        yield client


def test_login_success(client):
    res = client.post('/login', data=dict(
        username='testuser',
        password='password123'
    ), follow_redirects=True)

    content = res.data.decode("utf-8")
    assert 'Logout' in content or 'Изход' in content


def test_login_fail(client):
    res = client.post('/login', data=dict(
        username='testuser',
        password='wrongpass'
    ), follow_redirects=True)

    content = res.data.decode("utf-8")
    assert 'Invalid' in content or 'Невалидно' in content


def test_prediction_page_requires_login(client):
    res = client.get('/', follow_redirects=True)
    content = res.data.decode("utf-8")
    assert 'Login' in content or 'Вход' in content


def test_predict_outfit_success(client):
    # Log in first
    client.post('/login', data=dict(
        username='testuser',
        password='password123'
    ), follow_redirects=True)

    # Submit prediction form
    res = client.post('/predict_outfit', data=dict(
        temperature=20.0,
        condition='sunny',
        description='Лек вятър',
        ai_mode='simple'
    ), follow_redirects=True)

    content = res.data.decode("utf-8")
    assert 'Резултат' in content or 'Result' in content
    assert '👕' in content or 'T-Shirt' in content or 'тениска' in content


def test_submit_feedback(client):
    # Login
    client.post('/login', data=dict(
        username='testuser',
        password='password123'
    ), follow_redirects=True)

    # Manually insert a prediction for this user
    from app.models import Prediction
    prediction = Prediction(
        user_id=1,
        temperature=22,
        condition='sunny',
        predicted_outfit='T-shirt and jeans',
        confidence=0.95
    )
    with client.application.app_context():
        db.session.add(prediction)
        db.session.commit()
        prediction_id = prediction.id

    # Submit feedback for that prediction
    res = client.post('/submit_feedback', data=dict(
        prediction_id=prediction_id,
        rating=4,
        comment="Useful"
    ), follow_redirects=True)

    content = res.data.decode("utf-8")
    assert "Благодарим" in content or "Thanks" in content


def test_admin_can_delete_user(client):
    from app.models import User

    with client.application.app_context():
        # Add an admin user
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()

        # Add a normal user to delete
        user = User(username='victim', email='victim@example.com')
        user.set_password('1234')
        db.session.add(user)
        db.session.commit()
        victim_id = user.id

    # Login as admin
    client.post('/login', data=dict(
        username='admin',
        password='adminpass'
    ), follow_redirects=True)

    # Delete the user
    res = client.post(f'/admin/delete_user/{victim_id}', follow_redirects=True)

    content = res.data.decode("utf-8")
    assert 'изтрит' in content or 'deleted' in content

    # Confirm user is gone
    with client.application.app_context():
        victim = User.query.get(victim_id)
        assert victim is None
