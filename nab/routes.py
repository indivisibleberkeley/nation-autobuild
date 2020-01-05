from nab import app
from flask import render_template, redirect, request, make_response
from nab.forms import *
from nab.database import get_connection

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup/upload", methods=["GET", "POST"])
def signup_upload():
    form = SignupUploadForm()
    if form.validate_on_submit():
        with get_connection() as db:
            oid = db.store_signup_file(form.csvfile.data)
            return redirect("/signup/" + str(oid) + "/columns")
    return render_template("signup-upload.html", form=form)

@app.route("/signup/<uuid>/columns", methods=["GET", "POST"])
def signup_columns(uuid):
    with get_connection() as db:
        form = SignupColumnSelectForm()
        colnames = db.get_column_names(uuid)
        form.assign_choices(colnames)

        if form.validate_on_submit():
            date_col = form.date_col.data
            email_col = form.email_col.data
            role_col = form.role_col.data
            url_format = "/signup/{}/roles?date_col={}&email_col={}&role_col={}"
            return redirect(url_format.format(
                uuid, date_col, email_col, role_col))

        return render_template("signup-headers.html", form=form)

@app.route("/signup/<uuid>/roles", methods=["GET", "POST"])
def signup_roles(uuid):
    date_col = request.args["date_col"]
    email_col = request.args["email_col"]
    role_col = request.args["role_col"]

    with get_connection() as db:
        roles = db.get_unique_roles(uuid, role_col)
        form = SignupRoleAssignmentForm(
                date_col=date_col,
                email_col=email_col,
                role_col=role_col)
        form.assign_choices(roles)

        if form.validate_on_submit():
            date_col = form.date_col.data
            email_col = form.email_col.data
            role_col = form.role_col.data
            rolemap = form.gen_rolemap()
            db.generate_csv(uuid, date_col, email_col, role_col, rolemap)
            return redirect("/signup/{}/download".format(uuid))

        return render_template("signup-roles.html", form=form)

@app.route("/signup/<uuid>/download")
def signup_download(uuid):
    with get_connection() as db:
        csvdata = db.get_csv(uuid)
        response = make_response(csvdata)
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = "attachment; filename=result.csv"
        return response
