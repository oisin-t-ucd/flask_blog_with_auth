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

from forms import (
    BlogCategoryForm,
    BlogPostForm,
    CommentForm,
    EditCommentForm,
    LoginForm,
    RegistrationForm,
)
from models import BlogCategory, BlogComment, BlogPost, User, db

load_dotenv()
app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "your-secret-key-change-this-in-production"
)
app.config["WTF_CSRF_ENABLED"] = True

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
    # db.drop_all() uncomment this to reset the database when you next start the server
    db.create_all()


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
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

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


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
    form = BlogCategoryForm()
    if form.validate_on_submit():
        category = BlogCategory(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()

        flash("Category created successfully!", "success")
        return redirect(url_for("view_categories"))

    return render_template("create_category.html", form=form)


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
    form = BlogCategoryForm(category_id=category_id)

    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()

        flash("Category updated successfully!", "success")
        return redirect(url_for("view_categories"))

    elif request.method == "GET":
        form.name.data = category.name
        form.description.data = category.description

    return render_template("edit_category.html", category=category, form=form)


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
    comments = BlogComment.query.filter_by(post_id=post_id).all()
    form = CommentForm()
    print("comments:")
    print(comments)

    # Check if post is published or if user is the author
    if not post.published:
        if not current_user.is_authenticated or current_user.id != post.author_id:
            flash("This post is not available.", "danger")
            return redirect(url_for("view_posts"))

    return render_template("post_detail.html", post=post, form=form)


@app.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        category_id = form.category_id.data if form.category_id.data != 0 else None
        post = BlogPost(
            title=form.title.data,
            content=form.content.data,
            category_id=category_id,
            author_id=current_user.id,
            published=form.published.data,
        )
        db.session.add(post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for("my_posts"))

    return render_template("create_post.html", form=form)


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Check if user is the author
    if post.author_id != current_user.id:
        flash("You do not have permission to edit this post.", "danger")
        return redirect(url_for("view_posts"))

    form = BlogPostForm()
    if form.validate_on_submit():
        category_id = form.category_id.data if form.category_id.data != 0 else None
        post.title = form.title.data
        post.content = form.content.data
        post.category_id = category_id
        post.published = form.published.data
        post.updated_at = datetime.utcnow()
        db.session.commit()

        flash("Post updated successfully!", "success")
        return redirect(url_for("view_post", post_id=post_id))

    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.category_id.data = post.category_id if post.category_id else 0
        form.published.data = post.published

    return render_template("edit_post.html", post=post, form=form)


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


@app.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = BlogComment.query.get_or_404(comment_id)

    # Check if user is the author
    if comment.author_id != current_user.id:
        flash("You do not have permission to delete this comment.", "danger")
        return redirect(url_for("view_post", post_id=comment.post_id))

    db.session.delete(comment)
    db.session.commit()

    flash("Comment deleted successfully!", "success")
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


# COMMENT ROUTES


@app.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    post = BlogPost.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = BlogComment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()

        flash("Comment added!")
        return redirect(url_for("view_post", post_id=post.id))
    else:
        # If validation fails, show errors and redirect back
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", "danger")
        return redirect(url_for("view_post", post_id=post.id))


@app.route("/comment/<int:comment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    comment = BlogComment.query.get_or_404(comment_id)

    # Check if user is the author
    if comment.author_id != current_user.id:
        flash("You do not have permission to edit this comment.", "danger")
        return redirect(url_for("view_posts"))

    form = EditCommentForm()
    if form.validate_on_submit():
        comment.content = form.content.data
        comment.updated_at = datetime.utcnow()
        db.session.commit()

        flash("Comment updated successfully!", "success")
        return redirect(url_for("view_post", post_id=comment.post_id))

    elif request.method == "GET":
        form.content.data = comment.content

    return render_template("edit_comment.html", comment=comment, form=form)


if __name__ == "__main__":
    app.run(debug=True)
