import tkinter as tk
from tkinter import ttk
from imdb_scraper import get_top_10_movies, get_summary_and_storyline
import google.generativeai as genai
from vertexai.preview.vision_models import ImageGenerationModel
import vertexai
from PIL import Image, ImageTk
import io

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

        # Scene description = first paragraph of Gemini's response
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

        # Resize for Tkinter display
        img = img.resize((400, 300))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo  # keep reference

        # Display info in text box
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, f"Movie: {title}\n\n")
        text_box.insert(tk.END, f"Summary:\n{summary}\n\n")
        text_box.insert(tk.END, f"Storyline:\n{storyline}\n\n")
        text_box.insert(tk.END, f"Dialogue:\n{full_dialogue}")

    root = tk.Tk()
    root.title("IMDB TOP 10 MOVIES")
    root.geometry("900x600")

    image_label = tk.Label(root)
    image_label.pack(side=tk.BOTTOM, pady=10)

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

    root.mainloop()
