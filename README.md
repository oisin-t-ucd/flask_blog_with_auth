# Flask Blog Application

A complete Flask blog application with user authentication, blog post management, and category organization.

## Features

✅ **User Authentication**
- User registration with email and username validation
- Login/logout functionality
- Password hashing with Werkzeug security

✅ **Blog Post Management**
- Create, read, update, delete (CRUD) blog posts
- Mark posts as published/draft
- View all published posts or user's own posts
- Edit and delete own posts only

✅ **Blog Categories**
- Create and manage blog categories
- Assign posts to categories
- Filter posts by category

✅ **User Dashboard**
- View statistics (total posts, published count, categories)
- Quick access to create posts and manage categories
- View all personal posts

✅ **HTML Templates**
- Bootstrap 5 styling
- Responsive design
- User-friendly interface
- Flash messages for user feedback

## Project Structure

```
flask_blog_db/
├── app.py              # Main Flask application with all routes
├── models.py           # Database models (User, BlogCategory, BlogPost)
├── requirements.txt    # Python dependencies
├── blog.db             # SQLite database (created on first run)
└── templates/
    ├── base.html              # Base template with navigation
    ├── home.html              # Homepage with latest published posts
    ├── register.html          # User registration page
    ├── login.html             # User login page
    ├── dashboard.html         # User dashboard
    ├── create_post.html       # Create new blog post
    ├── edit_post.html         # Edit existing blog post
    ├── my_posts.html          # View all user's posts
    ├── post_detail.html       # View single post
    ├── posts.html             # View all published posts with filtering
    ├── create_category.html   # Create new category
    ├── edit_category.html     # Edit category
    └── categories.html        # View all categories
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Steps

1. **Navigate to project directory:**
   ```bash
   cd /Users/alt/Code/flask_blog_db
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your browser and go to: `http://localhost:5000`

## Database

The application uses SQLite for data persistence. The database file (`blog.db`) is automatically created on first run.

### Database Models

**User**
- id, username, email, password_hash, created_at
- Relationships: One-to-Many with BlogPost

**BlogCategory**
- id, name, description, created_at
- Relationships: One-to-Many with BlogPost

**BlogPost**
- id, title, content, published, created_at, updated_at
- Foreign keys: author_id (User), category_id (BlogCategory)

## Usage

### For Anonymous Users
- View homepage with latest published posts
- View all published blog posts
- Browse categories
- Register for an account
- Login to create posts

### For Logged-In Users
- **Dashboard**: View statistics and quick actions
- **Create Post**: Write and publish new blog posts
- **My Posts**: Manage personal posts (view, edit, delete, publish/unpublish)
- **Create Category**: Create new post categories
- **Edit Category**: Modify or delete categories

### Routes Overview

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Homepage |
| `/register` | GET, POST | User registration |
| `/login` | GET, POST | User login |
| `/logout` | GET | User logout |
| `/dashboard` | GET | User dashboard |
| `/posts` | GET | View all published posts |
| `/post/<id>` | GET | View single post |
| `/post/create` | GET, POST | Create new post |
| `/post/<id>/edit` | GET, POST | Edit post |
| `/post/<id>/delete` | POST | Delete post |
| `/post/<id>/publish` | POST | Toggle publish status |
| `/my-posts` | GET | View user's posts |
| `/categories` | GET | View all categories |
| `/category/create` | GET, POST | Create category |
| `/category/<id>/edit` | GET, POST | Edit category |
| `/category/<id>/delete` | POST | Delete category |

## Configuration

Edit the `app.py` file to change:
- `SECRET_KEY`: Change this in production!
- `SQLALCHEMY_DATABASE_URI`: Database URL
- `DEBUG`: Set to False in production

## Security Notes

⚠️ **Important for Production:**
- Change the `SECRET_KEY` to a strong random string
- Set `app.run(debug=False)` in production
- Use environment variables for sensitive configuration
- Add CSRF protection to forms
- Implement rate limiting for login attempts
- Use HTTPS in production

## Features You Can Add

- Comment system on posts
- Post likes/ratings
- User profiles
- Email notifications
- Search functionality
- Tags in addition to categories
- Rich text editor for posts
- Image uploads
- Social sharing buttons

## License

This project is open source and available under the MIT License.
