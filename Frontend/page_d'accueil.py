"""
Auteur : Furkan YILMAZ
Version : 0.0
Date : 18/11/2026
"""

import tkinter as tk
from io import BytesIO
from urllib.request import Request, urlopen

from customtkinter import *
from PIL import Image, ImageTk

# -- Constantes
RED = "#EC0028"
RED_HOVER = "#C70022"
CARD_DARK = "#1E1E1E"
CARD_DARK_HOVER = "#2A2A2A"
CARD_BORDER = "#2F2F2F"
WHITE = "#FFFFFF"
GREY = "#9A9A9A"
BG_BLACK = (6, 6, 6)
BG_RED = (105, 0, 25)

FONT = "Inter"  # la police par défaut du système au cas ou d'absence

CARD_W, CARD_H, GAP = 262, 112, 14
BTN_W, BTN_H = CARD_W * 2 + GAP, 42

# Icône de profil mise en place par un lien
AVATAR_URL = "https://img.icons8.com/ios-filled/100/9AA0A6/user-male-circle.png"
AVATAR_SIZE = 34


def load_avatar_from_url(url, size):
    """Télécharge l'image et la renvoie en PhotoImage."""
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=5) as response:
            data = response.read()
        img = Image.open(BytesIO(data)).convert("RGBA")
        img = img.resize((size, size), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as error:
        print("Icône non chargée, utilisation de l'icône dessinée :", error)
        return None


# -- Actions
def on_games():
    print("→ Page JEUX")


def on_movies():
    print("→ Page FILMS")


def on_login():
    print("→ Page CONNEXION")


def on_signup():
    print("→ Page CRÉATION DE COMPTE")


def on_profile():
    print("→ Profil utilisateur")


# --Dégradé
def make_gradient(width, height):
    """Dégradé diagonal"""
    small_w, small_h = 64, 40
    img = Image.new("RGB", (small_w, small_h))
    px = img.load()
    for y in range(small_h):
        for x in range(small_w):
            t = (x / small_w) * 0.45 + (y / small_h) * 1.15
            t = min(1.0, max(0.0, t * 1.1))
            px[x, y] = tuple(
                int(BG_RED[i] + (BG_BLACK[i] - BG_RED[i]) * t) for i in range(3)
            )
    return img.resize((max(width, 1), max(height, 1)), Image.BICUBIC)


# -- Carte cliquable
def make_card(title, subtitle, fg, hover, border, command):
    card = CTkFrame(
        app, width=CARD_W, height=CARD_H, corner_radius=8,
        fg_color=fg, border_width=1, border_color=border,
    )
    card.pack_propagate(False)

    lbl_title = CTkLabel(
        card, text=title, text_color=WHITE, anchor="w",
        font=CTkFont(family=FONT, size=22, weight="bold"),
    )
    lbl_title.pack(anchor="w", padx=18, pady=(26, 0))

    lbl_sub = CTkLabel(
        card, text=subtitle, text_color="#F0F0F0", anchor="w",
        font=CTkFont(family=FONT, size=11),
    )
    lbl_sub.pack(anchor="w", padx=18, pady=(2, 0))

    def enter(_):
        card.configure(fg_color=hover, cursor="hand2")

    def leave(_):
        card.configure(fg_color=fg)

    for widget in (card, lbl_title, lbl_sub):
        widget.bind("<Button-1>", lambda e: command())
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    return card


# -- Placement
def layout(event=None):
    """Replace tous les éléments quand la fenêtre change de taille."""
    global bg_photo

    w, h = canvas.winfo_width(), canvas.winfo_height()
    if w < 2 or h < 2:
        return

    # Fond dégradé
    bg_photo = ImageTk.PhotoImage(make_gradient(w, h))
    canvas.itemconfigure(bg_item, image=bg_photo)

    # Avatar en haut à droite
    r = AVATAR_SIZE // 2
    ax, ay = w - 36 - r, 38
    if avatar_photo is not None:
        canvas.coords(avatar_item, ax, ay)
    else:
        canvas.coords(avatar_bg, ax - r, ay - r, ax + r, ay + r)
        canvas.coords(avatar_head, ax - 5, ay - 9, ax + 5, ay + 1)
        canvas.coords(avatar_body, ax - 9, ay + 3, ax + 9, ay + 20)

    # Bloc central
    cx = w // 2
    y_title = int(h * 0.34)
    y_sub = y_title + 58
    y_cards = y_sub + 28
    y_btn = y_cards + CARD_H + 16
    y_text = y_btn + BTN_H + 22

    canvas.coords(title, cx, y_title)
    canvas.coords(subtitle, cx, y_sub)

    x0 = cx - (CARD_W * 2 + GAP) // 2
    canvas.coords(win_games, x0, y_cards)
    canvas.coords(win_movies, x0 + CARD_W + GAP, y_cards)
    canvas.coords(win_login, x0, y_btn)

    # "Pas encore de compte ? Créer un compte" centré
    canvas.coords(no_account, cx, y_text)
    canvas.coords(signup, cx, y_text)
    b1 = canvas.bbox(no_account)
    b2 = canvas.bbox(signup)
    w1, w2 = b1[2] - b1[0], b2[2] - b2[0]
    start = cx - (w1 + w2) // 2
    canvas.coords(no_account, start + w1, y_text)
    canvas.coords(signup, start + w1, y_text)

    canvas.tag_lower(bg_item)


# == Programme
set_appearance_mode("dark")

app = CTk()
app.title("CriticBox")
app.geometry("1000x640")
app.minsize(820, 560)

canvas = tk.Canvas(app, highlightthickness=0, bd=0, bg="#050505")
canvas.pack(fill="both", expand=True)

bg_photo = None
bg_item = canvas.create_image(0, 0, anchor="nw")

# Logo en haut à gauche
canvas.create_text(
    36, 38, text="CriticBox", anchor="w", fill=RED, font=(FONT, 17, "bold")
)

# Avatar en haut à droite : icône téléchargée depuis AVATAR_URL
# (si le téléchargement échoue, on dessine un petit avatar à la place)
avatar_photo = load_avatar_from_url(AVATAR_URL, AVATAR_SIZE)

if avatar_photo is not None:
    avatar_item = canvas.create_image(0, 0, image=avatar_photo, anchor="center")
    avatar_items = [avatar_item]
else:
    avatar_bg = canvas.create_oval(0, 0, 0, 0, fill="#3A3D40", outline="")
    avatar_head = canvas.create_oval(0, 0, 0, 0, fill="#9AA0A6", outline="")
    avatar_body = canvas.create_oval(0, 0, 0, 0, fill="#9AA0A6", outline="")
    avatar_items = [avatar_bg, avatar_head, avatar_body]

for item in avatar_items:
    canvas.tag_bind(item, "<Button-1>", lambda e: on_profile())
    canvas.tag_bind(item, "<Enter>", lambda e: canvas.config(cursor="hand2"))
    canvas.tag_bind(item, "<Leave>", lambda e: canvas.config(cursor=""))

# Titre + sous-titre
title = canvas.create_text(0, 0, text="CriticBox", fill=WHITE, font=(FONT, 50, "bold"))
subtitle = canvas.create_text(
    0, 0, text="Évaluez les jeux et les films", fill=WHITE, font=(FONT, 13)
)

# Cartes JEUX / FILMS
card_games = make_card(
    "JEUX", "Des jeux classés par catégorie",
    fg=RED, hover=RED_HOVER, border=RED, command=on_games,
)
card_movies = make_card(
    "FILMS", "Des films classés par genre",
    fg=CARD_DARK, hover=CARD_DARK_HOVER, border=CARD_BORDER, command=on_movies,
)
win_games = canvas.create_window(0, 0, window=card_games, anchor="nw")
win_movies = canvas.create_window(0, 0, window=card_movies, anchor="nw")

# Bouton SE CONNECTER
btn_login = CTkButton(
    app, text="SE CONNECTER", width=BTN_W, height=BTN_H, corner_radius=6,
    fg_color="#0A0A0A", hover_color="#1A1A1A",
    border_width=1, border_color="#BEBEBE", text_color=WHITE,
    font=CTkFont(family=FONT, size=12, weight="bold"),
    command=on_login,
)
win_login = canvas.create_window(0, 0, window=btn_login, anchor="nw")

# "Pas encore de compte ? Créer un compte"
no_account = canvas.create_text(
    0, 0, text="Pas encore de compte ? ", fill=GREY, font=(FONT, 10), anchor="e"
)
signup = canvas.create_text(
    0, 0, text="Créer un compte", fill=RED, font=(FONT, 10, "bold"), anchor="w"
)
canvas.tag_bind(signup, "<Button-1>", lambda e: on_signup())
canvas.tag_bind(signup, "<Enter>", lambda e: canvas.config(cursor="hand2"))
canvas.tag_bind(signup, "<Leave>", lambda e: canvas.config(cursor=""))

canvas.bind("<Configure>", layout)

app.mainloop()