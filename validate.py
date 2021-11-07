from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, ValidationError

# FormにはFlaskFormを継承している。


class Form(FlaskForm):
    name = StringField("名前")

    def validate_name(self, name):
        if name.data == "":
            raise ValidationError("名前を入力してください")
