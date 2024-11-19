import hashlib
import re
from flask import Blueprint, flash, get_flashed_messages, redirect, render_template, request, session
import bd

bp_comptes = Blueprint('comptes', __name__)

regex_html = re.compile(r'<(.*)>.*?|<(.*) />')
regex_courriel = re.compile(r'^[A-Za-z0-9]([A-Za-z0-9._%+-]*[A-Za-z0-9])?@[A-Za-z0-9-]+\.[A-Za-z]{2,}$')
regex_mdp = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')

# Centralized error messages
messages_erreurs = {
    "mdp1Invalide": "Le mot de passe doit contenir au moins une lettre majuscule, une lettre minuscule et un chiffre.",
    "mdp1Html": "Les balises HTML sont interdites dans le mot de passe.",
    "courrielInvalide": "Veuillez entrer une adresse courriel valide.",
    "courrielHtml": "Les balises HTML sont interdites dans le courriel.",
    "courrielExistant": "Ce courriel est déjà utilisé.",
    "mdpDiff": "Les deux mots de passe doivent être identiques.",
    "mdpVide": "Le mot de passe ne peut pas être vide.",
    "mdp1Length": "Le mot de passe doit contenir au moins 8 caractères."
}

def lister_routes():
    """Liste les routes pour le menu"""
    return [
        {'route': '/animaux/', 'nom': 'Accueil'},
        {'route': '/animaux/ajouter', 'nom': 'Ajouter un animal'},
        {'route': '/animaux/liste', 'nom': 'Liste des animaux'}
    ]

def hacher_mot_de_passe(mdp):
    """Encrypte le mot de passe"""
    return hashlib.sha512(mdp.encode()).hexdigest()

def creer_session(id):
    with bd.creer_connexion() as conn:
        compte = bd.get_compte(conn, id)
        if not compte:
            return redirect("/authentification", code=303)
        else:
            session.permanent = True
            session["compte"] = compte
            flash("Connection réussie!", "success")

def obtenir_comptes():
    """Retourne tous les comptes"""
    with bd.creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                SELECT animal.id, animal.nom, espece.nom AS espece_nom, animal.date_de_naissance, animal.image
                FROM animal
                JOIN espece ON animal.espece = espece.id
            """)
            return curseur.fetchall()            

@bp_comptes.route("/liste")
def liste():
    """Affiche la page de la liste des comptes """
    return render_template(
        "comptes/liste.jinja",
        titre="Liste", 
        route_active="/liste",
        routes = lister_routes(),
        animaux = obtenir_comptes()
    )

@bp_comptes.route("/authentification", methods=["GET", "POST"])
def connection():
    """Permet de se connecter"""
    if request.method == "GET":
        return render_template(
            "comptes/authentification.jinja",
            routes=lister_routes(),
            creation=False,
            errors={},
            courriel=""
        )
    
    courriel = request.form.get("courriel", default="").strip()
    mdp1 = request.form.get("mdp", default="").strip()
    errors = {}

    if not courriel:
        errors["courrielInvalide"] = messages_erreurs["courrielInvalide"]
    elif not bool(re.match(regex_courriel, courriel)):
        errors["courrielInvalide"] = messages_erreurs["courrielInvalide"]
    if bool(re.match(regex_html, courriel)):
        errors["courrielHtml"] = messages_erreurs["courrielHtml"]

    if not mdp1:
        errors["mdpVide"] = messages_erreurs["mdpVide"]
    elif not bool(re.match(regex_mdp, mdp1)):
        errors["mdp1Invalide"] = messages_erreurs["mdp1Invalide"]
    if bool(re.match(regex_html, mdp1)):
        errors["mdp1Html"] = messages_erreurs["mdp1Html"]

    if errors:
        return render_template(
            "comptes/authentification.jinja",
            routes=lister_routes(),
            creation=False,
            errors=errors,
            courriel=courriel
        )

    mdp1 = hacher_mot_de_passe(mdp1)
    with bd.creer_connexion() as conn:
        id_compte = bd.get_id(conn, courriel, mdp1)
    creer_session(id_compte["id"])
    return redirect("/", code=303)

@bp_comptes.route("/creer", methods=["GET", "POST"])
def creer_compte():
    if request.method == "GET":
        return render_template(
            "comptes/authentification.jinja",
            routes=lister_routes(),
            creation=True,
            errors={},
            courriel=""
        )

    mdp1 = request.form.get("mdp", default="").strip()
    mdp2 = request.form.get("mdp2", default="").strip()
    courriel = request.form.get("courriel", default="").strip()
    errors = {}

    if not courriel:
        errors["courrielInvalide"] = messages_erreurs["courrielInvalide"]
    elif not bool(re.match(regex_courriel, courriel)):
        errors["courrielInvalide"] = messages_erreurs["courrielInvalide"]
    if bool(re.match(regex_html, courriel)):
        errors["courrielHtml"] = messages_erreurs["courrielHtml"]

    if not mdp1:
        errors["mdpVide"] = messages_erreurs["mdpVide"]
    elif mdp1 != mdp2:
        errors["mdpDiff"] = messages_erreurs["mdpDiff"]
    elif not bool(re.match(regex_mdp, mdp1)):
        errors["mdp1Invalide"] = messages_erreurs["mdp1Invalide"]
    if bool(re.match(regex_html, mdp1)):
        errors["mdp1Html"] = messages_erreurs["mdp1Html"]    

    with bd.creer_connexion() as conn:
        if bd.courriel_exists(conn, courriel):
            errors["courrielExistant"] = messages_erreurs["courrielExistant"]

    if errors:
        return render_template(
            "comptes/authentification.jinja",
            routes=lister_routes(),
            creation=True,
            errors=errors,
            courriel=courriel
        )

    mdp1 = hacher_mot_de_passe(mdp1)
    with bd.creer_connexion() as conn:
        bd.creer_compte(conn, courriel, mdp1)
    flash("Compte créé avec succès!", "success")
    return redirect("/", code=303)
    
@bp_comptes.route("/deconnecter")
def deconnection():
    session.clear()
    flash("Déconnection réussie!", "success")
    return redirect("/", code=303)
