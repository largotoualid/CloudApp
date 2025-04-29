from flask import Flask, request, redirect
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

app = Flask(__name__)

# PostgreSQL connection string (Render)
DATABASE_URL = "postgresql://myapp_db_er18_user:9u844kb8VabGIjfB11Y2C4nKKO510toZ@dpg-d081f0s9c44c73be2d00-a.oregon-postgres.render.com/myapp_db_er18"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Model
class TextEntry(Base):
    __tablename__ = 'text_entries'
    id = Column(Integer, primary_key=True)
    content = Column(String)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content")
        if content:
            new_entry = TextEntry(content=content)
            session.add(new_entry)
            session.commit()
        return redirect("/")

    entries = session.query(TextEntry).all()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Text Manager</title>
    </head>
    <body>
        <h1>Text Saver App</h1>
        <form method="POST">
            <input type="text" name="content" placeholder="Enter text" required>
            <button type="submit">Save</button>
        </form>
        <hr>
        <h2>Saved Entries</h2>
    """

    for entry in entries:
        html += f"""
        <form method="POST" action="/update/{entry.id}">
            <input type="text" name="content" value="{entry.content}">
            <button type="submit">Update</button>
            <a href="/delete/{entry.id}">Delete</a>
        </form><br>
        """

    html += """
    </body>
    </html>
    """
    return html

@app.route("/update/<int:entry_id>", methods=["POST"])
def update(entry_id):
    new_content = request.form.get("content")
    entry = session.get(TextEntry, entry_id)
    if entry:
        entry.content = new_content
        session.commit()
    return redirect("/")

@app.route("/delete/<int:entry_id>")
def delete(entry_id):
    entry = session.get(TextEntry, entry_id)
    if entry:
        session.delete(entry)
        session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
