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


class FormWTFAjoutetype(FlaskForm):
    """
        Dans le formulaire "genres_ajouter_wtf.html" on impose que le champ soit rempli.
        Définition d'un "bouton" submit avec un libellé personnalisé.
    """

    type_wtf = StringField("Entre le type")

    submit = SubmitField("Enregistrer genre")

class FormWTFUpdatetype(FlaskForm):

    type_update_wtf = StringField("Entre le nouveau type")
    submit = SubmitField("Enregistrer genre")

class FormWTFDeletetype(FlaskForm):
    """
        Dans le formulaire "genre_delete_wtf.html"

        nom_genre_delete_wtf : Champ qui reçoit la valeur du genre, lecture seule. (readonly=true)
        submit_btn_del : Bouton d'effacement "DEFINITIF".
        submit_btn_conf_del : Bouton de confirmation pour effacer un "genre".
        submit_btn_annuler : Bouton qui permet d'afficher la table "t_genre".
    """
    type_delete_wtf = StringField("Effacer ce type ?")
    submit_btn_del = SubmitField("Effacer ")
    submit_btn_conf_del = SubmitField("Etes-vous sur d'effacer ?")
    submit_btn_annuler = SubmitField("Annuler")
