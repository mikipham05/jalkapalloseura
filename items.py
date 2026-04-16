import db

def add_item(title, description, event_date, start_time, user_id, category_ids=None):
    sql = """INSERT INTO items (title, description, event_date, start_time, user_id)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [title, description, event_date, start_time, user_id])
    item_id = db.last_insert_id()
    set_item_categories(item_id, category_ids or [])


def get_items(search_term=None):
    if not search_term:
        sql = "SELECT id, title FROM items ORDER BY id DESC"
        return db.query(sql)

    sql = """SELECT DISTINCT items.id, items.title FROM items
             LEFT JOIN item_categories ON items.id = item_categories.item_id
             LEFT JOIN categories ON item_categories.category_id = categories.id
             WHERE items.title LIKE ?
               OR items.description LIKE ?
               OR items.start_time LIKE ?
               OR items.event_date LIKE ?
               OR categories.name LIKE ?
             ORDER BY items.id DESC"""
    wildcard = f"%{search_term}%"
    return db.query(sql, [wildcard, wildcard, wildcard, wildcard, wildcard])


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
    if not results:
        return None

    item = dict(results[0])
    item["categories"] = get_item_categories(item_id)
    return item


def update_item(item_id, title, description, event_date=None, start_time=None, category_ids=None):
    sql_parts = ["title = ?", "description = ?"]
    params = [title, description]
    if event_date is not None:
        sql_parts.append("event_date = ?")
        params.append(event_date)
    if start_time is not None:
        sql_parts.append("start_time = ?")
        params.append(start_time)
    params.append(item_id)
    sql = f"UPDATE items SET {', '.join(sql_parts)} WHERE id = ?"
    db.execute(sql, params)
    if category_ids is not None:
        set_item_categories(item_id, category_ids)


def delete_item(item_id):
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])


def get_categories():
    sql = "SELECT id, name FROM categories ORDER BY name"
    return db.query(sql)


def get_item_categories(item_id):
    sql = """SELECT categories.id, categories.name FROM categories
             JOIN item_categories ON categories.id = item_categories.category_id
             WHERE item_categories.item_id = ?
             ORDER BY categories.name"""
    return [row["name"] for row in db.query(sql, [item_id])]


def get_item_category_ids(item_id):
    sql = "SELECT category_id FROM item_categories WHERE item_id = ?"
    return [row["category_id"] for row in db.query(sql, [item_id])]


def set_item_categories(item_id, category_ids):
    db.execute("DELETE FROM item_categories WHERE item_id = ?", [item_id])
    for category_id in category_ids:
        db.execute("INSERT OR IGNORE INTO item_categories (item_id, category_id) VALUES (?, ?)", [item_id, category_id])


def get_comments(item_id):
    sql = """SELECT comments.id, comments.content, comments.created_at,
                   users.id AS user_id, users.username
             FROM comments
             JOIN users ON comments.user_id = users.id
             WHERE comments.item_id = ?
             ORDER BY comments.created_at ASC"""
    return db.query(sql, [item_id])


def add_comment(item_id, user_id, content):
    sql = "INSERT INTO comments (item_id, user_id, content) VALUES (?, ?, ?)"
    db.execute(sql, [item_id, user_id, content])


def get_user_by_username(username):
    sql = "SELECT id, username FROM users WHERE username = ?"
    results = db.query(sql, [username])
    return results[0] if results else None


def get_items_by_user(user_id):
    sql = "SELECT id, title FROM items WHERE user_id = ? ORDER BY id DESC"
    return db.query(sql, [user_id])


def get_user_stats(user_id):
    sql = """SELECT
               COUNT(DISTINCT items.id) AS item_count,
               COUNT(comments.id) AS comment_count
             FROM users
             LEFT JOIN items ON items.user_id = users.id
             LEFT JOIN comments ON comments.user_id = users.id
             WHERE users.id = ?"""
    results = db.query(sql, [user_id])
    return results[0] if results else {"item_count": 0, "comment_count": 0}


def get_response_counts(item_id):
    sql = """SELECT
               SUM(CASE WHEN response = 'IN' THEN 1 ELSE 0 END) AS in_count,
               SUM(CASE WHEN response = 'OUT' THEN 1 ELSE 0 END) AS out_count
             FROM responses
             WHERE item_id = ?"""
    results = db.query(sql, [item_id])
    counts = results[0] if results else None
    return {
        "in_count": counts["in_count"] or 0,
        "out_count": counts["out_count"] or 0,
    }


def get_user_response(item_id, user_id):
    sql = "SELECT response FROM responses WHERE item_id = ? AND user_id = ?"
    results = db.query(sql, [item_id, user_id])
    return results[0]["response"] if results else None


def set_user_response(item_id, user_id, response):
    sql = "INSERT INTO responses (item_id, user_id, response) VALUES (?, ?, ?)"
    try:
        db.execute(sql, [item_id, user_id, response])
    except Exception:
        sql = "UPDATE responses SET response = ? WHERE item_id = ? AND user_id = ?"
        db.execute(sql, [response, item_id, user_id])

