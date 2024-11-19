import os
from flask import Blueprint, Flask, flash, redirect, render_template, request, session
from bd import creer_connexion

bp_animaux = Blueprint('animaux', __name__)

DOSSIER_TELEVERSEMENT = os.path.join('static', 'images', 'ajouts')
EXTENSION_AUTORISE = {'png', 'jpg', 'jpeg'}
CHEMIN_IMAGE_PAR_DEFAUT = 'default.jpg'

def lister_routes():
    """Liste les routes pour le menu"""
    return [
        {
            'route' : '/animaux/',
            'nom' : 'Accueil'
        },
        {
            'route' : '/animaux/ajouter',
            'nom' : 'Ajouter un animal'
        },
        {
            'route' : '/animaux/liste',
            'nom' : 'Liste des animaux'
        },
    ]

def extension_autorise(nom_fichier):
    return '.' in nom_fichier and nom_fichier.rsplit('.', 1)[1].lower() in EXTENSION_AUTORISE

def generer_nom(nom, nom_fichier_base):
    extension = nom_fichier_base.rsplit('.')[1].lower()
    nom_fichier = f"{nom}.{extension}"
    compteur = 1

    while os.path.exists(os.path.join(DOSSIER_TELEVERSEMENT, nom_fichier)):
        nom_fichier = f"{nom}_{compteur}.{extension}"
        compteur += 1

    return nom_fichier


def obtenir_permission(animal_details):
    if not animal_details:
        return False
    return animal_details.get('')
    

def obtenir_details_animal(id):
    """Retourne les informations d'un animal passé en paramètre"""
    if not id:
        return "Animal introuvable", 404

    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                SELECT animal.id, animal.nom, espece.id AS espece_id, espece.nom AS espece_nom, 
                       animal.date_de_naissance, animal.date_ajout, animal.description, animal.image, animal.compte_proprietaire 
                FROM animal
                JOIN espece ON animal.espece = espece.id
                WHERE animal.id = %s
            """, (id,))
            animal_details = curseur.fetchone()
    
    if not animal_details:
        return "Détails de l'animal introuvable", 404
    else:
        return animal_details

def obtenir_espece():
    """Retourne toutes les espèces"""
    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                SELECT espece.id, espece.nom
                FROM espece
            """)
            return curseur.fetchall()

def obtenir_5_derniers_animaux():
    """Retourne les 5 derniers animaux ajoutés"""
    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                SELECT animal.id, animal.nom, espece.nom AS espece_nom, animal.date_ajout, animal.image,  animal.est_adopte
                FROM animal
                JOIN espece ON animal.espece = espece.id
                WHERE animal.est_adopte=0
                ORDER BY animal.date_ajout DESC
                LIMIT 5
            """)
            return curseur.fetchall()

def obtenir_animaux():
    """Retourne tous les animaux"""
    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                SELECT animal.id, animal.nom, espece.nom AS espece_nom, animal.date_de_naissance, animal.image,  animal.est_adopte
                FROM animal
                JOIN espece ON animal.espece = espece.id
                WHERE animal.est_adopte=0
            """)
            return curseur.fetchall()

@bp_animaux.route("/")
def acceuil():
    """Affiche la page d'acceuil """
    animaux_recents = obtenir_5_derniers_animaux()
    return render_template(
        "animaux/acceuil.jinja", 
        titre="Acceuil",
        route_active="/",
        routes = lister_routes(),
        animaux_recents=animaux_recents
    )
    

@bp_animaux.route("/liste")
def liste():
    """Affiche la page de la liste des animaux avec une fonctionnalité de recherche"""
    search_query = request.args.get('search', '').strip()

    if search_query:
        with creer_connexion() as connexion:
            with connexion.get_curseur() as curseur:
                curseur.execute("""
                    SELECT animal.id, animal.nom, espece.nom AS espece_nom, animal.image, animal.est_adopte
                    FROM animal
                    JOIN espece ON animal.espece = espece.id
                    WHERE animal.est_adopte=0 AND animal.nom LIKE %s OR animal.description LIKE %s
                """, (f"%{search_query}%", f"%{search_query}%"))
                animaux = curseur.fetchall()
    else:
        animaux = obtenir_animaux()

    return render_template(
        "animaux/liste.jinja",
        titre="Liste",
        route_active="/liste",
        routes=lister_routes(),
        animaux=animaux
    )


@bp_animaux.route("/details")
def details():
    """Affiche la page des détails d'un animal """
    animal_id = request.args.get('id')
    animal_details = obtenir_details_animal(animal_id)
    est_proprietaire = session and bool(animal_details.get("compte_proprietaire") == session["compte"].get("id"))

    return render_template(
        "animaux/details.jinja",
        titre="Details de l'animal",
        route_active="/details",
        routes = lister_routes(),
        animal = animal_details,
        proprietaire = est_proprietaire
    )

@bp_animaux.route("/modifier")
def modifier():
    """Affiche la page de modification d'un animal """
    id = request.args.get('id')
    animal_details = obtenir_details_animal(id)
    espece = obtenir_espece()
    errors = {}

    est_proprietaire = session and bool(animal_details.get("compte_proprietaire") == session["compte"].get("id"))
        
    return render_template(
        "animaux/modifier.jinja",
        titre="Modification d'un animal",
        route_active = "/modifier",
        routes = lister_routes(),
        animal = animal_details,
        espece = espece,
        errors = errors,
        proprietaire = est_proprietaire
    )

