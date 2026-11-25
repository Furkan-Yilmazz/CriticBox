"""
Auteur : Furkan YILMAZ
Version : 0.0
Date : 25/11/2026
"""

import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk

RED, RED_HOVER = "#ee0028", "#ff1a40"
BG, FIELD, LINE, MUTED = "#0d0d0d", "#1b1b1b", "#2b2b2b", "#9a9a9a"
FONT = "Arial"


class Hero(tk.Canvas):
    "Panneau gauche : dégradé rouge → noir + texte."

    def __init__(self, master):
        super().__init__(master, highlightthickness=0, bd=0, bg="#4d0012")
        self._img = None
        self.bind("<Configure>", self._draw)

    def _draw(self, e):
        w, h = max(e.width, 1), max(e.height, 1)
        img = Image.new("RGB", (w, h))
        d = ImageDraw.Draw(img)
        top, bot = (155, 0, 40), (14, 0, 4)
        for y in range(h):
            t = (y / h) ** 0.9
            d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))
        self._img = ImageTk.PhotoImage(img)
        self.delete("all")
        self.create_image(0, 0, image=self._img, anchor="nw")
        x, y = int(w * 0.12), h // 2 - 70
        self.create_text(x, y, text="GAMES & FILMS", anchor="w", fill="white", font=(FONT, 30, "bold"))
        self.create_text(x, y + 45, text="Trouve ton prochain jeu ou film en quelques clics.",
                         anchor="w", fill="white", font=(FONT, 12), width=int(w * 0.76))
        for i, t in enumerate(["★  Note tes jeux et tes films",
                               "♥  Garde tes favoris au même endroit",
                               "+  Crée ta liste « à voir plus tard »"]):
            self.create_text(x, y + 85 + i * 26, text=t, anchor="w", fill="white", font=(FONT, 10, "bold"))


def field(parent, placeholder, secret=False):
    "Champ de saisie avec bouton Afficher/Masquer pour les mots de passe."
    box = ctk.CTkFrame(parent, fg_color=FIELD, border_color=LINE, border_width=1,
                       corner_radius=4, height=36, width=360)
    box.pack_propagate(False)
    entry = ctk.CTkEntry(box, placeholder_text=placeholder, show="•" if secret else "",
                         fg_color="transparent", border_width=0, text_color="white",
                         placeholder_text_color="#777", font=(FONT, 11))
    entry.pack(side="left", fill="both", expand=True, padx=(6, 0))
    if secret:
        btn = ctk.CTkButton(box, text="Afficher", width=54, height=24, fg_color="transparent",
                            hover=False, text_color="#cfcfcf", font=(FONT, 9))

        def toggle():
            hidden = entry.cget("show") == "•"
            entry.configure(show="" if hidden else "•")
            btn.configure(text="Masquer" if hidden else "Afficher")

        btn.configure(command=toggle)
        btn.pack(side="right", padx=4)
    return box, entry


