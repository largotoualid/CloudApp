from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Replace with your actual Render DB URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myapp_db_er18_user:9u844kb8VabGIjfB11Y2C4nKKO510toZ@dpg-d081f0s9c44c73be2d00-a.oregon-postgres.render.com/myapp_db_er18'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return """
    <h2>Text Entry App</h2>
    <input type="text" id="entryText" placeholder="Enter text">
    <button onclick="addEntry()">Add</button>
    <ul id="entries"></ul>

    <script>
    async function loadEntries() {
        const res = await fetch('/entries');
        const data = await res.json();
        const ul = document.getElementById('entries');
        ul.innerHTML = '';
        data.forEach(entry => {
            const li = document.createElement('li');
            li.innerHTML = `
                <input value="${entry.text}" onchange="editEntry(${entry.id}, this.value)">
                <button onclick="deleteEntry(${entry.id})">Delete</button>
            `;
            ul.appendChild(li);
        });
    }

    async function addEntry() {
        const text = document.getElementById('entryText').value;
        if (text.trim()) {
            await fetch('/entries', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            document.getElementById('entryText').value = '';
            loadEntries();
        }
    }

    async function editEntry(id, newText) {
        await fetch('/entries/' + id, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: newText })
        });
    }

    async function deleteEntry(id) {
        await fetch('/entries/' + id, { method: 'DELETE' });
        loadEntries();
    }

    loadEntries();
    </script>
    """

@app.route('/entries', methods=['GET'])
def get_entries():
    entries = Entry.query.all()
    return jsonify([{'id': e.id, 'text': e.text} for e in entries])

@app.route('/entries', methods=['POST'])
def add_entry():
    data = request.get_json()
    entry = Entry(text=data['text'])
    db.session.add(entry)
    db.session.commit()
    return jsonify({'id': entry.id, 'text': entry.text}), 201

@app.route('/entries/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    data = request.get_json()
    entry = Entry.query.get(entry_id)
    if not entry:
        return jsonify({'error': 'Not found'}), 404
    entry.text = data['text']
    db.session.commit()
    return jsonify({'id': entry.id, 'text': entry.text})

@app.route('/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    entry = Entry.query.get(entry_id)
    if not entry:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'result': 'Deleted'})

if __name__ == '__main__':
    app.run(debug=True)
