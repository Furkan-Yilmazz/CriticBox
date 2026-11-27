"""affiche la page des films ou celle des jeux."""

from customtkinter import CTk

import db
from films import FilmsPage
from games import GamesPage
from login import LoginDialog

PAGES = {"film": FilmsPage, "jeu": GamesPage}


class App(CTk):
    def __init__(self, start="film"):
        super().__init__()
        self.geometry("1100x700")
        self.pages = {}
        self.current = None
        self.show(start)
        self.after(300, self.ask_login)  # propose de se connecter au démarrage

    def ask_login(self):
        if db.current_user_id() is None:
            LoginDialog(self, self.refresh_all)

    def refresh_all(self):
        for page in self.pages.values():
            page.refresh_favorites()

    def show(self, kind):
        if kind == self.current:
            return
        if self.current:
            self.pages[self.current].pack_forget()
        if kind not in self.pages:
            self.pages[kind] = PAGES[kind](self, self.show)
        page = self.pages[kind]
        page.pack(fill="both", expand=True)
        self.title(page.cfg["window_title"])
        self.current = kind


def run(start="film"):
    App(start).mainloop()


if __name__ == "__main__":
    run("film")