class InscriptionApp(ctk.CTk):
    PREFS = ["Jeux", "Films", "Les deux"]

    def __init__(self):
        super().__init__(fg_color=BG)
        self.title("Créer un compte – GAMES")
        self.geometry("1100x760")
        self.minsize(900, 700)
        self.grid_columnconfigure((0, 1), weight=1, uniform="c")
        self.grid_rowconfigure(0, weight=1)
        self.pref = tk.StringVar(value="Les deux")

        Hero(self).grid(row=0, column=0, sticky="nsew")
        right = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(right, text="👤", width=30, height=30, corner_radius=15,
                     fg_color="#3a3a3a", font=(FONT, 12)).place(relx=1, x=-24, y=20, anchor="ne")

        f = ctk.CTkFrame(right, fg_color="transparent", width=360, height=640)
        f.pack_propagate(False)
        f.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(f, text="GAMES", text_color=RED, font=(FONT, 17, "bold")).pack(anchor="w")
        ctk.CTkLabel(f, text="CRÉER UN COMPTE", font=(FONT, 25, "bold")).pack(anchor="w", pady=(8, 6))
        ctk.CTkLabel(f, text="Rejoins-nous pour noter, sauvegarder et découvrir.",
                     text_color=MUTED, font=(FONT, 10)).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(f, text="PSEUDO", font=(FONT, 9)).pack(anchor="w", pady=(8, 4))
        box, self.pseudo = field(f, "Ton pseudo")
        box.pack()

        ctk.CTkLabel(f, text="MOT DE PASSE", font=(FONT, 9)).pack(anchor="w", pady=(10, 4))
        box, self.pw = field(f, "8 caractères minimum", secret=True)
        box.pack()

        ctk.CTkLabel(f, text="CONFIRMER LE MOT DE PASSE", font=(FONT, 9)).pack(anchor="w", pady=(10, 4))
        box, self.pw2 = field(f, "Répète le mot de passe", secret=True)
        box.pack()

        ctk.CTkLabel(f, text="TU PRÉFÈRES", font=(FONT, 9)).pack(anchor="w", pady=(10, 4))
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        row.grid_columnconfigure((0, 1, 2), weight=1, uniform="p")
        self.pref_btns = {}
        for i, p in enumerate(self.PREFS):
            b = ctk.CTkButton(row, text=p, height=30, corner_radius=4, font=(FONT, 9, "bold"),
                              command=lambda p=p: self.set_pref(p))
            b.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 4, 0 if i == 2 else 4))
            self.pref_btns[p] = b
        self.set_pref("Les deux")

        self.cgu = ctk.CTkCheckBox(f, text="J'accepte les conditions d'utilisation", font=(FONT, 9),
                                   text_color=MUTED, fg_color=RED, hover_color=RED_HOVER,
                                   border_color=LINE, checkbox_width=14, checkbox_height=14, corner_radius=2)
        self.cgu.pack(anchor="w", pady=14)

        ctk.CTkButton(f, text="CRÉER MON COMPTE", height=34, corner_radius=4, fg_color=RED,
                      hover_color=RED_HOVER, font=(FONT, 10, "bold"), command=self.submit).pack(fill="x")

        self.msg = ctk.CTkLabel(f, text="", text_color="#ff6b81", font=(FONT, 9), wraplength=360)
        self.msg.pack(pady=(8, 0))

        foot = ctk.CTkFrame(f, fg_color="transparent")
        foot.pack(pady=(4, 0))
        ctk.CTkLabel(foot, text="Déjà un compte ?", text_color=MUTED, font=(FONT, 10)).pack(side="left")
        ctk.CTkButton(foot, text="Se connecter", fg_color="transparent", hover=False, text_color=RED,
                      font=(FONT, 10, "bold"), width=0, command=self.go_login).pack(side="left", padx=4)

    def set_pref(self, value):
        self.pref.set(value)
        for p, b in self.pref_btns.items():
            on = p == value
            b.configure(fg_color=RED if on else FIELD, hover_color=RED_HOVER if on else LINE)

    def submit(self):
        pw = self.pw.get()
        if not self.pseudo.get().strip():
            return self.msg.configure(text="Choisis un pseudo.")
        if len(pw) < 8:
            return self.msg.configure(text="Le mot de passe doit contenir au moins 8 caractères.")
        if pw != self.pw2.get():
            return self.msg.configure(text="Les mots de passe ne correspondent pas.")
        if not self.cgu.get():
            return self.msg.configure(text="Accepte les conditions d'utilisation pour continuer.")
        self.msg.configure(text="")
        # TODO : enregistrer l'utilisateur (base de données / API)
        print("Compte créé :", self.pseudo.get(), "| préférence :", self.pref.get())

    def go_login(self):
        self.destroy()
        from connexion import ConnexionApp
        ConnexionApp().mainloop()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    InscriptionApp().mainloop()