from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    ValidationError,
)

from models import BlogCategory, Subscriber, User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(
                min=3, max=80, message="Username must be between 3 and 80 characters."
            ),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email address."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, message="Password must be at least 6 characters."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords do not match."),
        ],
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already exists.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already exists.")


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(message="Username is required.")],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required.")],
    )
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class BlogPostForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Title is required."),
            Length(
                min=5, max=200, message="Title must be between 5 and 200 characters."
            ),
        ],
    )
    status = StringField(
        "Status",
        validators=[
            DataRequired(message="Status is required."),
            Length(
                min=5, max=20, message="Status must be between 5 and 200 characters."
            ),
        ],
    )
    content = TextAreaField(
        "Content",
        validators=[
            DataRequired(message="Content is required."),
            Length(min=10, message="Content must be at least 10 characters."),
        ],
    )
    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[Optional()],
    )
    published = BooleanField("Publish")
    submit = SubmitField("Save Post")

    def __init__(self, *args, **kwargs):
        super(BlogPostForm, self).__init__(*args, **kwargs)
        # Dynamically populate category choices from database
        self.category_id.choices = [(0, "-- Select a Category --")] + [
            (category.id, category.name) for category in BlogCategory.query.all()
        ]


class BlogCategoryForm(FlaskForm):
    name = StringField(
        "Category Name",
        validators=[
            DataRequired(message="Category name is required."),
            Length(
                min=2,
                max=100,
                message="Category name must be between 2 and 100 characters.",
            ),
        ],
    )
    description = TextAreaField(
        "Description",
        validators=[Optional()],
    )
    submit = SubmitField("Save Category")

    def __init__(self, category_id=None, *args, **kwargs):
        super(BlogCategoryForm, self).__init__(*args, **kwargs)
        self.category_id = category_id

    def validate_name(self, name):
        query = BlogCategory.query.filter_by(name=name.data)
        # If editing, exclude the current category from duplicate check
        if self.category_id:
            query = query.filter(BlogCategory.id != self.category_id)
        existing = query.first()
        if existing:
            raise ValidationError("Category name already exists.")


class CommentForm(FlaskForm):
    content = TextAreaField(
        "Comment",
        validators=[
            DataRequired(message="Comment cannot be empty."),
            Length(
                min=1,
                max=1000,
                message="Comment must be between 1 and 1000 characters.",
            ),
        ],
    )
    submit = SubmitField("Post Comment")


class EditCommentForm(FlaskForm):
    content = TextAreaField(
        "Comment",
        validators=[
            DataRequired(message="Comment cannot be empty."),
            Length(
                min=1,
                max=1000,
                message="Comment must be between 1 and 1000 characters.",
            ),
        ],
    )
    submit = SubmitField("Update Comment")


class SubscribeForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Subscribe")

    def validate_email(self, email):
        subscriber = Subscriber.query.filter_by(email=email.data).first()
        if subscriber:
            raise ValidationError("This email is already subscribed.")
