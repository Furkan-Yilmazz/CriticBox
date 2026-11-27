"""Page des films : seulement la configuration, tout le reste est dans catalogue.py."""

import db
from catalogue import Page
from theme import date_fr


def film_infos(f):
    """Ligne sous le titre, sur la carte."""
    annee = (f.get("date_sortie") or "")[:4]
    duree = f.get("duree_min")
    return " · ".join(x for x in (annee, f"{duree} min" if duree else "") if x)


def film_fields(f):
    """Lignes d'informations de la fiche détaillée."""
    d = f.get("duree_min")
    return [
        ("RÉALISATEUR", f.get("realisateur")),
        ("DURÉE", f"{d // 60}h {d % 60:02d}" if d else None),
        ("DATE DE SORTIE", date_fr(f.get("date_sortie"))),
    ]


FILMS = {
    "kind": "film",
    "logo": "FILMS",
    "window_title": "Film",
    "heading": "Ma collection de films",
    "plural": "films",
    "search_hint": "Rechercher un film...",
    "loader": db.get_films,
    "id_key": "id_film",
    "title_key": "titre",
    "desc_key": "synopsis",
    "infos": film_infos,
    "fields": film_fields,
    "tags": lambda f: [],
    "tags_label": "",
    "later_text": "＋ À VOIR PLUS TARD",
    "later_in": "✓ DANS TA LISTE (RETIRER)",
    "later_label": "À VOIR PLUS TARD",
    "later_done": "Ajouté à ta liste À voir plus tard.",
    "trailer_text": "VOIR LA BANDE-ANNONCE",
    "trailer_query": "bande annonce",
}


class FilmsPage(Page):
    def __init__(self, master, on_switch):
        super().__init__(master, FILMS, on_switch)


if __name__ == "__main__":
    import main
    main.run("film")
