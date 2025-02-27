from flask import Flask, render_template, request, redirect, url_for, flash
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Add a secret key for flash messages

# Sample Data: Books and Users (In-memory storage)
books = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "category": "Fiction", "available": 5},
    {"id": 2, "title": "1984", "author": "George Orwell", "category": "Dystopian", "available": 3},
    {"id": 3, "title": "To Kill a Mockingbird", "author": "Harper Lee", "category": "Fiction", "available": 2},
    {"id": 4, "title": "The Silent Patient", "author": "Alex Michaelides", "category": "Thriller", "available": 6}
]

borrowed_books = []  # Track borrowed books
users = []  # User management (for simplicity)

@app.route("/admin", methods=["GET"])
def admin_dashboard():
    search_query = request.args.get('search', '').lower()  # Get search query from URL args, default to empty string

    # Filter books based on search query
    if search_query:
        filtered_books = [book for book in books if search_query in book['title'].lower() or search_query in book['author'].lower() or search_query in book['category'].lower()]
    else:
        filtered_books = books  # Show all books if no search query

    return render_template("admin_dashboard.html", books=filtered_books, users=users)

# Add Book Route
@app.route("/admin/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        category = request.form["category"]
        available = int(request.form["available"])
        
        new_book = {
            "id": len(books) + 1,  # Assign a new ID
            "title": title,
            "author": author,
            "category": category,
            "available": available
        }
        books.append(new_book)
        flash(f"Book '{title}' added successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("add_book.html")

# Update Book Route
@app.route("/admin/update/<int:book_id>", methods=["GET", "POST"])
def update_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("admin_dashboard"))
    
    if request.method == "POST":
        # Update the book
        book["title"] = request.form["title"]
        book["author"] = request.form["author"]
        book["category"] = request.form["category"]
        book["available"] = int(request.form["available"])
        
        # Redirect back to the admin dashboard
        flash(f"Book '{book['title']}' updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    
    return render_template("update_book.html", book=book)

# Remove Book Route
@app.route("/admin/remove/<int:book_id>")
def remove_book(book_id):
    global books
    books = [b for b in books if b["id"] != book_id]
    flash("Book removed successfully!", "success")
    return redirect(url_for("admin_dashboard"))

# Borrow Book Route
@app.route("/borrow/<int:book_id>")
def borrow_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if book and book["available"] > 0:
        book["available"] -= 1
        borrowed_books.append({
            "book_id": book_id,
            "borrow_date": datetime.datetime.now(),
            "due_date": datetime.datetime.now() + datetime.timedelta(days=14)  # 14 days due
        })
        flash(f"Book '{book['title']}' successfully borrowed!", "success")  # Flash message
    else:
        flash("Sorry, this book is unavailable!", "error")
    return redirect(url_for("index"))

# View Overdue Books Route
@app.route("/overdue")
def overdue_books():
    overdue = []
    for record in borrowed_books:
        book = next((b for b in books if b["id"] == record["book_id"]), None)
        if book and record["due_date"] < datetime.datetime.now():
            overdue.append({
                "book": book,
                "borrow_date": record["borrow_date"],
                "due_date": record["due_date"],
                "fine": (datetime.datetime.now() - record["due_date"]).days * 1  # $1 per day fine
            })
    return render_template("overdue_books.html", overdue=overdue)

# Main Index Route
@app.route("/")
def index():
    return render_template("index.html", books=books)

if __name__ == "__main__":
    app.run(debug=True)
