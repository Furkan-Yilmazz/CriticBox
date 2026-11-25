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


class ConnexionApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG)
        self.title("Connexion – GAMES")
        self.geometry("1100x700")
        self.minsize(900, 620)
        self.grid_columnconfigure((0, 1), weight=1, uniform="c")
        self.grid_rowconfigure(0, weight=1)

        Hero(self).grid(row=0, column=0, sticky="nsew")
        right = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(right, text="👤", width=30, height=30, corner_radius=15,
                     fg_color="#3a3a3a", font=(FONT, 12)).place(relx=1, x=-24, y=20, anchor="ne")

        f = ctk.CTkFrame(right, fg_color="transparent", width=360, height=520)
        f.pack_propagate(False)
        f.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(f, text="GAMES", text_color=RED, font=(FONT, 17, "bold")).pack(anchor="w")
        ctk.CTkLabel(f, text="CONNEXION", font=(FONT, 25, "bold")).pack(anchor="w", pady=(8, 6))
        ctk.CTkLabel(f, text="Content de te revoir ! Connecte-toi pour retrouver tes favoris.",
                     text_color=MUTED, font=(FONT, 10)).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(f, text="Username", font=(FONT, 9)).pack(anchor="w", pady=(8, 4))
        box, self.user = field(f, "Ton Pseudo")
        box.pack()

        ctk.CTkLabel(f, text="MOT DE PASSE", font=(FONT, 9)).pack(anchor="w", pady=(12, 4))
        box, self.pw = field(f, "••••••••", secret=True)
        box.pack()

        ctk.CTkButton(f, text="Mot de passe oublié ?", fg_color="transparent", hover=False,
                      text_color=RED, font=(FONT, 9, "bold"), width=0, height=20,
                      command=lambda: self.msg.configure(text="Fonction à venir.")
                      ).pack(anchor="e", pady=(8, 8))

        ctk.CTkButton(f, text="SE CONNECTER", height=34, corner_radius=4, fg_color=RED,
                      hover_color=RED_HOVER, font=(FONT, 10, "bold"), command=self.submit).pack(fill="x")
        ctk.CTkLabel(f, text="ou", font=(FONT, 9)).pack(pady=8)
        ctk.CTkButton(f, text="CONTINUER AVEC GOOGLE", height=34, corner_radius=4, fg_color=BG,
                      hover_color=FIELD, border_width=1, border_color=LINE,
                      font=(FONT, 10, "bold")).pack(fill="x")

        self.msg = ctk.CTkLabel(f, text="", text_color="#ff6b81", font=(FONT, 9))
        self.msg.pack(pady=(8, 0))

        foot = ctk.CTkFrame(f, fg_color="transparent")
        foot.pack(pady=(6, 0))
        ctk.CTkLabel(foot, text="Pas encore de compte ?", text_color=MUTED, font=(FONT, 10)).pack(side="left")
        ctk.CTkButton(foot, text="Créer un compte", fg_color="transparent", hover=False, text_color=RED,
                      font=(FONT, 10, "bold"), width=0, command=self.go_signup).pack(side="left", padx=4)

    def submit(self):
        if not self.user.get().strip() or not self.pw.get():
            self.msg.configure(text="Renseigne ton pseudo et ton mot de passe.")
            return
        self.msg.configure(text="")
        # TODO : vérifier les identifiants (base de données / API)
        print("Connexion :", self.user.get())

    def go_signup(self):
        self.destroy()
        from inscription import InscriptionApp
        InscriptionApp().mainloop()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ConnexionApp().mainloop()