from customtkinter import *
from PIL import Image, ImageDraw

# ───────────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────────
set_appearance_mode("dark")

RED = "#eb0028"
BG = "#0f0f0f"
PANEL = "#1a1a1a"
GREY = "#2a2a2a"

# Liste des jeux : vide pour l'instant
# Format : (titre, note, plateformes, couleur du haut, couleur du bas)
GAMES = []


def make_gradient(size, top, bottom, radius=8):
    """Crée une image avec un dégradé vertical et des coins arrondis."""
    w, h = size
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    t = tuple(int(top[i:i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(bottom[i:i + 2], 16) for i in (1, 3, 5))
    for y in range(h):
        ratio = y / (h - 1)
        color = tuple(int(t[k] + (b[k] - t[k]) * ratio) for k in range(3))
        draw.line([(0, y), (w, y)], fill=color)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    img = img.convert("RGBA")
    img.putalpha(mask)
    return img


# ───────────────────────────────────────────────
# Sidebar
# ───────────────────────────────────────────────
class Sidebar(CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=200, fg_color="#121212", corner_radius=0)
        self.pack_propagate(False)

        self.logo_label = CTkLabel(self, text="GAMES", font=("Impact", 35), text_color=RED)
        self.logo_label.pack(pady=(30, 10))

        # Bascule JEUX / FILMS
        self.toggle = CTkFrame(self, fg_color=PANEL, corner_radius=8)
        self.toggle.pack(padx=14, pady=(5, 10), fill="x")
        self.toggle.grid_columnconfigure((0, 1), weight=1)
        self.btn_jeux = CTkButton(self.toggle, text="JEUX", height=26, corner_radius=8,
                                  fg_color=RED, hover_color="#c70022",
                                  font=("Arial", 10, "bold"))
        self.btn_jeux.grid(row=0, column=0, padx=3, pady=3, sticky="ew")
        self.btn_films = CTkButton(self.toggle, text="FILMS", height=26, corner_radius=8,
                                   fg_color="transparent", hover_color=GREY,
                                   text_color="#cccccc", font=("Arial", 10, "bold"))
        self.btn_films.grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        # Recherche
        self.search_entry = CTkEntry(self, placeholder_text="Rechercher un titre...",
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
# Carte de jeu
# ───────────────────────────────────────────────
class GameCard(CTkFrame):
    COVER_SIZE = (130, 190)

    def __init__(self, master, title, rating, platforms, color_top, color_bottom):
        super().__init__(master, width=150, fg_color=PANEL, corner_radius=8)
        self.title_text = title
        self.is_favorite = False

        image = CTkImage(make_gradient(self.COVER_SIZE, color_top, color_bottom),
                         size=self.COVER_SIZE)
        self.cover = CTkLabel(self, image=image, text=title, compound="center",
                              font=("Arial", 13, "bold"), text_color="white",
                              wraplength=100)
        self.cover.pack(padx=10, pady=(10, 8))

        self.heart_btn = CTkButton(self, text="♡", width=22, height=22, corner_radius=11,
                                   fg_color="#0f0f0f", hover_color=GREY,
                                   font=("Arial", 12))
        self.heart_btn.place(x=self.COVER_SIZE[0] - 14, y=18)

        self.name_label = CTkLabel(self, text=title, font=("Arial", 11, "bold"),
                                   text_color="white", wraplength=130)
        self.name_label.pack(pady=(0, 2))

        self.info_label = CTkLabel(self, text=f"★ {rating} · {platforms}",
                                   font=("Arial", 9), text_color="#9a9a9a")
        self.info_label.pack(pady=(0, 10))


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


        self.avatar = CTkButton(self.header, text="👤", width=36, height=36, corner_radius=18,
                                fg_color="#3a3a3a", hover_color="#4a4a4a")
        self.avatar.pack(side="right", anchor="n")

        self.subtitle_label = CTkLabel(self, text="Découvrez nos meilleurs titres de la catégorie Survie",
                                       font=("Arial", 11), text_color="#9a9a9a")
        self.subtitle_label.pack(anchor="w", padx=25, pady=(0, 12))

        # Filtres
        self.filters = CTkFrame(self, fg_color="transparent")
        self.filters.pack(anchor="w", padx=25, pady=(0, 15))
        for text in ("Plateforme ▾", "Note ▾", "Année ▾", "Trier : Populaires ▾"):
            CTkButton(self.filters, text=text, height=26, corner_radius=13,
                      fg_color=PANEL, hover_color=GREY, font=("Arial", 10),
                      width=len(text) * 7 + 20).pack(side="left", padx=(0, 8))

        # Grille de cartes
        self.grid_frame = CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(anchor="nw", padx=25)
        self.cards = []
        for game in GAMES:
            self.add_game(*game)

    def add_game(self, title, rating, platforms, color_top, color_bottom):
        """Ajoute une carte de jeu à la grille."""
        i = len(self.cards)
        card = GameCard(self.grid_frame, title, rating, platforms, color_top, color_bottom)
        card.grid(row=i // self.COLUMNS, column=i % self.COLUMNS, padx=(0, 12), pady=(0, 12))
        self.cards.append(card)


# ───────────────────────────────────────────────
# Fenêtre principale
# ───────────────────────────────────────────────
class GamesPage(CTk):
    def __init__(self):
        super().__init__()
        self.title("Games")
        self.geometry("1100x700")
        self.configure(fg_color=BG)

        self.sidebar = Sidebar(self)
        self.sidebar.pack(side="left", fill="y")

        self.content = MainContent(self)
        self.content.pack(side="left", fill="both", expand=True)


if __name__ == "__main__":
    app = GamesPage()
    app.mainloop()