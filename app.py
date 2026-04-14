import sqlite3
from flask import Flask, redirect, render_template, request, session, abort
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
import items

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    all_items = items.get_items(query)
    return render_template("index.html", items=all_items, query=query)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    return render_template("show_item.html", item=item)

@app.route("/new_item")
def new_item():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("new_item.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    start_time = request.form.get("start_time", "").strip()

    if not title:
        return "VIRHE: otsikko vaaditaan", 400

    items.add_item(title, description, start_time, session["user_id"])
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

    return render_template("edit_item.html", item=item)

@app.route("/update_item", methods=["POST"])
def update_item():
    if "user_id" not in session:
        return redirect("/login")

    item_id = request.form.get("item_id")
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    start_time = request.form.get("start_time", "").strip()

    if not item_id:
        return "VIRHE: ilmoituksen id puuttuu", 400

    item = items.get_item(item_id)
    if item is None:
        abort(404)

    if item["user_id"] != session["user_id"]:
        return "Ei oikeuksia muokata tätä ilmoitusta", 403

    items.update_item(item_id, title, description, start_time or None)
    return redirect("/item/" + str(item_id))

@app.route("/delete_item", methods=["POST"])
def delete_item():
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


