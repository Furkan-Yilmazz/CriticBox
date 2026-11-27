"""Page catalogue commune aux films et aux jeux."""

import queue
import random
import threading

from customtkinter import *

import db
from fiche import Fiche
from login import LoginDialog
from theme import BG, COVER_SIZE, GREY, PANEL, RED, download_image, placeholder

set_appearance_mode("dark")

# Sidebar

class Sidebar(CTkFrame):
    def __init__(self, master, cfg, on_search, on_home, on_random, on_favorites,
                 on_later, on_switch):
        super().__init__(master, width=200, fg_color="#121212", corner_radius=0)
        self.pack_propagate(False)

        CTkLabel(self, text=cfg["logo"], font=("Impact", 35),
                 text_color=RED).pack(pady=(30, 10))

        # Bascule FILMS / JEUX
        toggle = CTkFrame(self, fg_color=PANEL, corner_radius=8)
        toggle.pack(padx=14, pady=(5, 10), fill="x")
        toggle.grid_columnconfigure((0, 1), weight=1)
        for col, (kind, text) in enumerate((("film", "FILMS"), ("jeu", "JEUX"))):
            actif = kind == cfg["kind"]
            CTkButton(toggle, text=text, height=26, corner_radius=8,
                      fg_color=RED if actif else "transparent",
                      hover_color="#c70022" if actif else GREY,
                      text_color="white" if actif else "#cccccc",
                      font=("Arial", 10, "bold"),
                      command=lambda k=kind: on_switch(k)
                      ).grid(row=0, column=col, padx=3, pady=3, sticky="ew")

        # Recherche : le filtre se met à jour à chaque lettre tapée
        self.search_entry = CTkEntry(self, placeholder_text=cfg["search_hint"],
                                     height=30, corner_radius=6, fg_color=PANEL,
                                     border_width=0, font=("Arial", 10))
        self.search_entry.pack(padx=14, pady=5, fill="x")
        self.search_entry.bind("<KeyRelease>",
                               lambda e: on_search(self.search_entry.get()))

        self.btn_home = CTkButton(self, text="ACCUEIL", height=32, corner_radius=6,
                                  fg_color=RED, hover_color="#c70022",
                                  font=("Arial", 11, "bold"), command=on_home)
        self.btn_home.pack(padx=14, pady=5, fill="x")

        CTkButton(self, text="AU HASARD", height=32, corner_radius=6,
                  fg_color=GREY, hover_color="#3a3a3a",
                  font=("Arial", 11, "bold"), command=on_random
                  ).pack(padx=14, pady=5, fill="x")

        self.btn_fav = CTkButton(self, text="♥  MES FAVORIS", height=32, corner_radius=6,
                                 fg_color=GREY, hover_color="#3a3a3a",
                                 font=("Arial", 11, "bold"), command=on_favorites)
        self.btn_fav.pack(padx=14, pady=5, fill="x")

        self.btn_later = CTkButton(self, text=cfg["later_label"], height=32, corner_radius=6,
                                   fg_color=GREY, hover_color="#3a3a3a",
                                   font=("Arial", 11, "bold"), command=on_later)
        self.btn_later.pack(padx=14, pady=5, fill="x")

    def set_home_active(self, active):
        self.btn_home.configure(fg_color=RED if active else GREY,
                                hover_color="#c70022" if active else "#3a3a3a")

    def set_favorites_active(self, active):
        self.btn_fav.configure(fg_color=RED if active else GREY,
                               hover_color="#c70022" if active else "#3a3a3a")

    def set_later_active(self, active):
        self.btn_later.configure(fg_color=RED if active else GREY,
                                 hover_color="#c70022" if active else "#3a3a3a")

