import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from models import BlogCategory, BlogPost, User, db

load_dotenv()
app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "your-secret-key-change-this-in-production"
)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in first."


# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create tables
with app.app_context():
    db.create_all()
    # Load default categories if there are none:
    if BlogCategory.query.count() == 0:
        default_categories = ["Personal", "Work", "Home", "Urgent"]
        for name in default_categories:
            db.session.add(BlogCategory(name=name))
        db.session.commit()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validation
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return redirect(url_for("register"))

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get("remember"))
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# ==================== Authentication ====================


@app.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    published_posts = (
        BlogPost.query.filter_by(published=True)
        .order_by(BlogPost.created_at.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("home.html", posts=published_posts)


@app.route("/dashboard")
@login_required
def dashboard():
    total_posts = BlogPost.query.filter_by(author_id=current_user.id).count()
    published_posts = BlogPost.query.filter_by(
        author_id=current_user.id, published=True
    ).count()
    categories = BlogCategory.query.all()

    return render_template(
        "dashboard.html",
        user=current_user,
        total_posts=total_posts,
        published_posts=published_posts,
        categories=categories,
    )


# ==================== Blog Category Routes ====================


@app.route("/categories")
def view_categories():
    page = request.args.get("page", 1, type=int)
    categories = BlogCategory.query.order_by(BlogCategory.created_at.desc()).paginate(
        page=page, per_page=10
    )
    return render_template("categories.html", categories=categories)


@app.route("/category/create", methods=["GET", "POST"])
@login_required
def create_category():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("Category name is required.", "danger")
            return redirect(url_for("create_category"))

        if BlogCategory.query.filter_by(name=name).first():
            flash("Category already exists.", "danger")
            return redirect(url_for("create_category"))

        category = BlogCategory(name=name, description=description)
        db.session.add(category)
        db.session.commit()

        flash("Category created successfully!", "success")
        return redirect(url_for("view_categories"))

    return render_template("create_category.html")


@app.route("/category/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    category = BlogCategory.query.get_or_404(category_id)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("Category name is required.", "danger")
            return redirect(url_for("edit_category", category_id=category_id))

        existing = BlogCategory.query.filter_by(name=name).first()
        if existing and existing.id != category_id:
            flash("Category name already exists.", "danger")
            return redirect(url_for("edit_category", category_id=category_id))

        category.name = name
        category.description = description
        db.session.commit()

        flash("Category updated successfully!", "success")
        return redirect(url_for("view_categories"))

    return render_template("edit_category.html", category=category)


@app.route("/category/<int:category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id):
    category = BlogCategory.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()

    flash("Category deleted successfully!", "success")
    return redirect(url_for("view_categories"))


# ==================== Blog Post Routes ====================


@app.route("/posts")
def view_posts():
    page = request.args.get("page", 1, type=int)
    category_id = request.args.get("category_id", type=int)

    query = BlogPost.query.filter_by(published=True)
    if category_id:
        query = query.filter_by(category_id=category_id)

    posts = query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=10)
    categories = BlogCategory.query.all()

    return render_template(
        "posts.html", posts=posts, categories=categories, selected_category=category_id
    )


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Check if post is published or if user is the author
    if not post.published:
        if not current_user.is_authenticated or current_user.id != post.author_id:
            flash("This post is not available.", "danger")
            return redirect(url_for("view_posts"))

    return render_template("post_detail.html", post=post)


@app.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    categories = BlogCategory.query.all()

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category_id = request.form.get("category_id", type=int)
        published = request.form.get("published") == "on"

        if not title or not content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("create_post"))

        post = BlogPost(
            title=title,
            content=content,
            category_id=category_id if category_id else None,
            author_id=current_user.id,
            published=published,
        )
        db.session.add(post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for("my_posts"))

    return render_template("create_post.html", categories=categories)


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Check if user is the author
    if post.author_id != current_user.id:
        flash("You do not have permission to edit this post.", "danger")
        return redirect(url_for("view_posts"))

    categories = BlogCategory.query.all()

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category_id = request.form.get("category_id", type=int)
        published = request.form.get("published") == "on"

        if not title or not content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("edit_post", post_id=post_id))

        post.title = title
        post.content = content
        post.category_id = category_id if category_id else None
        post.published = published
        post.updated_at = datetime.utcnow()
        db.session.commit()

        flash("Post updated successfully!", "success")
        return redirect(url_for("view_post", post_id=post_id))

    return render_template("edit_post.html", post=post, categories=categories)


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Check if user is the author
    if post.author_id != current_user.id:
        flash("You do not have permission to delete this post.", "danger")
        return redirect(url_for("view_posts"))

    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully!", "success")
    return redirect(url_for("my_posts"))


@app.route("/my-posts")
@login_required
def my_posts():
    page = request.args.get("page", 1, type=int)
    posts = (
        BlogPost.query.filter_by(author_id=current_user.id)
        .order_by(BlogPost.created_at.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("my_posts.html", posts=posts)


@app.route("/post/<int:post_id>/publish", methods=["POST"])
@login_required
def publish_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Check if user is the author
    if post.author_id != current_user.id:
        flash("You do not have permission to publish this post.", "danger")
        return redirect(url_for("view_posts"))

    post.published = not post.published
    db.session.commit()

    status = "published" if post.published else "unpublished"
    flash(f"Post {status} successfully!", "success")
    return redirect(url_for("my_posts"))


if __name__ == "__main__":
    app.run(debug=True)
