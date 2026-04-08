from backend.app import app, db

def add_column_if_not_exists(table, column_name, column_type):
    with app.app_context():
        try:
            db.session.execute(db.text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}"))
            db.session.commit()
            print(f"Added {column_name} to {table}")
        except Exception as e:
            db.session.rollback()
            print(f"Column {column_name} might already exist in {table}: {e}")

if __name__ == '__main__':
    add_column_if_not_exists('customers', 'score', 'INT DEFAULT 0')
    add_column_if_not_exists('customers', 'assigned_to', 'INT')
    add_column_if_not_exists('follow_ups', 'deal_id', 'INT')
    add_column_if_not_exists('follow_ups', 'is_conversion', 'BOOLEAN DEFAULT FALSE')
    add_column_if_not_exists('todos', 'due_date', 'DATETIME')
    
    with app.app_context():
        # This will create new tables like messages
        db.create_all()
        print("db.create_all() executed")
