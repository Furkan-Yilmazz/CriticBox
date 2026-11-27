"""
Accès aux données Supabase pour l'application Games & Films.

Prérequis :
    pip install supabase python-dotenv.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

# Lit le fichier db.env (ou .env) situé à côté de db.py
for _nom in ("db.env", ".env"):
    load_dotenv(Path(__file__).with_name(_nom))

_client = None


def client():
    global _client
    if _client is None:
        url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL / SUPABASE_KEY manquants dans le fichier .env")
        _client = create_client(url, key)
    return _client


def get_films():
    try:
        return client().table("film").select("*").order("titre").execute().data
    except Exception as e:
        print("Erreur Supabase (film) :", e)
        return []


def get_games():
    try:
        return client().table("jeu_video").select("*").order("nom_jeu").execute().data
    except Exception as e:
        print("Erreur Supabase (jeu_video) :", e)
        return []

def _email(pseudo):
    return f"{pseudo.strip().lower()}@gmail.com"

def sign_up(pseudo, password, preference="Les deux"):
    try:
        client().auth.sign_up({
            "email": _email(pseudo),
            "password": password,
            "options": {"data": {"pseudo": pseudo, "preference": preference}},
        })
        return True, None
    except Exception as e:
        print("Erreur inscription :", e)
        return False, str(e)


T_USERS = "utilisateurs"
T_FAV = "mettre"
T_NOTE = {"film": "critiquer_film", "jeu": "critiquer_jeu"}
T_LATER = "a_voir_plus_tard"
COL = {"film": "id_film", "jeu": "id_jeu"}

_user_id = None


def current_user_id():
    return _user_id


def sign_in(pseudo, password):
    global _user_id
    try:
        client().auth.sign_in_with_password({"email": _email(pseudo), "password": password})
        pseudo = pseudo.strip()
        rows = client().table(T_USERS).select("id_utilisateur").eq("pseudo", pseudo).execute().data
        if not rows:
            rows = client().table(T_USERS).insert(
                {"pseudo": pseudo, "mot_de_passe": "géré par Supabase Auth"}
            ).execute().data
        _user_id = rows[0]["id_utilisateur"]
        return True, None
    except Exception as e:
        print("Erreur connexion :", e)
        return False, "Pseudo ou mot de passe incorrect."

def get_favorites(kind):
    col = COL[kind]
    if _user_id is None:      # pas connecté : aucun favori à chercher
        return set()
    try:
        rows = (client().table(T_FAV).select(col)
                .eq("id_utilisateur", _user_id).execute().data)
        return {r[col] for r in rows if r.get(col) is not None}
    except Exception as e:
        print("Erreur get_favorites :", e)
        return set()


def toggle_favorite(kind, item_id):
    """Ajoute ou retire un favori."""
    col = COL[kind]
    try:
        q = client().table(T_FAV).select("id_favori").eq("id_utilisateur", _user_id).eq(col, item_id)
        existing = q.execute().data
        if existing:
            client().table(T_FAV).delete().eq("id_favori", existing[0]["id_favori"]).execute()
            return False
        client().table(T_FAV).insert(
            {"id_utilisateur": _user_id, col: item_id, "favoris": True}
        ).execute()
        return True
    except Exception as e:
        print("Erreur toggle_favorite :", e)
        return None

def save_rating(kind, item_id, note, commentaire=None):
    col = COL[kind]
    try:
        client().table(T_NOTE[kind]).upsert(
            {"id_utilisateur": _user_id, col: item_id, "note": note, "commentaire": commentaire},
            on_conflict=f"id_utilisateur,{col}",
        ).execute()
        return True
    except Exception as e:
        print("Erreur save_rating :", e)
        return False


def get_rating(kind, item_id):
    col = COL[kind]
    try:
        rows = (client().table(T_NOTE[kind]).select("note")
                .eq("id_utilisateur", _user_id).eq(col, item_id).execute().data)
        return rows[0]["note"] if rows else 0
    except Exception as e:
        print("Erreur get_rating :", e)
        return 0

def add_watchlist(kind, item_id):
    col = COL[kind]
    try:
        exists = (client().table(T_LATER).select(col)
                  .eq("id_utilisateur", _user_id).eq(col, item_id).execute().data)
        if not exists:
            client().table(T_LATER).insert({"id_utilisateur": _user_id, col: item_id}).execute()
        return True
    except Exception as e:
        print("Erreur add_watchlist :", e)
        return False
def get_watchlist(kind):
    col = COL[kind]
    if _user_id is None:
        return set()
    try:
        rows = (client().table(T_LATER).select(col)
                .eq("id_utilisateur", _user_id).execute().data)
        return {r[col] for r in rows if r.get(col) is not None}
    except Exception as e:
        print("Erreur get_watchlist :", e)
        return set()


def toggle_watchlist(kind, item_id):
    col = COL[kind]
    try:
        q = (client().table(T_LATER).select(col)
             .eq("id_utilisateur", _user_id).eq(col, item_id).execute().data)
        if q:
            (client().table(T_LATER).delete()
             .eq("id_utilisateur", _user_id).eq(col, item_id).execute())
            return False
        client().table(T_LATER).insert({"id_utilisateur": _user_id, col: item_id}).execute()
        return True
    except Exception as e:
        print("Erreur toggle_watchlist :", e)
        return None