from flask import Flask, redirect, render_template, request
from comptes import bp_comptes
from animaux import bp_animaux
from bd import creer_connexion

app = Flask(__name__)

app.register_blueprint(bp_comptes, url_prefix="/comptes")
app.register_blueprint(bp_animaux, url_prefix="/animaux")
app.secret_key = "e21f73185e51e634aa9ef799c70878d366a55b7fd626981f271b66b10ac65c84"

@app.route("/")
def index():
    """Afficher la page index"""
    return redirect('/animaux/')

if __name__ == '__main__':
    app.run(debug=True)