# Carte (film ou jeu)
class Card(CTkFrame):
    def __init__(self, master, cfg, item, is_favorite, on_open, on_heart):
        super().__init__(master, width=150, fg_color=PANEL, corner_radius=8)
        self.item = item
        self.item_id = item.get(cfg["id_key"])
        self.title = item.get(cfg["title_key"]) or ""
        self.is_favorite = is_favorite
        self.poster = None

        self.cover = CTkLabel(
            self, text=self.title, compound="center",
            image=CTkImage(placeholder(), size=COVER_SIZE),
            font=("Arial", 13, "bold"), text_color="white", wraplength=100
        )
        self.cover.pack(padx=10, pady=(10, 8))

        self.heart_btn = CTkButton(self, text="♡", width=22, height=22, corner_radius=11,
                                   fg_color="#0f0f0f", hover_color=GREY, font=("Arial", 12),
                                   command=lambda: on_heart(self))
        self.heart_btn.place(x=COVER_SIZE[0] - 14, y=18)
        self.set_favorite(is_favorite)

        self.name_label = CTkLabel(self, text=self.title, font=("Arial", 11, "bold"),
                                   text_color="white", wraplength=130)
        self.name_label.pack(pady=(0, 2))

        self.info_label = CTkLabel(self, text=cfg["infos"](item), font=("Arial", 9),
                                   text_color="#9a9a9a")
        self.info_label.pack(pady=(0, 10))

        # Un clic n'importe où sur la carte (sauf le cœur) ouvre la fiche
        for widget in (self, self.cover, self.name_label, self.info_label):
            widget.bind("<Button-1>", lambda e: on_open(self))

    def set_favorite(self, value):
        self.is_favorite = value
        self.heart_btn.configure(text="♥" if value else "♡",
                                 text_color=RED if value else "white")

    def set_poster(self, pil_image):
        self.poster = pil_image
        self.cover.configure(image=CTkImage(pil_image, size=COVER_SIZE), text="")

