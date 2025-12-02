"""Unit tests for the microblog application."""

import pytest
from datetime import datetime
from microblog import create_app, db
from microblog.models import User, Post


@pytest.fixture
def app():
    """Create test application."""
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create test user."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", password="testpass123")
        db.session.add(user)
        db.session.commit()
        # Refresh to get the ID
        db.session.refresh(user)
        return user


@pytest.fixture
def test_post(app, test_user):
    """Create test post."""
    with app.app_context():
        # Ensure we have a fresh user instance
        user = User.query.get(test_user.id)
        post = Post(
            title="Test Post",
            content="This is a test post content.",
            user_id=user.id
        )
        db.session.add(post)
        db.session.commit()
        # Refresh to get the ID
        db.session.refresh(post)
        return post


class TestUserModel:
    """Test User model functionality."""

    def test_create_user(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(username="newuser", email="new@example.com", password="password123")
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == "newuser"
            assert user.email == "new@example.com"
            assert user.password_hash is not None
            assert user.created_at is not None

    def test_password_hashing(self, app):
        """Test password hashing and checking."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password="testpass")

            assert user.password_hash is not None
            assert user.password_hash != "testpass"
            assert user.check_password("testpass") is True
            assert user.check_password("wrongpass") is False

    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com", password="testpass")
            assert repr(user) == "<User testuser>"


class TestPostModel:
    """Test Post model functionality."""

    def test_create_post(self, app, test_user):
        """Test post creation."""
        with app.app_context():
            # Get fresh user instance
            user = User.query.get(test_user.id)
            post = Post(
                title="Test Title",
                content="Test content here.",
                user_id=user.id
            )
            db.session.add(post)
            db.session.commit()

            assert post.id is not None
            assert post.title == "Test Title"
            assert post.content == "Test content here."
            assert post.user_id == user.id
            assert post.created_at is not None
            assert post.updated_at is not None

    def test_post_author_relationship(self, app, test_user, test_post):
        """Test post-author relationship."""
        with app.app_context():
            # Get fresh instances from the database
            user = User.query.get(test_user.id)
            post = Post.query.get(test_post.id)
            assert post.author == user
            assert post in user.posts

    def test_post_repr(self, app, test_user):
        """Test post string representation."""
        with app.app_context():
            # Get fresh user instance
            user = User.query.get(test_user.id)
            post = Post(
                title="Test Title",
                content="Test content.",
                user_id=user.id
            )
            assert repr(post) == "<Post Test Title>"


class TestRoutes:
    """Test application routes."""

    def test_index_page(self, client):
        """Test index page loads."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Welcome to Microblog" in response.data

    def test_register_page(self, client):
        """Test registration page loads."""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Register" in response.data

    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_create_post_requires_login(self, client):
        """Test create post requires authentication."""
        response = client.get("/create")
        assert response.status_code == 302  # Redirect to login

    def test_logout_requires_login(self, client):
        """Test logout requires authentication."""
        response = client.get("/auth/logout")
        assert response.status_code == 302  # Redirect to login

    def test_register_user(self, client, app):
        """Test user registration."""
        response = client.post("/auth/register", data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "password2": "password123",
            "bio": "Test bio"
        })

        assert response.status_code == 302  # Redirect after successful registration

        with app.app_context():
            user = User.query.filter_by(username="newuser").first()
            assert user is not None
            assert user.email == "new@example.com"
            assert user.bio == "Test bio"

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username fails."""
        with client.application.app_context():
            username = test_user.username
        response = client.post("/auth/register", data={
            "username": username,  # Already exists
            "email": "different@example.com",
            "password": "password123",
            "password2": "password123"
        })

        assert response.status_code == 200  # Stay on registration page
        assert b"Username already exists" in response.data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        with client.application.app_context():
            email = test_user.email
        response = client.post("/auth/register", data={
            "username": "differentuser",
            "email": email,  # Already exists
            "password": "password123",
            "password2": "password123"
        })

        assert response.status_code == 200  # Stay on registration page
        assert b"Email already registered" in response.data

    def test_login_user(self, client, test_user):
        """Test user login."""
        with client.application.app_context():
            username = test_user.username
        response = client.post("/auth/login", data={
            "username": username,
            "password": "testpass123"
        })

        assert response.status_code == 302  # Redirect after successful login
        assert response.headers["Location"].endswith("/")

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        with client.application.app_context():
            username = test_user.username
        response = client.post("/auth/login", data={
            "username": username,
            "password": "wrongpassword"
        })

        assert response.status_code == 200  # Stay on login page
        assert b"Invalid username or password" in response.data

    def test_login_with_safe_next_redirect(self, client, test_user):
        """Login should follow safe next redirects."""
        with client.application.app_context():
            username = test_user.username
        response = client.post("/auth/login?next=/create", data={
            "username": username,
            "password": "testpass123"
        })

        assert response.status_code == 302
        assert response.headers["Location"].endswith("/create")

    def test_login_with_unsafe_next_redirect(self, client, test_user):
        """Login should ignore external next redirects."""
        with client.application.app_context():
            username = test_user.username
        response = client.post("/auth/login?next=http://evil.com/phish", data={
            "username": username,
            "password": "testpass123"
        })

        assert response.status_code == 302
        assert response.headers["Location"].endswith("/")

    def test_create_post_authenticated(self, client, app, test_user):
        """Test creating post when authenticated."""
        with app.app_context():
            username = test_user.username
            user_id = test_user.id

        # Login first
        client.post("/auth/login", data={
            "username": username,
            "password": "testpass123"
        })

        # Create post
        response = client.post("/create", data={
            "title": "New Test Post",
            "content": "This is new test content."
        })

        assert response.status_code == 302  # Redirect after successful creation

        with app.app_context():
            post = Post.query.filter_by(title="New Test Post").first()
            assert post is not None
            assert post.content == "This is new test content."
            assert post.user_id == user_id

    def test_view_post(self, client, test_post):
        """Test viewing a single post."""
        response = client.get(f"/post/{test_post.id}")
        assert response.status_code == 200
        assert b"Test Post" in response.data
        assert b"This is a test post content." in response.data

    def test_view_nonexistent_post(self, client):
        """Test viewing non-existent post returns 404."""
        response = client.get("/post/999")
        assert response.status_code == 404

    def test_profile_page(self, client, test_user):
        """Test user profile page."""
        with client.application.app_context():
            username = test_user.username
            email = test_user.email
        response = client.get(f"/profile/{username}")
        assert response.status_code == 200
        assert username.encode() in response.data
        assert email.encode() in response.data

    def test_profile_nonexistent_user(self, client):
        """Test profile page for non-existent user returns 404."""
        response = client.get("/profile/nonexistentuser")
        assert response.status_code == 404


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_post_title(self, client, app, test_user):
        """Test creating post with empty title fails."""
        # Login first
        client.post("/auth/login", data={
            "username": "testuser",
            "password": "testpass123"
        })

        response = client.post("/create", data={
            "title": "",  # Empty title
            "content": "Some content"
        })

        assert response.status_code == 200  # Stay on form page
        assert b"This field is required" in response.data

    def test_empty_post_content(self, client, app, test_user):
        """Test creating post with empty content fails."""
        # Login first
        client.post("/auth/login", data={
            "username": "testuser",
            "password": "testpass123"
        })

        response = client.post("/create", data={
            "title": "Some title",
            "content": ""  # Empty content
        })

        assert response.status_code == 200  # Stay on form page
        assert b"This field is required" in response.data

    def test_short_password(self, client):
        """Test registration with short password fails."""
        response = client.post("/auth/register", data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "123",  # Too short
            "password2": "123"
        })

        assert response.status_code == 200  # Stay on registration page
        assert b"Field must be at least 6 characters long" in response.data

    def test_password_mismatch(self, client):
        """Test registration with password mismatch fails."""
        response = client.post("/auth/register", data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "password2": "different123"
        })

        assert response.status_code == 200  # Stay on registration page
        assert b"Field must be equal to password" in response.data

    def test_invalid_email(self, client):
        """Test registration with invalid email fails."""
        response = client.post("/auth/register", data={
            "username": "newuser",
            "email": "invalid-email",  # Invalid format
            "password": "password123",
            "password2": "password123"
        })

        assert response.status_code == 200  # Stay on registration page
        assert b"Invalid email address" in response.data


class TestDatabaseOperations:
    """Test database operations and constraints."""

    def test_user_unique_username(self, app, test_user):
        """Test username uniqueness constraint."""
        with app.app_context():
            duplicate_user = User(username="testuser", email="different@example.com", password="pass")
            db.session.add(duplicate_user)

            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()

    def test_user_unique_email(self, app, test_user):
        """Test email uniqueness constraint."""
        with app.app_context():
            duplicate_user = User(username="different", email="test@example.com", password="pass")
            db.session.add(duplicate_user)

            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()

    def test_post_foreign_key_constraint(self, app):
        """Test post foreign key constraint (SQLite doesn't enforce by default)."""
        with app.app_context():
            # Note: SQLite doesn't enforce foreign key constraints by default
            # This test verifies the relationship is properly set up
            user = User(username="testuser", email="test@example.com", password="testpass")
            db.session.add(user)
            db.session.commit()

            post = Post(title="Test", content="Test", user_id=user.id)
            db.session.add(post)
            db.session.commit()

            # Verify the relationship works
            assert post.author == user
            assert post in user.posts


if __name__ == "__main__":
    pytest.main([__file__])
