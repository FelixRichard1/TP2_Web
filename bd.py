"""
Connexion à la BD
"""

import types
import contextlib
import mysql.connector


@contextlib.contextmanager
def creer_connexion():
    """Pour créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user="root",
        password="swmT97jn&@S7Ek",
        host="127.0.0.1",
        database="toutou",
        raise_on_warnings=True
    )

    # Pour ajouter la méthode getCurseur() à l'objet connexion
    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    """Permet d'avoir les enregistrements sous forme de dictionnaires"""
    curseur = self.cursor(dictionary=True)
    try:
        yield curseur
    finally:
        curseur.close()

def get_compte(conn, id):
    """Retourne le compte associé a l'id"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT id, courriel, est_admin FROM compte WHERE id=%(id)s;",
            {
                "id": id
            }
        )
        return curseur.fetchone()


def get_id(conn, courriel, mdp):
    with conn.get_curseur() as curs:
        curs.execute(
            "SELECT id FROM compte WHERE courriel=%(courriel)s AND mdp=%(mdp)s;",
            {
                "courriel": courriel,
                "mdp": mdp
            }
        )
        return curs.fetchone()


def courriel_exists(conn, courriel):
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT id FROM compte WHERE courriel=%(courriel)s;",
            {
                "courriel": courriel
            }
        )
        potentiel = curseur.fetchone()
        if not potentiel:
            return False
        return True


def get_mdp(conn, identifiant):
    """retourne le mot de passe haché de la base de données"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT mdp FROM compte WHERE id=%(id)s;", {
            "id": identifiant
        })
        return curseur.fetchone()


def creer_compte(conn, courriel, mdp):
    with conn.get_curseur() as curs:
        curs.execute("INSERT INTO `compte`(courriel,mdp,est_admin) VALUES (%(courriel)s,%(mdp)s,0)", {
            "courriel": courriel,
            "mdp": mdp
        })

