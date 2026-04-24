import customtkinter as ctk


class VarDict(dict):
    def __missing__(self, key):
        self[key] = ctk.StringVar(value="")
        return self[key]
