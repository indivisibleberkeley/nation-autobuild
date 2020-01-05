from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, SelectField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired

class SignupUploadForm(FlaskForm):
    csvfile = FileField("Signup CSV File", validators=[
        FileRequired(),
        FileAllowed(["csv", "txt"], "CSV files only")])
    submit = SubmitField("Upload")

class SignupColumnSelectForm(FlaskForm):
    date_col = SelectField("(Start) Date", validators=[DataRequired()])
    email_col = SelectField("Email", validators=[DataRequired()])
    role_col = SelectField("Role/Item", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def assign_choices(self, colnames):
        choices = [(str(i), name) for (i, name) in enumerate(colnames)]
        self.date_col.choices = choices
        self.email_col.choices = choices
        self.role_col.choices = choices

class SignupRoleAssignmentForm(FlaskForm):
    date_col  = HiddenField(validators=[DataRequired()])
    email_col = HiddenField(validators=[DataRequired()])
    role_col  = HiddenField(validators=[DataRequired()])
    signin_roles = SelectMultipleField("Signin Roles")
    delivery_roles = SelectMultipleField("Food Delivery Roles")
    snack_roles = SelectMultipleField("Snack Provider Roles")
    lunch_roles = SelectMultipleField("Lunch Provider Roles")
    submit = SubmitField("Submit")

    def assign_choices(self, roles):
        choices = [(role, role) for role in roles]
        self.signin_roles.choices = choices
        self.delivery_roles.choices = choices
        self.snack_roles.choices = choices
        self.lunch_roles.choices = choices

    def gen_rolemap(self):
        taglist = [
            ("signin", self.signin_roles),
            ("delivery", self.delivery_roles),
            ("snacks", self.snack_roles),
            ("lunch", self.lunch_roles)
        ]
        rolemap = {}

        for tag, field in taglist:
            for role in field.data:
                rolemap[role] = tag

        return rolemap