# Fenêtre principale
class Page(CTkFrame):
    COLUMNS = 5

    def __init__(self, master, cfg, on_switch):
        super().__init__(master, fg_color=BG, corner_radius=0)
        self.cfg = cfg
        self.fiche = None
        self.only_favs = False
        self.only_later = False
        self.later_ids = set()
        self.query = ""
        self.cards = []
        self.visible = []
        self.pending = 0
        self.poster_queue = queue.Queue()

        self.sidebar = Sidebar(self, cfg, self.on_search, self.go_home, self.random_item,
                               self.toggle_favorites_view, self.toggle_later_view, on_switch)
        self.sidebar.pack(side="left", fill="y")

        main = CTkFrame(self, fg_color=BG, corner_radius=0)
        main.pack(side="left", fill="both", expand=True)

        header = CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(25, 0))
        CTkLabel(header, text=cfg["heading"], font=("Arial", 24, "bold"),
                 text_color="white").pack(side="left")
        CTkButton(header, text="👤", width=36, height=36, corner_radius=18,
                  fg_color="#3a3a3a", hover_color="#4a4a4a",
                  command=self.show_profile).pack(side="right", anchor="n")

        self.subtitle = CTkLabel(main, text="Chargement...", font=("Arial", 11),
                                 text_color="#9a9a9a")
        self.subtitle.pack(anchor="w", padx=25, pady=(0, 12))

        self.grid_frame = CTkScrollableFrame(main, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=(25, 10), pady=(0, 10))

        self.after(100, self.load)

    # ───────── chargement ─────────
    def load(self):
        items = self.cfg["loader"]()
        favs = db.get_favorites(self.cfg["kind"])
        self.later_ids = db.get_watchlist(self.cfg["kind"])
        for item in items:
            card = Card(self.grid_frame, self.cfg, item,
                        item.get(self.cfg["id_key"]) in favs,
                        self.open_fiche, self.on_heart)
            self.cards.append(card)
        self.refresh_grid()

        if items:
            self.pending = len(items)
            threading.Thread(target=self._download_posters, args=(items,),
                             daemon=True).start()
            self.after(100, self._poll_posters)

    def _download_posters(self, items):
        for index, item in enumerate(items):
            url = item.get("image_url")
            self.poster_queue.put((index, download_image(url) if url else None))

    def _poll_posters(self):
        try:
            while True:
                index, img = self.poster_queue.get_nowait()
                self.pending -= 1
                if img is not None:
                    self.cards[index].set_poster(img)
        except queue.Empty:
            pass
        if self.pending > 0:
            self.after(150, self._poll_posters)

    # ───────── grille, recherche, favoris
    def refresh_grid(self):
        q = self.query.lower().strip()
        self.visible = [c for c in self.cards
                        if q in c.title.lower()
                        and (c.is_favorite or not self.only_favs)
                        and (c.item_id in self.later_ids or not self.only_later)]
        for card in self.cards:
            card.grid_forget()
        for i, card in enumerate(self.visible):
            card.grid(row=i // self.COLUMNS, column=i % self.COLUMNS,
                      padx=(0, 12), pady=(0, 12))

        n = len(self.visible)
        if not self.cards:
            text = "Aucun élément trouvé (vérifie la connexion Supabase)"
        elif self.only_favs:
            text = f"{n} favori(s)" if n else "Aucun favori pour l'instant"
        elif self.only_later:
            text = f"{n} dans ta liste" if n else "Ta liste est vide pour l'instant"
        elif q:
            text = f"{n} résultat(s) sur {len(self.cards)}"
        else:
            text = f"{n} {self.cfg['plural']} dans votre collection"
        self.subtitle.configure(text=text, text_color="#9a9a9a")
        self.sidebar.set_home_active(not (self.only_favs or self.only_later))

    def notice(self, text):
        self.subtitle.configure(text=text, text_color=RED)
        self.after(2500, self.refresh_grid)

    def go_home(self):
        self.only_favs = self.only_later = False
        self.query = ""
        self.sidebar.search_entry.delete(0, "end")
        self.sidebar.set_favorites_active(False)
        self.sidebar.set_later_active(False)
        self.refresh_grid()

    def on_search(self, text):
        self.query = text
        self.refresh_grid()

    def toggle_favorites_view(self):
        if not self.only_favs and db.current_user_id() is None:
            self.notice("Connecte-toi pour voir tes favoris (bouton 👤 en haut à droite).")
            return
        self.only_favs = not self.only_favs
        self.only_later = False
        self.sidebar.set_favorites_active(self.only_favs)
        self.sidebar.set_later_active(False)
        self.refresh_grid()

    def toggle_later_view(self):
        if not self.only_later and db.current_user_id() is None:
            self.notice("Connecte-toi pour voir ta liste (bouton 👤 en haut à droite).")
            return
        self.only_later = not self.only_later
        self.only_favs = False
        self.sidebar.set_later_active(self.only_later)
        self.sidebar.set_favorites_active(False)
        self.refresh_grid()

    def on_heart(self, card):
        if db.current_user_id() is None:
            self.notice("Connecte-toi pour utiliser les favoris (bouton 👤 en haut à droite).")
            return
        state = db.toggle_favorite(self.cfg["kind"], card.item_id)
        if state is None:
            self.notice("Erreur : favori non modifié.")
            return
        card.set_favorite(state)
        if self.only_favs:
            self.refresh_grid()

    def random_item(self):
        pool = self.visible or self.cards
        if pool:
            self.open_fiche(random.choice(pool))

    # ───────── fenêtres
    def open_fiche(self, card):
        if self.fiche is not None and self.fiche.winfo_exists():
            self.fiche.focus()
            return

        def favorite_changed(state, c=card):
            c.set_favorite(state)
            if self.only_favs:
                self.refresh_grid()

        def later_changed(state, c=card):
            if state:
                self.later_ids.add(c.item_id)
            else:
                self.later_ids.discard(c.item_id)
            if self.only_later:
                self.refresh_grid()

        self.fiche = Fiche(self.winfo_toplevel(), self.cfg, card.item,
                           card.is_favorite, favorite_changed,
                           card.item_id in self.later_ids, later_changed)

    def show_profile(self):
        top = self.winfo_toplevel()
        if db.current_user_id() is None:
            LoginDialog(top, self.after_auth)
            return

        box = CTkToplevel(top)
        box.title("Profil")
        box.geometry("300x190")
        box.resizable(False, False)
        box.transient(top)
        CTkLabel(box, text="👤  " + (db.current_pseudo() or "Connecté"),
                 font=("Arial", 16, "bold"), text_color="white").pack(pady=(30, 18))

        def logout():
            db.sign_out()
            box.destroy()
            self.after_auth()

        CTkButton(box, text="SE DÉCONNECTER", width=160, fg_color=RED,
                  hover_color="#c70022", command=logout).pack(pady=4)
        CTkButton(box, text="FERMER", width=160, fg_color=GREY, hover_color="#3a3a3a",
                  command=box.destroy).pack(pady=4)

    def after_auth(self):
        refresh = getattr(self.winfo_toplevel(), "refresh_all", None)
        if refresh:
            refresh()
        else:
            self.refresh_favorites()

    def refresh_favorites(self):
        favs = db.get_favorites(self.cfg["kind"])
        for card in self.cards:
            card.set_favorite(card.item_id in favs)
        self.later_ids = db.get_watchlist(self.cfg["kind"])
        if db.current_user_id() is None:
            self.only_favs = self.only_later = False
            self.sidebar.set_favorites_active(False)
            self.sidebar.set_later_active(False)
        self.refresh_grid()
