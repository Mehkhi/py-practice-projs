"""WTForms forms for the microblog application."""

import re
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from microblog.models import User


_EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


class SimpleEmail:
    """Lightweight email validator that avoids external dependencies."""

    def __init__(self, message: str | None = None):
        self.message = message or "Invalid email address."

    def __call__(self, form, field):
        data = (field.data or "").strip()
        if not data or not _EMAIL_REGEX.match(data):
            raise ValidationError(self.message)


class LoginForm(FlaskForm):
    """Form for user login."""

    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """Form for user registration."""

    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), SimpleEmail(), Length(max=120)]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)]
    )
    password2 = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo("password")]
    )
    bio = TextAreaField(
        "Bio (optional)",
        validators=[Length(max=500)]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        """Validate that username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already exists. Please choose a different one.")

    def validate_email(self, email):
        """Validate that email is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already registered. Please use a different one.")


class PostForm(FlaskForm):
    """Form for creating and editing posts."""

    title = StringField(
        "Title",
        validators=[DataRequired(), Length(min=1, max=200)]
    )
    content = TextAreaField(
        "Content",
        validators=[DataRequired(), Length(min=1, max=5000)]
    )
    submit = SubmitField("Post")
