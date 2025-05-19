import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser(
    "~/.config/gcloud/application_default_credentials.json")

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from imdb_scraper import get_top_10_movies, get_summary_and_storyline
import google.generativeai as genai
from vertexai.preview.vision_models import ImageGenerationModel
import vertexai
from PIL import Image, ImageTk
import io

vertexai.init(
    project="dark-yen-459418-k4",
    location="us-central1"
)
vertexai.init(project="dark-yen-459418-k4", location="us-central1")


def generate_image(scene_description, location, style):
    model = ImageGenerationModel.from_pretrained("imagegeneration@002")

    prompt = f"""
    Generate a {style} style image for the following movie scene.

    Location: {location}
    Atmosphere: {scene_description}
    """

    print("IMAGE PROMPT:", prompt)

    try:
        model = ImageGenerationModel.from_pretrained("imagegeneration@002")
        image_response = model.generate_images(prompt=prompt, number_of_images=1)

        print("Image successfully generated:", image_response)

        image_bytes = image_response[0]._image_bytes
        image = Image.open(io.BytesIO(image_bytes))
        return image
    except Exception as e:
        print("IMAGE GENERATION ERROR:", e)
        return None


genai.configure(api_key="AIzaSyCtTPtcczd13x5K-VHHP6WaRMIknvlmtoY")


