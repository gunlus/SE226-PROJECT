import tkinter as tk
from tkinter import ttk
from imdb_scraper import get_top_10_movies, get_summary_and_storyline

def start_gui():
    def on_select(event):
        selection = listbox.curselection()
        if not selection:
            return

        index = selection[0]
        title = movie_data[index][0]
        summary, storyline = get_summary_and_storyline(title)

        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, f"🎬 Movie: {title}\n\n")
        text_box.insert(tk.END, f"📄 Summary:\n{summary}\n\n")
        text_box.insert(tk.END, f"📝 Storyline:\n{storyline}")

    def generate_dialogue():
        try:
            num_chars = int(character_entry.get())
            word_count = int(wordcount_entry.get())
            max_len = int(maxlength_entry.get())

            print("Generating dialogue with:")
            print("Characters:", num_chars)
            print("Word Count:", word_count)
            print("Max Length:", max_len)

            # Buraya ileride Gemini API entegrasyonu gelecek
        except ValueError:
            print("Please enter valid numbers!")

    root = tk.Tk()
    root.title("IMDB TOP 10 MOVIES")
    root.geometry("900x600")

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(main_frame, width=40, font=("Arial", 12))
    listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

    text_box = tk.Text(main_frame, wrap=tk.WORD, font=("Arial", 11))
    text_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # 🎯 Buraya yeni alanlar (Entry + Label + Button) ekleniyor:
    control_frame = ttk.Frame(root, padding=10)
    control_frame.pack(side=tk.BOTTOM, fill=tk.X)

    ttk.Label(control_frame, text="Number of Characters:").grid(row=0, column=0, sticky=tk.W, padx=5)
    character_entry = ttk.Entry(control_frame, width=10)
    character_entry.grid(row=0, column=1, padx=5)

    ttk.Label(control_frame, text="Word Count:").grid(row=1, column=0, sticky=tk.W, padx=5)
    wordcount_entry = ttk.Entry(control_frame, width=10)
    wordcount_entry.grid(row=1, column=1, padx=5)

    ttk.Label(control_frame, text="Max Dialogue Length:").grid(row=2, column=0, sticky=tk.W, padx=5)
    maxlength_entry = ttk.Entry(control_frame, width=10)
    maxlength_entry.grid(row=2, column=1, padx=5)

    generate_button = ttk.Button(control_frame, text="Generate Dialogue", command=generate_dialogue)
    generate_button.grid(row=3, column=0, columnspan=2, pady=10)

    global movie_data
    movie_data = get_top_10_movies()
    for title, _ in movie_data:
        listbox.insert(tk.END, title)

    listbox.bind("<<ListboxSelect>>", on_select)

    root.mainloop()