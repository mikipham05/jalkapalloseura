import sqlite3
from flask import Flask, redirect, render_template, request, session, abort
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
import items
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

@app.context_processor
def inject_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return dict(csrf_token=session['csrf_token'])

def check_csrf():
    token = request.form.get('csrf_token')
    if not token or token != session.get('csrf_token'):
        abort(403)

@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    category_id_str = request.args.get("category", "").strip()
    category_id = int(category_id_str) if category_id_str.isdigit() else None
    categories = items.get_categories()
    all_items = items.get_items(query, category_id)
    return render_template("index.html", items=all_items, query=query, categories=categories, selected_category=category_id)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    comments = items.get_comments(item_id)
    response_counts = items.get_response_counts(item_id)
    current_response = None
    if "user_id" in session:
        current_response = items.get_user_response(item_id, session["user_id"])
    return render_template("show_item.html", item=item, comments=comments, response_counts=response_counts, current_response=current_response)

@app.route("/item/<int:item_id>/comment", methods=["POST"])
def add_item_comment(item_id):
    check_csrf()
    if "user_id" not in session:
        return redirect("/login")

    item = items.get_item(item_id)
    if item is None:
        abort(404)

    content = request.form.get("content", "").strip()
    if content:
        items.add_comment(item_id, session["user_id"], content)

    return redirect("/item/" + str(item_id))

@app.route("/item/<int:item_id>/response", methods=["POST"])
def add_item_response(item_id):
    check_csrf()
    if "user_id" not in session:
        return redirect("/login")

    item = items.get_item(item_id)
    if item is None:
        abort(404)

    response = request.form.get("response")
    if response in ["IN", "OUT"]:
        items.set_user_response(item_id, session["user_id"], response)

    return redirect("/item/" + str(item_id))

@app.route("/comment/<int:comment_id>/edit", methods=["GET", "POST"])
def edit_comment(comment_id):
    if "user_id" not in session:
        return redirect("/login")

    comment = items.get_comment_by_id(comment_id)
    if comment is None:
        abort(404)

    if comment["user_id"] != session["user_id"]:
        return "Ei oikeuksia muokata tätä kommenttia", 403

    if request.method == "POST":
        check_csrf()
        content = request.form.get("content", "").strip()
        if not content:
            return "Kommentti ei voi olla tyhjä", 400
        items.update_comment(comment_id, content)
        return redirect("/item/" + str(comment["item_id"]))

    return render_template("edit_comment.html", comment=comment)

@app.route("/comment/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    check_csrf()
    if "user_id" not in session:
        return redirect("/login")

    comment = items.get_comment_by_id(comment_id)
    if comment is None:
        abort(404)

    if comment["user_id"] != session["user_id"]:
        return "Ei oikeuksia poistaa tätä kommenttia", 403

    items.delete_comment(comment_id)
    return redirect("/item/" + str(comment["item_id"]))

@app.route("/user/<username>")
def user_page(username):
    user = items.get_user_by_username(username)
    if user is None:
        abort(404)

    user_items = items.get_items_by_user(user["id"])
    stats = items.get_user_stats(user["id"])
    return render_template("user.html", user=user, items=user_items, stats=stats)

@app.route("/new_item")
def new_item():
    if "user_id" not in session:
        return redirect("/login")

    categories = items.get_categories()
    return render_template("new_item.html", categories=categories)

@app.route("/create_item", methods=["POST"])
def create_item():
    check_csrf()
    if "user_id" not in session:
        return redirect("/login")

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    event_date = request.form.get("event_date", "").strip()
    start_time = request.form.get("start_time", "").strip()
    category_id = request.form.get("category")

    if not title:
        return "VIRHE: otsikko vaaditaan", 400

    category_ids = [category_id] if category_id else []
    items.add_item(title, description, event_date, start_time, session["user_id"], category_ids)
    return redirect("/")

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    if "user_id" not in session:
        return redirect("/login")

    item = items.get_item(item_id)
    if item is None:
        abort(404)

    if item["user_id"] != session["user_id"]:
        return "Ei oikeuksia muokata tätä ilmoitusta", 403

    categories = items.get_categories()
    selected_category_ids = items.get_item_category_ids(item_id)
    selected_category_id = selected_category_ids[0] if selected_category_ids else None
    return render_template("edit_item.html", item=item, categories=categories, selected_category_id=selected_category_id)

@app.route("/update_item", methods=["POST"])
def update_item():
    check_csrf()
    if "user_id" not in session:
        return redirect("/login")

    item_id = request.form.get("item_id")
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    event_date = request.form.get("event_date", "").strip()
    start_time = request.form.get("start_time", "").strip()
    category_id = request.form.get("category")

    if not item_id:
        return "VIRHE: ilmoituksen id puuttuu", 400

    item = items.get_item(item_id)
    if item is None:
        abort(404)

    if item["user_id"] != session["user_id"]:
        return "Ei oikeuksia muokata tätä ilmoitusta", 403

    category_ids = [category_id] if category_id else []
    items.update_item(item_id, title, description, event_date or None, start_time or None, category_ids)
    return redirect("/item/" + str(item_id))

@app.route("/delete_item", methods=["POST"])
def delete_item():
    check_csrf()
    if "user_id" not in session:
        return redirect("/login")

    item_id = request.form.get("item_id")
    if not item_id:
        return "VIRHE: ilmoituksen id puuttuu", 400

    item = items.get_item(item_id)
    if item is None:
        abort(404)

    if item["user_id"] != session["user_id"]:
        return "Ei oikeuksia poistaa tätä ilmoitusta", 403

    items.delete_item(item_id)
    return redirect("/")

@app.route("/register")
def register():
    if "user_id" in session:
        return redirect("/")
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    check_csrf()
    username = request.form.get("username", "").strip()
    password1 = request.form.get("password1", "")
    password2 = request.form.get("password2", "")

    if not username:
        return "VIRHE: käyttäjätunnus vaaditaan", 400

    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat", 400

    password_hash = generate_password_hash(password1)
    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu", 400

    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect("/")
        return render_template("login.html")

    check_csrf()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    results = db.query("SELECT id, password_hash FROM users WHERE username = ?", [username])
    if not results:
        return "VIRHE: väärä tunnus tai salasana", 400

    result = results[0]
    if check_password_hash(result["password_hash"], password):
        session["user_id"] = result["id"]
        session["username"] = username
        return redirect("/")

    return "VIRHE: väärä tunnus tai salasana", 400

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect("/")

