from flask import Flask, redirect, render_template, request
from bd import creer_connexion

app = Flask(__name__)

def lister_routes():
    """Liste les routes pour le menu"""
    return [
        {
            'route' : '/',
            'nom' : 'Accueil'
        },
        {
            'route' : '/ajouter',
            'nom' : 'Ajouter un animal'
        },
        {
            'route' : '/liste',
            'nom' : 'Liste des animaux'
        },
    ]
def obtenir_details_animal(id):
    """Retourne les informations d'un animal passé en paramètre"""
    if not id:
        return "Animal introuvable", 404

    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                SELECT animal.id, animal.nom, espece.id AS espece_id, espece.nom AS espece_nom, 
                       animal.date_de_naissance, animal.date_ajout, animal.description, animal.image
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
                SELECT animal.id, animal.nom, espece.nom AS espece_nom, animal.date_ajout, animal.image
                FROM animal
                JOIN espece ON animal.espece = espece.id
                ORDER BY animal.date_ajout DESC
                LIMIT 5
            """)
            return curseur.fetchall()

def obtenir_animaux():
    """Retourne tous les animaux"""
    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                SELECT animal.id, animal.nom, espece.nom AS espece_nom, animal.date_de_naissance, animal.image
                FROM animal
                JOIN espece ON animal.espece = espece.id
            """)
            return curseur.fetchall()
        

@app.route("/")
def acceuil():
    """Affiche la page d'acceuil """
    animaux_recents = obtenir_5_derniers_animaux()
    return render_template(
        "acceuil.jinja", 
        titre="Acceuil",
        route_active="/",
        routes = lister_routes(),
        animaux_recents=animaux_recents
    )

@app.route("/liste")
def liste():
    """Affiche la page de la liste des animaux """
    return render_template(
        "liste.jinja",
        titre="Liste", 
        route_active="/liste",
        routes = lister_routes(),
        animaux=obtenir_animaux()
    )

@app.route("/details")
def details():
    """Affiche la page des détails d'un animal """
    animal_id = request.args.get('id')
    animal_details = obtenir_details_animal(animal_id)
    
    return render_template(
        "details.jinja",
        titre="Details de l'animal",
        route_active="/details",
        routes=lister_routes(),
        animal=animal_details
    )

@app.route("/modifier")
def modifier():
    """Affiche la page de modification d'un animal """
    id = request.args.get('id')
    animal_details = obtenir_details_animal(id)
    espece = obtenir_espece()
    errors = {}
    
    return render_template(
        "modifier.jinja",
        titre="Modification d'un animal",
        route_active="/modifier",
        routes=lister_routes(),
        animal=animal_details,
        espece=espece,
        errors=errors
    )

@app.route("/ajouter", methods=['GET', 'POST'])
def ajouter():
    """Affiche la page d'ajout d'un animal et gère l'ajout via POST"""
    if request.method == 'POST':
        errors = {}
        nom = request.form['nom'].strip()
        date_de_naissance = request.form['date_de_naissance']
        espece = request.form['espece']
        description = request.form.get('description', '').strip()

        if not (1 <= len(nom) <= 50) or not nom.replace(" ", "").isalpha():
            errors['nom'] = "Nom invalide: doit contenir entre 1 et 50 caractères alphabétiques."

        if not description or not (5 <= len(description) <= 2000):
            errors['description'] = "Description invalide: doit contenir entre 5 et 2000 caractères."

        if errors:
            return render_template(
                'ajouter.jinja',
                titre="Ajouter un nouvel animal",
                route_active="/ajouter",
                routes=lister_routes(),
                espece=obtenir_espece(),
                errors=errors
            )

        with creer_connexion() as connexion:
            with connexion.get_curseur() as curseur:
                curseur.execute("""
                    INSERT INTO animal (nom, date_de_naissance, espece, description, date_ajout) 
                    VALUES (%s, %s, %s, %s, CURDATE())
                """, (nom, date_de_naissance, espece, description))
                new_id = curseur.lastrowid

        return redirect('/details?id=' + str(new_id))

    return render_template(
        "ajouter.jinja",
        titre="Ajouter", 
        route_active="/ajouter",
        routes=lister_routes(),
        espece=obtenir_espece(),
        errors={}
    )


@app.route("/sauvegarder", methods=['POST'])
def sauvegarder_animal():
    """Met à jour les informations d'un animal existant"""
    errors = {}
    id = request.args.get('id')
    
    if not id:
        return redirect('/ajouter')

    nom = request.form['nom'].strip()
    date_de_naissance = request.form['date_de_naissance']
    espece = request.form['espece']
    description = request.form.get('description', '').strip()

    if not (1 <= len(nom) <= 50) or not nom.replace(" ", "").isalpha():
        errors['nom'] = "Nom invalide: doit contenir entre 1 et 50 caractères alphabétiques."
    
    if not description or not (5 <= len(description) <= 2000):
        errors['description'] = "Description invalide: doit contenir entre 5 et 2000 caractères."

    if errors:
        especes = obtenir_espece()
        animal_details = obtenir_details_animal(id)
        return render_template(
            'modifier.jinja',
            titre="Modifier un animal",
            route_active="/modifier",
            routes=lister_routes(),
            animal=animal_details,
            espece=especes,
            errors=errors,
            nom=nom,
            date_de_naissance=date_de_naissance,
            description=description
        )
    
    with creer_connexion() as connexion:
        with connexion.get_curseur() as curseur:
            curseur.execute("""
                UPDATE animal 
                SET nom = %s, date_de_naissance = %s, espece = %s, description = %s
                WHERE id = %s
            """, (nom, date_de_naissance, espece, description, id))

    return redirect('/details?id=' + str(id))


if __name__ == '__main__':
    app.run(debug=True)