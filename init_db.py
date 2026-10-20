from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Tables created:", db.inspect(db.engine).get_table_names())

