"""Fenêtre de détails d'un film ou d'un jeu (même code pour les deux)."""

import threading
import webbrowser
from urllib.parse import quote_plus

from customtkinter import *

import db
from theme import POSTER_SIZE, RED, download_image, placeholder

STAR_ON = "#ffc400"
STAR_OFF = "#555555"
BTN = "#292929"
BTN_HOVER = "#3b3b3b"


class Fiche(CTkToplevel):
    W, H = 820, 620

    def __init__(self, master, cfg, item, is_favorite, on_favorite,
                 in_later=False, on_later=None):
        super().__init__(master)
        self.cfg = cfg
        self.item = item
        self.kind = cfg["kind"]
        self.item_id = item[cfg["id_key"]]
        self.titre = item.get(cfg["title_key"]) or ""
        self.is_favorite = is_favorite
        self.on_favorite = on_favorite
        self.in_later = in_later
        self.on_later = on_later
        self.poster_result = None  # None = en cours, False = échec, sinon image

        self.title(self.titre)
        self.resizable(False, False)
        self.configure(fg_color="#101112")
        self.transient(master)
        x = master.winfo_rootx() + (master.winfo_width() - self.W) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.H) // 2
        self.geometry(f"{self.W}x{self.H}+{max(0, x)}+{max(0, y)}")
        self.after(150, self._take_focus)

        contenu = CTkFrame(self, fg_color="transparent")
        contenu.pack(fill="both", expand=True, padx=20, pady=20)
        contenu.grid_columnconfigure(1, weight=1)
        contenu.grid_rowconfigure(0, weight=1)

        # ── Affiche (à gauche) ──
        self.poster = CTkLabel(
            contenu, text=self.titre, compound="center",
            image=CTkImage(placeholder(POSTER_SIZE), size=POSTER_SIZE),
            font=("Arial", 16, "bold"), text_color="white", wraplength=150
        )
        self.poster.grid(row=0, column=0, padx=(0, 22), sticky="n")

        # ── Informations (à droite) ──
        infos = CTkFrame(contenu, fg_color="transparent")
        infos.grid(row=0, column=1, sticky="nsew")

        CTkLabel(infos, text=self.titre.upper(), font=("Arial", 21, "bold"),
                 text_color="white", anchor="w", wraplength=480, justify="left"
                 ).pack(fill="x", pady=(0, 10))

        for label, value in cfg["fields"](item):
            self._info(infos, label, value or "—")

        # Étoiles
        CTkLabel(infos, text="TA NOTE (CLIQUE SUR UNE ÉTOILE)", text_color="#aaaaaa",
                 font=("Arial", 10), anchor="w").pack(fill="x", pady=(8, 0))
        etoiles = CTkFrame(infos, fg_color="transparent")
        etoiles.pack(anchor="w", pady=(0, 8))
        self.stars = []
        for n in range(1, 6):
            star = CTkButton(etoiles, text="★", width=29, height=30,
                             fg_color="transparent", hover_color=BTN,
                             text_color=STAR_OFF, font=("Arial", 23),
                             command=lambda v=n: self.rate(v))
            star.pack(side="left", padx=(0, 1))
            self.stars.append(star)
        self.note_label = CTkLabel(etoiles, text="", text_color="white", font=("Arial", 11))
        self.note_label.pack(side="left", padx=(8, 0))

        note = 0
        if db.current_user_id() is not None:
            note = db.get_rating(self.kind, self.item_id)
        self.show_note(note)

        # Plateformes (jeux uniquement)
        tags = cfg["tags"](item)
        if tags:
            CTkLabel(infos, text=cfg["tags_label"], text_color="#aaaaaa",
                     font=("Arial", 10), anchor="w").pack(fill="x", pady=(2, 4))
            ligne = CTkFrame(infos, fg_color="transparent")
            ligne.pack(anchor="w", pady=(0, 8))
            for nom in tags:
                CTkLabel(ligne, text=nom, fg_color="#292b2d", corner_radius=14,
                         text_color="white", font=("Arial", 10), padx=10, pady=5
                         ).pack(side="left", padx=(0, 6))

        # Description
        CTkLabel(infos, text="DESCRIPTION", text_color="#aaaaaa",
                 font=("Arial", 10), anchor="w").pack(fill="x", pady=(2, 2))
        CTkLabel(infos, text=item.get(cfg["desc_key"]) or "Pas de description.",
                 text_color="#dddddd", font=("Arial", 11), wraplength=480,
                 justify="left", anchor="w").pack(fill="x", pady=(0, 10))

        # Boutons
        CTkButton(infos, text="FERMER", height=30, fg_color=BTN, hover_color=BTN_HOVER,
                  border_width=1, border_color="#555555", command=self.destroy
                  ).pack(fill="x", pady=3)
        self.later_btn = CTkButton(infos, text="", height=30, fg_color=BTN,
                                   hover_color=BTN_HOVER, command=self.toggle_later)
        self.later_btn.pack(fill="x", pady=3)
        self._update_later_button()
        self.fav_btn = CTkButton(infos, text="", height=30, fg_color=BTN,
                                 hover_color=BTN_HOVER, command=self.toggle_fav)
        self.fav_btn.pack(fill="x", pady=3)
        self._update_fav_button()
        CTkButton(infos, text=cfg["trailer_text"], height=32, fg_color=RED,
                  hover_color="#c70022", command=self.open_trailer
                  ).pack(fill="x", pady=(5, 0))

        self.status = CTkLabel(infos, text="", text_color="#9a9a9a",
                               font=("Arial", 11), anchor="w")
        self.status.pack(fill="x", pady=(8, 0))

        # Affiche en grand, téléchargée en arrière-plan
        url = item.get("image_url")
        if url:
            threading.Thread(target=self._download, args=(url,), daemon=True).start()
            self.after(150, self._wait_poster)

    # ───────── affichage ─────────
    @staticmethod
    def _info(parent, label, value):
        bloc = CTkFrame(parent, fg_color="transparent")
        bloc.pack(fill="x", pady=3)
        CTkLabel(bloc, text=label, text_color="#aaaaaa", font=("Arial", 9),
                 anchor="w").pack(fill="x")
        CTkLabel(bloc, text=value, text_color="white", font=("Arial", 12, "bold"),
                 anchor="w").pack(fill="x")

    def say(self, text):
        self.status.configure(text=text)

    def show_note(self, note):
        for i, star in enumerate(self.stars, start=1):
            star.configure(text_color=STAR_ON if i <= note else STAR_OFF)
        self.note_label.configure(text=f"{note} / 5" if note else "pas encore noté")

    def _update_fav_button(self):
        self.fav_btn.configure(
            text="♥ RETIRER DES FAVORIS" if self.is_favorite else "♡ AJOUTER AUX FAVORIS"
        )

    def _update_later_button(self):
        self.later_btn.configure(
            text=self.cfg["later_in"] if self.in_later else self.cfg["later_text"]
        )

    def _take_focus(self):
        try:
            self.grab_set()
            self.focus()
        except Exception:
            pass

    # ───────── affiche ─────────
    def _download(self, url):
        img = download_image(url, POSTER_SIZE)
        self.poster_result = img if img is not None else False

    def _wait_poster(self):
        try:
            if self.poster_result is None:
                self.after(150, self._wait_poster)
            elif self.poster_result is not False:
                self.poster.configure(
                    image=CTkImage(self.poster_result, size=POSTER_SIZE), text=""
                )
        except Exception:
            pass  # la fenêtre a été fermée entre-temps

    # ───────── actions ─────────
    def _logged(self):
        if db.current_user_id() is None:
            self.say("Connecte-toi pour utiliser cette fonction.")
            return False
        return True

    def rate(self, n):
        if not self._logged():
            return
        if db.save_rating(self.kind, self.item_id, n):
            self.show_note(n)
            self.say("Note enregistrée.")
        else:
            self.say("Impossible d'enregistrer la note.")

    def toggle_later(self):
        if not self._logged():
            return
        state = db.toggle_watchlist(self.kind, self.item_id)
        if state is None:
            self.say("Erreur : liste non modifiée.")
            return
        self.in_later = state
        self._update_later_button()
        if self.on_later:
            self.on_later(state)
        self.say(self.cfg["later_done"] if state else "Retiré de ta liste.")

    def toggle_fav(self):
        if not self._logged():
            return
        state = db.toggle_favorite(self.kind, self.item_id)
        if state is None:
            self.say("Erreur : favori non modifié.")
            return
        self.is_favorite = state
        self._update_fav_button()
        self.on_favorite(state)
        self.say("Ajouté aux favoris." if state else "Retiré des favoris.")

    def open_trailer(self):
        url = self.item.get("trailer_url")
        if not url:  # pas de lien en base : recherche YouTube
            requete = quote_plus(f"{self.titre} {self.cfg['trailer_query']}")
            url = "https://www.youtube.com/results?search_query=" + requete
        webbrowser.open(url)
