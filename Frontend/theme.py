"""Couleurs, tailles et petites fonctions partagées par toute l'appli."""

from io import BytesIO
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageOps

RED = "#eb0028"
BG = "#0f0f0f"
PANEL = "#1a1a1a"
GREY = "#2a2a2a"

COVER_SIZE = (130, 190)    # affiche sur la carte
POSTER_SIZE = (190, 280)   # affiche dans la fiche détaillée

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def date_fr(iso):
    """'2011-11-18' -> '18 novembre 2011' ('—' si la date est absente)."""
    try:
        annee, mois, jour = str(iso).split("-")
        return f"{int(jour)} {MOIS[int(mois) - 1]} {annee}"
    except Exception:
        return "—"


def rounded(img, radius=8):
    """Applique des coins arrondis à une image."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, img.width - 1, img.height - 1], radius, fill=255
    )
    img.putalpha(mask)
    return img


def placeholder(size=COVER_SIZE):
    """Image grise affichée en attendant l'affiche (ou si elle ne charge pas)."""
    return rounded(Image.new("RGB", size, "#262626"))


def download_image(url, size=COVER_SIZE):
    """Télécharge une affiche et la recadre à la taille voulue. None si échec."""
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=8) as response:
            data = response.read()
        img = Image.open(BytesIO(data)).convert("RGB")
        return rounded(ImageOps.fit(img, size, Image.LANCZOS))
    except Exception as error:
        print("Affiche non chargée :", url, "-", error)
        return None
