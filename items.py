import db

def add_item(title, description, event_date, start_time, user_id):
    sql = """INSERT INTO items (title, description, event_date, start_time, user_id)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [title, description, event_date, start_time, user_id])

def get_items(search_term=None):
    if not search_term:
        sql = "SELECT id, title FROM items ORDER BY id DESC"
        return db.query(sql)

    sql = """SELECT id, title FROM items
             WHERE title LIKE ? OR description LIKE ? OR start_time LIKE ? OR event_date LIKE ?
             ORDER BY id DESC"""
    wildcard = f"%{search_term}%"
    return db.query(sql, [wildcard, wildcard, wildcard, wildcard])

def get_item(item_id):
    sql = """SELECT items.id,
                   items.title,
                   items.description,
                   items.event_date,
                   items.start_time,
                   users.id AS user_id,
                   users.username
            FROM items
            JOIN users ON items.user_id = users.id
            WHERE items.id = ?"""
    results = db.query(sql, [item_id])
    return results[0] if results else None

def update_item(item_id, title, description, event_date=None, start_time=None):
    if event_date is None and start_time is None:
        sql = """UPDATE items SET title = ?,
                                   description = ?
                 WHERE id = ?"""
        db.execute(sql, [title, description, item_id])
    elif event_date is None:
        sql = """UPDATE items SET title = ?,
                                   description = ?,
                                   start_time = ?
                 WHERE id = ?"""
        db.execute(sql, [title, description, start_time, item_id])
    elif start_time is None:
        sql = """UPDATE items SET title = ?,
                                   description = ?,
                                   event_date = ?
                 WHERE id = ?"""
        db.execute(sql, [title, description, event_date, item_id])
    else:
        sql = """UPDATE items SET title = ?,
                                   description = ?,
                                   event_date = ?,
                                   start_time = ?
                 WHERE id = ?"""
        db.execute(sql, [title, description, event_date, start_time, item_id])

def delete_item(item_id):
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])
