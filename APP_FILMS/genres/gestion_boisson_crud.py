"""
    Fichier : gestion_genres_crud.py
    Auteur : OM 2021.03.16
    Gestions des "routes" FLASK et des données pour les genres.
"""
import re
import sys

from flask import flash, session
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask_wtf import form

from APP_FILMS import obj_mon_application
from APP_FILMS.database.connect_db_context_manager import MaBaseDeDonnee
from APP_FILMS.erreurs.msg_erreurs import *
from APP_FILMS.erreurs.exceptions import *
from APP_FILMS.essais_wtf_forms.wtf_forms_1 import MonPremierWTForm
from APP_FILMS.genres.gestion_boisson_wtf_forms import FormWTFAjouterboisson
from APP_FILMS.genres.gestion_boisson_wtf_forms import FormWTFUpdateboisson
from APP_FILMS.genres.gestion_boisson_wtf_forms import FormWTFDeleteboisson


@obj_mon_application.route("/boisson_afficher/<string:order_by>/<int:Id_boisson_sel>", methods=['GET', 'POST'])
def boisson_afficher(order_by, Id_boisson_sel):
    if request.method == "GET":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion genres ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur GestionGenres {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            with MaBaseDeDonnee().connexion_bd.cursor() as mc_afficher:
                if order_by == "ASC" and Id_boisson_sel == 0:
                    strsql_boisson_afficher = """SELECT Id_boisson, Marque, Prix_boisson,Quantite_boisson,Date_achat_boisson,Date_peremption_boisson FROM t_boisson ORDER BY Id_boisson ASC"""
                    mc_afficher.execute(strsql_boisson_afficher)
                elif order_by == "ASC":
                    # C'EST LA QUE VOUS ALLEZ DEVOIR PLACER VOTRE PROPRE LOGIQUE MySql
                    # la commande MySql classique est "SELECT * FROM t_boisson"
                    # Pour "lever"(raise) une erreur s'il y a des erreurs sur les noms d'attributs dans la table
                    # donc, je précise les champs à afficher
                    # Constitution d'un dictionnaire pour associer l'id du genre sélectionné avec un nom de variable
                    valeur_Id_boisson_selected_dictionnaire = {"value_Id_boisson_selected": Id_boisson_sel}
                    strsql_boisson_afficher = """SELECT Id_boisson, Marque, Prix_boisson,Quantite_boisson,Date_achat_boisson,Date_peremption_boisson FROM t_boisson  WHERE Id_boisson = %(value_Id_boisson_selected)s"""

                    mc_afficher.execute(strsql_boisson_afficher, valeur_Id_boisson_selected_dictionnaire)
                else:
                    strsql_boisson_afficher = """SELECT Id_boisson, Marque, Prix_boisson,Quantite_boisson,Date_achat_boisson,Date_peremption_boisson FROM t_boisson ORDER BY Id_boisson DESC"""

                    mc_afficher.execute(strsql_boisson_afficher)

                data_boisson = mc_afficher.fetchall()

                print("data_boisson ", data_boisson, " Type : ", type(data_boisson))

                # Différencier les messages si la table est vide.
                if not data_boisson and Id_boisson_sel == 0:
                    flash("""La table "t_boisson" est vide. !!""", "warning")
                elif not data_boisson and Id_boisson_sel > 0:
                    # Si l'utilisateur change l'Id_boisson dans l'URL et que le genre n'existe pas,
                    flash(f"Le Compte demandé n'existe pas !!", "warning")
                else:
                    # Dans tous les autres cas, c'est que la table "t_boisson" est vide.
                    # OM 2020.04.09 La ligne ci-dessous permet de donner un sentiment rassurant aux utilisateurs.
                    flash(f"Comptes affichés !!", "success")

        except Exception as erreur:
            print(f"RGG Erreur générale.")
            # OM 2020.04.09 On dérive "Exception" par le "@obj_mon_application.errorhandler(404)" fichier "run_mon_app.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            flash(f"RGG Exception {erreur}")
            raise Exception(f"RGG Erreur générale. {erreur}")
            raise MaBdErreurOperation(f"RGG Exception {msg_erreurs['ErreurNomBD']['message']} {erreur}")

    # Envoie la page "HTML" au serveur.
    return render_template("genres/boisson_afficher.html", data=data_boisson)


"""
    Auteur : OM 2021.03.22
    Définition d'une "route" /genres_ajouter

    Test : ex : http://127.0.0.1:5005/genres_ajouter

    Paramètres : sans

    But : Ajouter un genre pour un film

    Remarque :  Dans le champ "Marque_html" du formulaire "genres/genres_ajouter.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@obj_mon_application.route("/boisson_ajouter", methods=['GET', 'POST'])
def boisson_ajouter_wtf():
    form = FormWTFAjouterboisson()
    if request.method == "POST":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion genres ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur GestionGenres {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            if form.validate_on_submit():
                Marque_wtf = form.Marque_wtf.data
                Prix_boisson_wtf = form.Prix_boisson_wtf.data
                Quantite_boisson_wtf = form.Quantite_boisson_wtf.data
                Date_achat_boisson_wtf = form.Date_achat_boisson_wtf.data
                Date_peremption_boisson_wtf = form.Date_peremption_boisson_wtf.data
                
                

                valeurs_insertion_dictionnaire = {"value_Marque": Marque_wtf,
                                                  "value_Prix_boisson_wtf": Prix_boisson_wtf,
                                                  "value_Quantite_boisson_wtf": Quantite_boisson_wtf,
                                                  "value_Date_achat_boisson_wtf": Date_achat_boisson_wtf,
                                                  "value_Date_peremption_boisson_wtf": Date_peremption_boisson_wtf,
                                                  }
                print("valeurs_insertion_dictionnaire ", valeurs_insertion_dictionnaire)

                strsql_insert_boisson = """INSERT INTO t_boisson (Id_boisson,Marque, Prix_boisson,Quantite_boisson,Date_achat_boisson,Date_peremption_boisson) VALUES (NULL,%(value_Marque)s,%(value_Prix_boisson_wtf)s,%(value_Quantite_boisson_wtf)s,%(value_Date_achat_boisson_wtf)s,%(value_Date_peremption_boisson_wtf)s)"""
                with MaBaseDeDonnee() as mconn_bd:
                    mconn_bd.mabd_execute(strsql_insert_boisson, valeurs_insertion_dictionnaire)

                flash(f"Données insérées !!", "success")
                print(f"Données insérées !!")

                # Pour afficher et constater l'insertion de la valeur, on affiche en ordre inverse. (DESC)
                return redirect(url_for('boisson_afficher', order_by='DESC', Id_boisson_sel=0))

        # ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except pymysql.err.IntegrityError as erreur_genre_doublon:
            # Dérive "pymysql.err.IntegrityError" dans "MaBdErreurDoublon" fichier "erreurs/exceptions.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            code, msg = erreur_genre_doublon.args

            flash(f"{error_codes.get(code, msg)} ", "warning")

        # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except (pymysql.err.OperationalError,
                pymysql.ProgrammingError,
                pymysql.InternalError,
                TypeError) as erreur_gest_genr_crud:
            code, msg = erreur_gest_genr_crud.args

            flash(f"{error_codes.get(code, msg)} ", "danger")
            flash(f"Erreur dans Gestion genres CRUD : {sys.exc_info()[0]} "
                  f"{erreur_gest_genr_crud.args[0]} , "
                  f"{erreur_gest_genr_crud}", "danger")

    return render_template("genres/boisson_ajouter_wtf.html", form=form)



"""
    Auteur : OM 2021.03.29
    Définition d'une "route" /genre_update

    Test : ex cliquer sur le menu "genres" puis cliquer sur le bouton "EDIT" d'un "genre"

    Paramètres : sans

    But : Editer(update) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"

    Remarque :  Dans le champ "nom_genre_update_wtf" du formulaire "genres/genre_update_wtf.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@obj_mon_application.route("/boisson_update", methods=['GET', 'POST'])
def boisson_update_wtf():
    # L'utilisateur vient de cliquer sur le bouton "EDIT". Récupère la valeur de "Id_boisson"
    Id_boisson_update = request.values['Id_boisson_btn_edit_html']

    # Objet formulaire pour l'UPDATE
    form_update = FormWTFUpdateboisson()
    try:
        print(" on submit ", form_update.validate_on_submit())
        if form_update.validate_on_submit():
            # Récupèrer la valeur du champ depuis "genre_update_wtf.html" après avoir cliqué sur "SUBMIT".
            # Puis la convertir en lettres minuscules.
            Marque_update = form_update.Marque_update_wtf.data
            Marque_update = Marque_update.capitalize()

            Prix_boisson_update = form_update.Prix_boisson_update_wtf.data
            Prix_boisson_update = Prix_boisson_update.capitalize()

            Quantite_boisson_update = form_update.Quantite_boisson_update_wtf.data
            Quantite_boisson_update = Quantite_boisson_update.capitalize()

            Date_achat_boisson_update = form_update.Date_achat_boisson_update_wtf.data

            Date_peremption_boisson_update = form_update.Date_peremption_boisson_update_wtf.data

            valeur_update_dictionnaire = {"value_Id_boisson": Id_boisson_update,
                                          "value_Marque": Marque_update,
                                          "value_Prix_boisson": Prix_boisson_update,
                                          "value_Quantite_boisson": Quantite_boisson_update,
                                          "value_Date_achat_boisson": Date_achat_boisson_update,
                                          "value_Date_peremption_boisson": Date_peremption_boisson_update
                                          }

            print("valeur_update_dictionnaire ", valeur_update_dictionnaire)

            str_sql_update_intitulegenre = """UPDATE t_boisson SET Marque = %(value_Marque)s,Prix_boisson = %(value_Prix_boisson)s,Quantite_boisson = %(value_Quantite_boisson)s,Date_achat_boisson = %(value_Date_achat_boisson)s,Date_peremption_boisson = %(value_Date_peremption_boisson)s WHERE Id_boisson = %(value_Id_boisson)s"""

            with MaBaseDeDonnee() as mconn_bd:
                mconn_bd.mabd_execute(str_sql_update_intitulegenre, valeur_update_dictionnaire)

            flash(f"Compte mis à jour !!", "success")
            print(f"Compte mis à jour !!")

            # afficher et constater que la donnée est mise à jour.
            # Affiche seulement la valeur modifiée, "ASC" et l'"Id_boisson_update"
            return redirect(url_for('boisson_afficher', order_by="ASC", Id_boisson_sel=0))
        elif request.method == "GET":
            # Opération sur la BD pour récupérer "Id_boisson" et "intitule_genre" de la "t_boisson"
            str_sql_Id_boisson = "SELECT Id_boisson, Marque,Prix_boisson,Quantite_boisson,Date_achat_boisson,Date_peremption_boisson  FROM t_boisson WHERE Id_boisson = %(value_Id_boisson)s"
            valeur_select_dictionnaire = {"value_Id_boisson": Id_boisson_update}
            mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()
            mybd_curseur.execute(str_sql_Id_boisson, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()", vu qu'il n'y a qu'un seul champ "nom genre" pour l'UPDATE
            data_boisson = mybd_curseur.fetchone()

            print(" ", data_boisson, " type ", type(data_boisson), " genre ",
                  data_boisson["Marque"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "genre_update_wtf.html"
            form_update.Marque_update_wtf.data = data_boisson["Marque"]
            form_update.Prix_boisson_update_wtf.data = data_boisson["Prix_boisson"]
            form_update.Quantite_boisson_update_wtf.data = data_boisson["Quantite_boisson"]
            form_update.Date_achat_boisson_update_wtf.data = data_boisson["Date_achat_boisson"]
            form_update.Date_peremption_boisson_update_wtf.data = data_boisson["Date_peremption_boisson"]


    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans genre_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans genre_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_genr_crud:
        code, msg = erreur_gest_genr_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_genr_crud} ", "danger")
        flash(f"Erreur dans genre_update_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_genr_crud.args[0]} , "
              f"{erreur_gest_genr_crud}", "danger")
        flash(f"__KeyError dans genre_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("genres/boisson_update_wtf.html", form_update=form_update)



"""
    Auteur : OM 2021.04.08
    Définition d'une "route" /genre_delete

    Test : ex. cliquer sur le menu "genres" puis cliquer sur le bouton "DELETE" d'un "genre"

    Paramètres : sans

    But : Effacer(delete) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"

    Remarque :  Dans le champ "nom_boisson_delete_wtf" du formulaire "genres/boisson_delete_wtf.html",
                le contrôle de la saisie est désactivée. On doit simplement cliquer sur "DELETE"
"""


# ****************************************
# BOUTON SUPRIMMER !!!!!!!!!!!
# *****************************************







@obj_mon_application.route("/boisson_delete", methods=['GET', 'POST'])
def boisson_delete_wtf():
    data_films_attribue_genre_delete = None
    btn_submit_del = None
    # L'utilisateur vient de cliquer sur le bouton "DELETE". Récupère la valeur de "Id_boisson"
    Id_boisson_delete = request.values['Id_boisson_btn_delete_html']

    # Objet formulaire pour effacer le genre sélectionné.
    form_delete = FormWTFDeleteboisson()
    try:
        print(" on submit ", form_delete.validate_on_submit())
        if request.method == "POST" and form_delete.validate_on_submit():

            if form_delete.submit_btn_annuler.data:
                return redirect(url_for("boisson_afficher", order_by="ASC", Id_boisson_sel=0))

            if form_delete.submit_btn_conf_del.data:
                # Récupère les données afin d'afficher à nouveau
                # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                data_films_attribue_genre_delete = session['data_films_attribue_genre_delete']
                print("data_films_attribue_genre_delete ", data_films_attribue_genre_delete)

                flash(f"Effacer le genre de façon définitive de la BD !!!", "danger")
                # L'utilisateur vient de cliquer sur le bouton de confirmation pour effacer...
                # On affiche le bouton "Effacer genre" qui va irrémédiablement EFFACER le genre
                btn_submit_del = True

            if form_delete.submit_btn_del.data:
                valeur_delete_dictionnaire = {"value_Id_boisson": Id_boisson_delete}
                print("valeur_delete_dictionnaire ", valeur_delete_dictionnaire)

                str_sql_delete_films_genre = """DELETE FROM t_type_boisson WHERE fk_boisson = %(value_Id_boisson)s"""
                str_sql_delete_idgenre = """DELETE FROM t_boisson WHERE id_boisson = %(value_Id_boisson)s"""
                # Manière brutale d'effacer d'abord la "fk_genre", même si elle n'existe pas dans la "t_genre_film"
                # Ensuite on peut effacer le genre vu qu'il n'est plus "lié" (INNODB) dans la "t_genre_film"
                with MaBaseDeDonnee() as mconn_bd:
                    mconn_bd.mabd_execute(str_sql_delete_films_genre, valeur_delete_dictionnaire)
                    mconn_bd.mabd_execute(str_sql_delete_idgenre, valeur_delete_dictionnaire)

                flash(f"Genre définitivement effacé !!", "success")
                print(f"Genre définitivement effacé !!")

                # afficher les données
                return redirect(url_for('boisson_afficher', order_by="ASC", Id_boisson_sel=0))

        if request.method == "GET":
            valeur_select_dictionnaire = {"value_Id_boisson": Id_boisson_delete}
            print(Id_boisson_delete, type(Id_boisson_delete))

            # Requête qui affiche tous les films_genres qui ont le genre que l'utilisateur veut effacer
            str_sql_genres_films_delete = """SELECT Id_type_boisson, Marque, id_boisson, type FROM t_type_boisson 
                                            INNER JOIN t_type ON t_type_boisson.fk_type = t_type.id_type
                                            INNER JOIN t_boisson ON t_type_boisson.fk_boisson = t_boisson.id_boisson
                                            WHERE fk_boisson = %(value_Id_boisson)s"""

            mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()

            mybd_curseur.execute(str_sql_genres_films_delete, valeur_select_dictionnaire)
            data_films_attribue_genre_delete = mybd_curseur.fetchall()
            print("data_films_attribue_genre_delete...", data_films_attribue_genre_delete)

            # Nécessaire pour mémoriser les données afin d'afficher à nouveau
            # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
            session['data_films_attribue_genre_delete'] = data_films_attribue_genre_delete

            # Opération sur la BD pour récupérer "id_genre" et "intitule_genre" de la "t_genre"
            str_sql_id_genre = "SELECT id_boisson, Marque FROM t_boisson WHERE Id_boisson = %(value_Id_boisson)s"

            mybd_curseur.execute(str_sql_id_genre, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()",
            # vu qu'il n'y a qu'un seul champ "nom genre" pour l'action DELETE
            data_nom_genre = mybd_curseur.fetchone()
            print("data_nom_genre ", data_nom_genre, " type ", type(data_nom_genre), " genre ",
                  data_nom_genre["Marque"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "genre_delete_wtf.html"
            form_delete.marque_delete_wtf.data = data_nom_genre["Marque"]

            # Le bouton pour l'action "DELETE" dans le form. "genre_delete_wtf.html" est caché.
            btn_submit_del = False

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans genre_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans genre_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_genr_crud:
        code, msg = erreur_gest_genr_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_genr_crud} ", "danger")

        flash(f"Erreur dans genre_delete_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_genr_crud.args[0]} , "
              f"{erreur_gest_genr_crud}", "danger")

        flash(f"__KeyError dans genre_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("genres/boisson_delete_wtf.html",
                           form_delete=form_delete,
                           btn_submit_del=btn_submit_del,
                           data_films_associes=data_films_attribue_genre_delete)




