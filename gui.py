import tkinter as tk
from tkinter import ttk, messagebox
from logic import fetch_imdb_top_10, get_movie_storyline, generate_dialogue_gemini, generate_image_vertex
from PIL import ImageTk
from io import BytesIO

class AppGUI:
    def __init__(self, master):
        self.master = master
        self.movies = fetch_imdb_top_10()
        self.setup_ui()
        print("Movies loaded:", self.movies)

    def setup_ui(self):
        self.left_frame = tk.Frame(self.master)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.right_frame = tk.Frame(self.master)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.movie_listbox = tk.Listbox(self.left_frame, height=15, width=40)
        self.movie_listbox.pack()
        for title, _ in self.movies:
            self.movie_listbox.insert(tk.END, title)
        self.movie_listbox.bind("<<ListboxSelect>>", self.display_movie_details)

        self.story_text = tk.Text(self.right_frame, height=8, width=60)
        self.story_text.pack(pady=5)

        self.dp1 = tk.IntVar(value=2)
        self.dp2 = tk.StringVar(value="500")
        self.igp1 = tk.StringVar()
        self.igp2 = tk.StringVar(value="Futuristic")

        tk.Label(self.right_frame, text="Characters in Dialogue (2-4):").pack()
        tk.Entry(self.right_frame, textvariable=self.dp1).pack()

        tk.Label(self.right_frame, text="Max Word Count:").pack()
        tk.Entry(self.right_frame, textvariable=self.dp2).pack()

        tk.Label(self.right_frame, text="Location:").pack()
        tk.Entry(self.right_frame, textvariable=self.igp1).pack()

        tk.Label(self.right_frame, text="Style:").pack()
        styles = ["Marvel", "Futuristic", "Cartoon", "Realistic"]
        ttk.Combobox(self.right_frame, textvariable=self.igp2, values=styles).pack()

        tk.Button(self.right_frame, text="Generate Dialogue & Image", command=self.generate_all).pack(pady=10)

        self.dialogue_text = tk.Text(self.right_frame, height=15, width=60)
        self.dialogue_text.pack()

    def display_movie_details(self, event):
        index = self.movie_listbox.curselection()[0]
        title, _ = self.movies[index]
        storyline = get_movie_storyline(title)
        self.story_text.delete("1.0", tk.END)
        self.story_text.insert(tk.END, f"{title}:\n{storyline}")

    def generate_all(self):
        selection = self.movie_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a movie from the list first.")
            return

        index = selection[0]
        title, _ = self.movies[index]

        storyline = self.story_text.get("1.0", tk.END).strip()
        dialogue = generate_dialogue_gemini(storyline, self.dp1.get(), self.dp2.get())
        self.dialogue_text.delete("1.0", tk.END)
        self.dialogue_text.insert(tk.END, dialogue)
        prompt = f"{storyline} in {self.igp2.get()} style, located in {self.igp1.get()}"
        img = generate_image_vertex(prompt)
        img.show()
