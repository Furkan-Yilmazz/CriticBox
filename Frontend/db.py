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
    return f"{pseudo.strip().lower()}@games-films.app"


def sign_up(pseudo, password, preference="Les deux"):
    try:
        client().auth.sign_up({
            "email": _email(pseudo),
            "password": password,
            "options": {"data": {"pseudo": pseudo, "preference": preference}},
        })
        return True, None
    except Exception as e:
        return False, str(e)


def sign_in(pseudo, password):
    try:
        client().auth.sign_in_with_password({"email": _email(pseudo), "password": password})
        return True, None
    except Exception as e:
        return False, "Pseudo ou mot de passe incorrect."
