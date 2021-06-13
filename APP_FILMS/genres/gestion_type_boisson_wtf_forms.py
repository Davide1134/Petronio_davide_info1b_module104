"""
    Fichier : gestion_genres_wtf_forms.py
    Auteur : OM 2021.03.22
    Gestion des formulaires avec WTF
"""


from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import DateField
from wtforms.validators import Length
from wtforms.validators import Regexp

class FormWTFAjoutetypeboisson(FlaskForm):


   fk_boisson_wtf = StringField("Entre l'id de la boisson")
fk_type_wtf = StringField("Entre le l'id du type")
submit = SubmitField("Enregistrer")

