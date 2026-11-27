import queue
import threading
from io import BytesIO
from urllib.request import Request, urlopen

from customtkinter import *
from PIL import Image, ImageDraw, ImageOps

from db import get_films

# ───────────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────────
set_appearance_mode("dark")

RED = "#eb0028"
BG = "#0f0f0f"
PANEL = "#1a1a1a"
GREY = "#2a2a2a"

COVER_SIZE = (130, 190)


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


# ───────────────────────────────────────────────
# Sidebar
# ───────────────────────────────────────────────
class Sidebar(CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=200, fg_color="#121212", corner_radius=0)
        self.pack_propagate(False)

        self.logo_label = CTkLabel(self, text="FILMS", font=("Impact", 35), text_color=RED)
        self.logo_label.pack(pady=(30, 10))

        # Bascule FILMS / JEUX
        self.toggle = CTkFrame(self, fg_color=PANEL, corner_radius=8)
        self.toggle.pack(padx=14, pady=(5, 10), fill="x")
        self.toggle.grid_columnconfigure((0, 1), weight=1)

        self.btn_films = CTkButton(self.toggle, text="FILMS", height=26, corner_radius=8,
                                   fg_color=RED, hover_color="#c70022",
                                   font=("Arial", 10, "bold"))
        self.btn_films.grid(row=0, column=0, padx=3, pady=3, sticky="ew")

        self.btn_jeux = CTkButton(self.toggle, text="JEUX", height=26, corner_radius=8,
                                  fg_color="transparent", hover_color=GREY,
                                  text_color="#cccccc", font=("Arial", 10, "bold"))
        self.btn_jeux.grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        # Recherche
        self.search_entry = CTkEntry(self, placeholder_text="Rechercher un film...",
                                     height=30, corner_radius=6, fg_color=PANEL,
                                     border_width=0, font=("Arial", 10))
        self.search_entry.pack(padx=14, pady=5, fill="x")

        # Boutons
        self.btn_random = CTkButton(self, text="AU HASARD", height=32, corner_radius=6,
                                    fg_color=RED, hover_color="#c70022",
                                    font=("Arial", 11, "bold"))
        self.btn_random.pack(padx=14, pady=5, fill="x")

        self.btn_fav = CTkButton(self, text="♥  MES FAVORIS", height=32, corner_radius=6,
                                 fg_color=GREY, hover_color="#3a3a3a",
                                 font=("Arial", 11, "bold"))
        self.btn_fav.pack(padx=14, pady=5, fill="x")


# ───────────────────────────────────────────────
# Carte de film
# ───────────────────────────────────────────────
class FilmCard(CTkFrame):
    def __init__(self, master, film):
        """film : dictionnaire d'une ligne de la table Supabase `film`."""
        super().__init__(master, width=150, fg_color=PANEL, corner_radius=8)

        self.film = film
        self.is_favorite = False

        titre = film.get("titre", "")
        annee = (film.get("date_sortie") or "")[:4]
        duree = film.get("duree_min")
        infos = " · ".join(str(x) for x in (annee, f"{duree} min" if duree else "") if x)

        self.cover = CTkLabel(
            self, text=titre, compound="center",
            image=CTkImage(placeholder(), size=COVER_SIZE),
            font=("Arial", 13, "bold"), text_color="white", wraplength=100
        )
        self.cover.pack(padx=10, pady=(10, 8))

        self.heart_btn = CTkButton(self, text="♡", width=22, height=22, corner_radius=11,
                                   fg_color="#0f0f0f", hover_color=GREY, font=("Arial", 12))
        self.heart_btn.place(x=COVER_SIZE[0] - 14, y=18)

        self.name_label = CTkLabel(self, text=titre, font=("Arial", 11, "bold"),
                                   text_color="white", wraplength=130)
        self.name_label.pack(pady=(0, 2))

        self.info_label = CTkLabel(self, text=infos, font=("Arial", 9), text_color="#9a9a9a")
        self.info_label.pack(pady=(0, 10))

    def set_poster(self, pil_image):
        """Affiche la vraie affiche (appelé quand le téléchargement est fini)."""
        self.cover.configure(image=CTkImage(pil_image, size=COVER_SIZE), text="")


# ───────────────────────────────────────────────
# Zone principale
# ───────────────────────────────────────────────
class MainContent(CTkFrame):
    COLUMNS = 5

    def __init__(self, master):
        super().__init__(master, fg_color=BG, corner_radius=0)

        # En-tête
        self.header = CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=25, pady=(25, 0))

        self.title_label = CTkLabel(self.header, text="Ma collection de films",
                                    font=("Arial", 24, "bold"), text_color="white")
        self.title_label.pack(side="left")

        self.avatar = CTkButton(self.header, text="👤", width=36, height=36, corner_radius=18,
                                fg_color="#3a3a3a", hover_color="#4a4a4a")
        self.avatar.pack(side="right", anchor="n")

        self.subtitle_label = CTkLabel(self, text="Chargement des films...",
                                       font=("Arial", 11), text_color="#9a9a9a")
        self.subtitle_label.pack(anchor="w", padx=25, pady=(0, 12))

        # Grille de cartes
        self.grid_frame = CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(anchor="nw", padx=25)

        self.cards = []
        self.poster_queue = queue.Queue()
        self.after(100, self.load_films)

    def load_films(self):
        films = get_films()
        self.subtitle_label.configure(
            text=f"{len(films)} films dans votre collection" if films
            else "Aucun film trouvé (vérifie la connexion Supabase)"
        )
        for film in films:
            self.add_film(film)

        # Téléchargement des affiches en arrière-plan : l'interface ne se fige pas
        threading.Thread(target=self._download_posters, args=(films,), daemon=True).start()
        self.after(100, self._poll_posters)

    def add_film(self, film):
        """Ajoute une carte de film à la grille."""
        i = len(self.cards)
        card = FilmCard(self.grid_frame, film)
        card.grid(row=i // self.COLUMNS, column=i % self.COLUMNS, padx=(0, 12), pady=(0, 12))
        self.cards.append(card)

    def _download_posters(self, films):
        for index, film in enumerate(films):
            url = film.get("image_url")
            img = download_image(url) if url else None
            self.poster_queue.put((index, img))

    def _poll_posters(self):
        try:
            while True:
                index, img = self.poster_queue.get_nowait()
                if img is not None and index < len(self.cards):
                    self.cards[index].set_poster(img)
        except queue.Empty:
            pass
        self.after(150, self._poll_posters)


# ───────────────────────────────────────────────
# Fenêtre principale
# ───────────────────────────────────────────────
class FilmsPage(CTk):
    def __init__(self):
        super().__init__()

        self.title("Film")
        self.geometry("1100x700")
        self.configure(fg_color=BG)

        self.sidebar = Sidebar(self)
        self.sidebar.pack(side="left", fill="y")

        self.content = MainContent(self)
        self.content.pack(side="left", fill="both", expand=True)


if __name__ == "__main__":
    app = FilmsPage()
    app.mainloop()
