from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "securevault"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------- DATABASE TABLES ---------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return redirect("/login")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        check = User.query.filter_by(email=email).first()

        if check:
            return "Email already exists"

        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session["user"] = user.id

            return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    passwords = Password.query.filter_by(user_id=session["user"]).all()

    return render_template("dashboard.html", passwords=passwords)


# ---------------- ADD PASSWORD ---------------- #

@app.route("/add", methods=["GET", "POST"])
def add():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        website = request.form["website"]
        email = request.form["email"]
        password = request.form["password"]

        new_password = Password(
            website=website,
            email=email,
            password=password,
            user_id=session["user"]
        )

        db.session.add(new_password)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("add.html")


# ---------------- DELETE PASSWORD ---------------- #

@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect("/login")

    data = Password.query.get(id)

    if data:
        db.session.delete(data)
        db.session.commit()

    return redirect("/dashboard")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


# ---------------- RUN ---------------- #

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)