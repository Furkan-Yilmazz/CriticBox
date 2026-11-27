"""Page des jeux : seulement la configuration, tout le reste est dans catalogue.py."""

import db
from catalogue import Page
from theme import date_fr


def game_infos(g):
    """Ligne sous le titre, sur la carte."""
    return (g.get("date_sortie") or "")[:4]


def game_fields(g):
    """Lignes d'informations de la fiche détaillée."""
    return [
        ("DÉVELOPPEUR", g.get("studio_dev")),
        ("ÉDITEUR", g.get("editeur")),
        ("DATE DE SORTIE", date_fr(g.get("date_sortie"))),
    ]


def game_platforms(g):
    return [p.strip() for p in (g.get("platform") or "").split(",") if p.strip()]


GAMES = {
    "kind": "jeu",
    "logo": "JEUX",
    "window_title": "Jeux",
    "heading": "Ma collection de jeux",
    "plural": "jeux",
    "search_hint": "Rechercher un jeu...",
    "loader": db.get_games,
    "id_key": "id_jeu",
    "title_key": "nom_jeu",
    "desc_key": "description",
    "infos": game_infos,
    "fields": game_fields,
    "tags": game_platforms,
    "tags_label": "PLATEFORMES",
    "later_text": "＋ À JOUER PLUS TARD",
    "later_in": "✓ DANS TA LISTE (RETIRER)",
    "later_label": "À JOUER PLUS TARD",
    "later_done": "Ajouté à ta liste À jouer plus tard.",
    "trailer_text": "VOIR LE GAMEPLAY",
    "trailer_query": "gameplay",
}


class GamesPage(Page):
    def __init__(self, master, on_switch):
        super().__init__(master, GAMES, on_switch)


if __name__ == "__main__":
    import main
    main.run("jeu")
