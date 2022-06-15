import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_bargains")
def get_bargains():
    bargains = list(mongo.db.bargains.find())
    return render_template("bargains.html", bargains=bargains)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_bargain", methods=["GET", "POST"])
def add_bargain():
    # add new bargain
    if request.method == "POST":
        under_50 = "on" if request.form.get("under_50") else "off"
        bargain = {
            "category_name": request.form.get("category_name"),
            "bargain_name": request.form.get("bargain_name"),
            "bargain_img": request.form.get("bargain_img"),
            "bargain_description": request.form.get("bargain_description"),
            "bargain_link": request.form.get("bargain_link"),
            "under_50": under_50,
            "created_by": session["user"]
            # new func here
        }
        mongo.db.bargains.insert_one(bargain)
        flash("Bargain Successfully Added")
        return redirect(url_for("get_bargains"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_bargain.html", categories=categories)


@app.route("/edit_bargain/<bargain_id>", methods=["GET", "POST"])
def edit_bargain(bargain_id):
    # edit bargain
    if request.method == "POST":
        under_50 = "on" if request.form.get("under_50") else "off"
        submit = {
            "category_name": request.form.get("category_name"),
            "bargain_name": request.form.get("bargain_name"),
            "bargain_img": request.form.get("bargain_img"),
            "bargain_description": request.form.get("bargain_description"),
            "bargain_link": request.form.get("bargain_link"),
            "under_50": under_50,
            "created_by": session["user"]
            # new func here
        }
        mongo.db.bargains.update_one({"_id": ObjectId(bargain_id)}, {'$set':submit})
        flash("Task Successfully Updated")
        return redirect(url_for("get_bargains"))
        

    bargain = mongo.db.bargains.find_one({"_id": ObjectId(bargain_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_bargain.html", bargain=bargain, categories=categories)


@app.route("/delete_bargain/<bargain_id>")
def delete_bargain(bargain_id):
    # delete bargain
    mongo.db.bargains.delete_one({"_id": ObjectId(bargain_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("get_bargains"))


@app.route("/report_bargain/<bargain_id>", methods=["GET", "POST"])
def report_bargain(bargain_id):
    # report
    if request.method == "POST":
        report = {
            "reportcategory_name": request.form.get("reportcategory_name"),
            "bargain_name": request.form.get("bargain_name"),
            "bargain_comment": request.form.get("bargain_comment"),
        }
        mongo.db.reports.insert_one(report)
        flash("Bargain Successfully Reported")
        return redirect(url_for("get_bargains"))
        

    bargain = mongo.db.bargains.find_one({"_id": ObjectId(bargain_id)})
    reportcategories = mongo.db.reportcategories.find().sort("reportcategory_name", 1)
    return render_template("report_bargain.html", bargain=bargain, reportcategories=reportcategories,)

# MANAGE GAME CATEGORIES                 
@app.route("/get_categories")
def get_categories():
    # manage categories
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    # add categories
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    # delete device category
    mongo.db.categories.delete_one({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))


# MANAGE REPORT CATEGORIES                 
@app.route("/get_reportcategories")
def get_reportcategories():
    # manage categories
    reportcategories = list(mongo.db.reportcategories.find().sort("reportcategory_name", 1))
    return render_template("categories.html", reportcategories=reportcategories)

@app.route("/get_reports")
def get_reports():
    # report page
    reports = list(mongo.db.reports.find())
    return render_template("reports.html", reports=reports)


@app.route("/delete_report/<report_id>")
def delete_report(report_id):
    # delete report
    mongo.db.reports.delete_one({"_id": ObjectId(report_id)})
    flash("Report Successfully Deleted")
    return redirect(url_for("get_reports"))




if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)