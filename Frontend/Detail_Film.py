from customtkinter import *

set_appearance_mode("dark")
set_default_color_theme("blue")


class FilmApp(CTk):
    def __init__(self):
        super().__init__()

        self.title("Ma bibliothèque de films")
        self.geometry("760x470")
        self.minsize(620, 420)
        self.configure(fg_color="#090b0d")

        self.popup = None
        self.note = 4

        titre = CTkLabel(
            self, text="Mes films",
            font=CTkFont(size=25, weight="bold"),
            text_color="white"
        )
        titre.pack(anchor="w", padx=28, pady=(24, 16))

        # Carte du film : toute la carte est cliquable
        self.carte = CTkFrame(
            self, width=165, height=238,
            fg_color="#75401f", corner_radius=7,
            border_width=1, border_color="#168bd0",
            cursor="hand2"
        )
        self.carte.pack(anchor="nw", padx=28)
        self.carte.pack_propagate(False)

        self.nom_film = CTkLabel(
            self.carte,
            text="Dune :\nDeuxième\npartie",
            font=CTkFont(size=19, weight="bold"),
            text_color="white",
            justify="center",
            cursor="hand2"
        )
        self.nom_film.place(relx=0.5, rely=0.5, anchor="center")

        # Le clic sur le cadre ou le texte ouvre la petite fenêtre
        for widget in (self.carte, self.nom_film):
            widget.bind("<Button-1>", self.ouvrir_fiche)

        aide = CTkLabel(
            self, text="Clique sur l'affiche pour voir les détails du film.",
            text_color="#999999", font=CTkFont(size=12)
        )
        aide.pack(anchor="w", padx=28, pady=14)

    def ouvrir_fiche(self, event=None):
        # Empêche d'ouvrir plusieurs fenêtres identiques
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.focus()
            return

        self.popup = CTkToplevel(self)
        self.popup.title("Dune : Deuxième partie")
        self.popup.geometry("900x680")
        self.popup.resizable(False, False)
        self.popup.configure(fg_color="#101112")
        self.popup.transient(self)
        self.popup.grab_set()

        # Centre la fenêtre par rapport à la fenêtre principale
        self.popup.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 680) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 440) // 2
        self.popup.geometry(f"+{max(0, x)}+{max(0, y)}")

        contenu = CTkFrame(self.popup, fg_color="transparent")
        contenu.pack(fill="both", expand=True, padx=16, pady=16)
        contenu.grid_columnconfigure(1, weight=1)
        contenu.grid_rowconfigure(0, weight=1)

        # Affiche à gauche
        affiche = CTkFrame(
            contenu, width=190, height=390,
            fg_color="#75401f", corner_radius=6
        )
        affiche.grid(row=0, column=0, padx=(0, 18))
        affiche.grid_propagate(False)

        CTkLabel(
            affiche, text="Dune :\nDeuxième partie",
            font=CTkFont(size=20, weight="bold"),
            text_color="white", justify="center"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Informations à droite
        infos = CTkFrame(contenu, fg_color="transparent")
        infos.grid(row=0, column=1, sticky="nsew")
        infos.grid_columnconfigure(0, weight=1)

        CTkLabel(
            infos, text="DUNE : DEUXIÈME PARTIE",
            font=CTkFont(size=21, weight="bold"),
            text_color="white", anchor="w"
        ).pack(fill="x", pady=(0, 3))

        CTkLabel(
            infos, text="SCIENCE-FICTION",
            font=CTkFont(size=10, weight="bold"),
            text_color="#ff1744", anchor="w"
        ).pack(fill="x", pady=(0, 10))

        self.info(infos, "RÉALISATEUR", "Denis Villeneuve")
        self.info(infos, "DURÉE ET ANNÉE", "2h 46 · 2024")
        self.info(infos, "NOTE MOYENNE", "★ 8.5 / 10")

        CTkLabel(
            infos, text="TA NOTE (CLIQUE SUR UNE ÉTOILE)",
            text_color="#aaaaaa", font=CTkFont(size=10), anchor="w"
        ).pack(fill="x", pady=(7, 0))

        etoiles = CTkFrame(infos, fg_color="transparent")
        etoiles.pack(anchor="w", pady=(0, 8))
        self.etoile_labels = []

        for valeur in range(1, 6):
            etoile = CTkButton(
                etoiles, text="★", width=29, height=30,
                fg_color="transparent", hover_color="#292929",
                text_color="#ffc400", font=CTkFont(size=23),
                command=lambda n=valeur: self.changer_note(n)
            )
            etoile.pack(side="left", padx=(0, 1))
            self.etoile_labels.append(etoile)

        self.note_label = CTkLabel(
            etoiles, text="4 / 5", text_color="white",
            font=CTkFont(size=11)
        )
        self.note_label.pack(side="left", padx=(8, 0))
        self.changer_note(4)

        CTkLabel(
            infos, text="OÙ REGARDER",
            text_color="#aaaaaa", font=CTkFont(size=10), anchor="w"
        ).pack(fill="x", pady=(2, 4))

        plateformes = CTkFrame(infos, fg_color="transparent")
        plateformes.pack(anchor="w", pady=(0, 8))
        for nom in ("Prime Video", "Apple TV", "Canal+"):
            CTkLabel(
                plateformes, text=nom, fg_color="#292b2d",
                corner_radius=14, text_color="white",
                font=CTkFont(size=10), padx=10, pady=5
            ).pack(side="left", padx=(0, 6))

        CTkLabel(
            infos, text="DESCRIPTION",
            text_color="#aaaaaa", font=CTkFont(size=10), anchor="w"
        ).pack(fill="x", pady=(2, 2))

        CTkLabel(
            infos,
            text=("Paul Atréides s’allie aux Fremen pour venger sa famille "
                  "et empêcher un terrible futur."),
            text_color="#dddddd", font=CTkFont(size=11),
            wraplength=420, justify="left", anchor="w"
        ).pack(fill="x", pady=(0, 10))

        CTkButton(
            infos, text="FERMER", height=30,
            fg_color="#292929", hover_color="#3b3b3b",
            border_width=1, border_color="#555555",
            command=self.fermer_fiche
        ).pack(fill="x", pady=3)

        CTkButton(
            infos, text="＋ À VOIR PLUS TARD", height=30,
            fg_color="#292929", hover_color="#3b3b3b",
            command=lambda: self.message("Ajouté à la liste À voir plus tard.")
        ).pack(fill="x", pady=3)

        CTkButton(
            infos, text="♡ AJOUTER AUX FAVORIS", height=30,
            fg_color="#292929", hover_color="#3b3b3b",
            command=lambda: self.message("Ajouté aux favoris.")
        ).pack(fill="x", pady=3)

        CTkButton(
            infos, text="VOIR LA BANDE-ANNONCE", height=32,
            fg_color="#f00035", hover_color="#c9002d",
            command=lambda: self.message("Ajoute ici le lien de ta bande-annonce.")
        ).pack(fill="x", pady=(5, 0))

        self.popup.protocol("WM_DELETE_WINDOW", self.fermer_fiche)

    @staticmethod
    def info(parent, label, value):
        bloc = CTkFrame(parent, fg_color="transparent")
        bloc.pack(fill="x", pady=3)
        CTkLabel(
            bloc, text=label, text_color="#aaaaaa",
            font=CTkFont(size=9), anchor="w"
        ).pack(fill="x")
        CTkLabel(
            bloc, text=value, text_color="white",
            font=CTkFont(size=12, weight="bold"), anchor="w"
        ).pack(fill="x")

    def changer_note(self, note):
        self.note = note
        for index, bouton in enumerate(self.etoile_labels, start=1):
            bouton.configure(text_color="#ffc400" if index <= note else "#555555")
        self.note_label.configure(text=f"{note} / 5")

    def message(self, texte):
        boite = CTkToplevel(self.popup)
        boite.title("Information")
        boite.geometry("320x130")
        boite.resizable(False, False)
        boite.transient(self.popup)
        boite.grab_set()
        CTkLabel(
            boite, text=texte, wraplength=275,
            text_color="white"
        ).pack(padx=20, pady=20)
        CTkButton(
            boite, text="OK", command=boite.destroy, width=90
        ).pack(pady=(0, 15))

    def fermer_fiche(self):
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.grab_release()
            self.popup.destroy()
        self.popup = None


if __name__ == "__main__":
    app = FilmApp()
    app.mainloop()