@bp_animaux.route("/ajouter", methods=['GET', 'POST'])
def ajouter():
    """Affiche la page d'ajout d'un animal et gère l'ajout via POST"""
    if request.method == 'POST':
        errors = {}
        nom = request.form['nom'].strip()
        date_de_naissance = request.form['date_de_naissance']
        espece = request.form['espece']
        description = request.form.get('description', '').strip()
        image = request.files.get('image')

        if not (1 <= len(nom) <= 50) or not nom.replace(" ", "").isalpha():
            errors['nom'] = "Nom invalide: doit contenir entre 1 et 50 caractères alphabétiques."

        if not description or not (5 <= len(description) <= 2000):
            errors['description'] = "Description invalide: doit contenir entre 5 et 2000 caractères."

        if image and not extension_autorise(image.filename):
            errors['image'] = "Format d'image non pris en charge. Formats autorisés: png, jpg, jpeg."

        if errors:
            return render_template(
                'animaux/ajouter.jinja',
                titre="Ajouter un nouvel animal",
                route_active="/ajouter",
                routes=lister_routes(),
                espece=obtenir_espece(),
                errors=errors
            )

        if image and extension_autorise(image.filename):
            os.makedirs(DOSSIER_TELEVERSEMENT, exist_ok=True)
            image_filename = generer_nom(nom, image.filename)
            image_path = os.path.join(DOSSIER_TELEVERSEMENT, image_filename)
            image.save(image_path)
            chemin_image_bd = os.path.join('images', 'ajouts', image_filename)
        else:
            chemin_image_bd = CHEMIN_IMAGE_PAR_DEFAUT

        with creer_connexion() as connexion:
            with connexion.get_curseur() as curseur:
                curseur.execute("""
                    INSERT INTO animal (nom, date_de_naissance, espece, description, image, compte_proprietaire, date_ajout) 
                    VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
                """, (nom, date_de_naissance, espece, description, chemin_image_bd, session["compte"].get("id")))
                new_id = curseur.lastrowid

        flash("Animal ajouté avec succès!", "success")
        return redirect('/animaux/details?id=' + str(new_id))

    return render_template(
        "animaux/ajouter.jinja",
        titre="Ajouter",
        route_active="/ajouter",
        routes=lister_routes(),
        espece=obtenir_espece(),
        errors={}
    )

@bp_animaux.route("/adopter", methods=['POST'])
def adopter():
    id = request.form.get('id')

    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                UPDATE animal
                SET est_adopte=1
                WHERE id = %s
            """, (id,))
    if curseur.rowcount == 0:
        flash("Animal introuvable ou déjà adopté.", "warning")
    else:
        flash("Animal adopté avec succès.", "success")
    return redirect('/animaux/liste') 

@bp_animaux.route("/supprimer", methods=['POST'])
def supprimer():
    id = request.form.get('id')

    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                DELETE FROM animal
                WHERE id = %s
            """, (id,))
    if curseur.rowcount == 0:
        flash("Animal introuvable ou déjà supprimé.", "warning")
    else:
        flash("Animal supprimé avec succès.", "success")
    return redirect('/animaux/liste') 

@bp_animaux.route("/sauvegarder", methods=['POST'])
def sauvegarder():
    """Met à jour les informations d'un animal existant"""
    errors = {}
    id = request.args.get('id')
    
    if not id:
        return redirect('/animaux/ajouter')

    nom = request.form['nom'].strip()
    date_de_naissance = request.form['date_de_naissance']
    espece = request.form['espece']
    description = request.form.get('description', '').strip()
    image = request.files.get('image')

    if not (1 <= len(nom) <= 50) or not nom.replace(" ", "").isalpha():
        errors['nom'] = "Nom invalide: doit contenir entre 1 et 50 caractères alphabétiques."
    
    if not description or not (5 <= len(description) <= 2000):
        errors['description'] = "Description invalide: doit contenir entre 5 et 2000 caractères."

    if image and not extension_autorise(image.filename):
        errors['image'] = "Format d'image non pris en charge. Formats autorisés: png, jpg, jpeg."

    if errors:
        especes = obtenir_espece()
        animal_details = obtenir_details_animal(id)
        est_proprietaire = session and bool(animal_details.get("compte_proprietaire") == session["compte"].get("id"))

        return render_template(
            'animaux/modifier.jinja',
            titre="Modifier un animal",
            route_active="/modifier",
            routes=lister_routes(),
            animal=animal_details,
            especes=especes,
            errors=errors,
            proprietaire=est_proprietaire,
            nom=animal_details.get("nom"),
            date_de_naissance=animal_details.get("date_de_naissance"),
            description=animal_details.get("description"),

        )
    
    if image and extension_autorise(image.filename):
        os.makedirs(DOSSIER_TELEVERSEMENT, exist_ok=True)
        image_filename = generer_nom(nom, image.filename)
        image_path = os.path.join(DOSSIER_TELEVERSEMENT, image_filename)
        image.save(image_path)
        chemin_image_bd = os.path.join('images', 'ajouts', image_filename)
    else:
        chemin_image_bd = CHEMIN_IMAGE_PAR_DEFAUT

    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                UPDATE animal 
                SET nom = %s, date_de_naissance = %s, espece = %s, description = %s, image = %s
                WHERE id = %s
            """, (nom, date_de_naissance, espece, description, chemin_image_bd, id))
    return redirect('/animaux/details?id=' + str(id))