def generate_dialogue(storyline, num_chars, word_count, max_len):
    prompt = f"""
    Create a movie dialogue between {num_chars} characters.
    The dialogue should not exceed {max_len} words and should be based on the following storyline:

    {storyline}

    Limit total word count to approximately {word_count}.
    Return only the dialogue and a scene description at the top.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def clean_title(raw_title):
    if len(raw_title) > 2 and raw_title[1] == ".":
        return raw_title.split(". ", 1)[1]
    return raw_title


def start_gui():
    global current_dialogue
    current_dialogue = ""
    def on_select(event):
        selection = listbox.curselection()
        if not selection:
            return

        index = selection[0]
        raw_title = movie_data[index][0]
        title = clean_title(raw_title)
        summary, storyline = get_summary_and_storyline(title)

        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, f"Movie: {title}\n\n")
        text_box.insert(tk.END, f"Summary:\n{summary}\n\n")
        text_box.insert(tk.END, f"Storyline:\n{storyline}")

    def on_generate_dialogue():
        selection = listbox.curselection()
        if not selection:
            print("No movie selected.")
            return

        index = selection[0]
        raw_title = movie_data[index][0]
        title = clean_title(raw_title)
        summary, storyline = get_summary_and_storyline(title)

        try:
            num_chars = int(character_entry.get())
            word_count = int(wordcount_entry.get())
            max_len = int(maxlength_entry.get())
        except ValueError:
            print("Please enter valid numbers!")
            return

        print("Generating dialogue...")
        full_dialogue = generate_dialogue(storyline, num_chars, word_count, max_len)

        location = location_entry.get()
        style = style_combobox.get()

        scene_description = full_dialogue.strip().split("\n")[0]

        dangerous_words = ["kill", "dead", "blood", "war", "drug", "murder", "corpse", "naked", "violence"]
        if any(word in scene_description.lower() for word in dangerous_words):
            print("Scene description contains risky words. Replacing it with a safe default.")
            scene_description = "a peaceful futuristic city at night"

        print("SCENE DESCRIPTION:", scene_description)
        print("LOCATION:", location)

        img = generate_image(scene_description, location, style)

        if img is None:
            text_box.insert(tk.END, "\nCould not generate image. Try different location or description.\n")
            return

        img = img.resize((400, 300))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo

        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, f"Movie: {title}\n\n")
        text_box.insert(tk.END, f"Summary:\n{summary}\n\n")
        text_box.insert(tk.END, f"Storyline:\n{storyline}\n\n")
        text_box.insert(tk.END, f"Dialogue:\n{full_dialogue}")

        global current_dialogue
        current_dialogue = full_dialogue

    root = tk.Tk()
    root.title("IMDB TOP 10 MOVIES")
    root.geometry("900x600")

    def save_dialogue_to_file(dialogue, filename):

        try:
            if not filename.endswith('.txt'):
                filename += '.txt'

            with open(filename, 'w', encoding='utf-8') as file:
                file.write(dialogue)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    def on_save_dialogue():
        global current_dialogue
        if not current_dialogue:
            messagebox.showwarning("Warning", "No dialogue to save! Generate a dialogue first.")
            return

        filename = filename_entry.get().strip()
        if not filename:
            messagebox.showwarning("Warning", "Please enter a filename")
            return

        file_path = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            if save_dialogue_to_file(current_dialogue, file_path):
                messagebox.showinfo("Success", f"Dialogue saved to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to save dialogue")

    image_frame = ttk.Frame(root)
    image_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=(10, 0))

    image_label = tk.Label(image_frame)
    image_label.pack(pady=10)

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(main_frame, width=40, font=("Arial", 12))
    listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

    text_box = tk.Text(main_frame, wrap=tk.WORD, font=("Arial", 11))
    text_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    control_frame = ttk.Frame(root, padding=10)
    control_frame.pack(side=tk.BOTTOM, fill=tk.X)

    ttk.Label(control_frame, text="Location:").grid(row=0, column=2, padx=5, sticky=tk.W)
    location_entry = ttk.Entry(control_frame, width=20)
    location_entry.grid(row=0, column=3, padx=5)

    ttk.Label(control_frame, text="e.g. 'a street in Paris', 'a space station', 'a beach at sunset'",
              font=("Arial", 8, "italic")).grid(row=0, column=4, padx=5)

    ttk.Label(control_frame, text="Style:").grid(row=1, column=2, padx=5, sticky=tk.W)
    style_combobox = ttk.Combobox(control_frame, values=["Marvel", "Futuristic", "Cartoon", "Realistic"],
                                  state="readonly")
    style_combobox.current(0)
    style_combobox.grid(row=1, column=3, padx=5)

    ttk.Label(control_frame, text="Number of Characters:").grid(row=0, column=0, sticky=tk.W, padx=5)
    character_entry = ttk.Entry(control_frame, width=10)
    character_entry.grid(row=0, column=1, padx=5)

    ttk.Label(control_frame, text="Word Count:").grid(row=1, column=0, sticky=tk.W, padx=5)
    wordcount_entry = ttk.Entry(control_frame, width=10)
    wordcount_entry.grid(row=1, column=1, padx=5)

    ttk.Label(control_frame, text="Max Dialogue Length:").grid(row=2, column=0, sticky=tk.W, padx=5)
    maxlength_entry = ttk.Entry(control_frame, width=10)
    maxlength_entry.grid(row=2, column=1, padx=5)

    generate_button = ttk.Button(control_frame, text="Generate Dialogue", command=on_generate_dialogue)
    generate_button.grid(row=3, column=0, columnspan=2, pady=10)

    global movie_data
    movie_data = get_top_10_movies()
    for title, _ in movie_data:
        listbox.insert(tk.END, title)

    listbox.bind("<<ListboxSelect>>", on_select)

    buttons_frame = ttk.Frame(control_frame)
    buttons_frame.grid(row=3, column=2, columnspan=3, pady=10)

    ttk.Label(buttons_frame, text="File Name:").pack(side=tk.LEFT, padx=5)
    filename_entry = ttk.Entry(buttons_frame, width=30)
    filename_entry.pack(side=tk.LEFT, padx=5)
    filename_entry.insert(0, "movie_dialogue")

    save_button = ttk.Button(buttons_frame, text="Save Dialogue", command=on_save_dialogue)
    save_button.pack(side=tk.LEFT, padx=20)
    root.mainloop()
