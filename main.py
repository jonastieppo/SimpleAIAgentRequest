# %%
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import io
from AI_parser import returnFunctionCall # LLM_request is used by returnFunctionCall internally
from googletrans import Translator, LANGUAGES # Import Translator

class ImageBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Browser with Prompt")
        self.root.geometry("500x550")  # Increased height for the new widget
        self.root.configure(bg='lightgray')

        # Image history and current index
        self.image_history = []  # Stores (image_data, url) tuples
        self.current_image_index = -1

        # User prompts storage
        self.user_prompts = []

        # Initialize the translator
        self.translator = Translator()

        # --- Central Image Widget ---
        # Create a frame for the image to help with centering and padding
        image_frame = tk.Frame(root, pady=10, bg='lightgray') # Reduced pady for image
        image_frame.pack(expand=True, fill=tk.BOTH)

        self.image_label = tk.Label(image_frame, bg='white')
        self.image_label.pack(expand=True) # Center the label in the frame

        # --- Bottom Buttons (Packed BEFORE prompt field to appear above it) ---
        button_frame = tk.Frame(root, bg='lightgray')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.prev_button = tk.Button(button_frame, text="Previous Image", command=self.load_previous_image, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=(20, 10), pady=5, expand=True)

        self.next_button = tk.Button(button_frame, text="Next Image", command=self.load_next_image)
        self.next_button.pack(side=tk.RIGHT, padx=(10, 20), pady=5, expand=True)

        # --- Bottom Text Field (Packed LAST with side=BOTTOM to be at the very bottom) ---
        prompt_outer_frame = tk.Frame(root, bg='lightgray') # Frame to hold label and entry
        prompt_outer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        prompt_label = tk.Label(prompt_outer_frame, text="Your Prompt:", bg='lightgray')
        prompt_label.pack(side=tk.LEFT, padx=(20, 5))

        self.prompt_entry = tk.Entry(prompt_outer_frame, relief=tk.SUNKEN, borderwidth=2)
        self.prompt_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 20), ipady=2)
        self.prompt_entry.bind("<Return>", self.submit_prompt) # Bind Enter key

        # Load the initial image (AFTER all UI elements are defined and packed)
        self.load_next_image()

    def fetch_image_from_url(self, url="https://picsum.photos/200/200"):
        """Fetches an image from the given URL or a new random one."""
        try:
            headers = {'Cache-Control': 'no-cache'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            image_data = response.content
            actual_url = response.url
            return image_data, actual_url
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch image: {e}")
            # Ensure label is cleared or shows error if fetch fails critically before first image
            if self.current_image_index < 0 and not self.image_history:
                 self.image_label.config(text="Image load failed. Try 'Next'.", image=None)
                 self.image_label.image = None
            return None, None

    def display_image(self, image_data):
        """Displays the given image data in the label."""
        if image_data:
            try:
                pil_image = Image.open(io.BytesIO(image_data))
                pil_image = pil_image.resize((200, 200), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(pil_image)

                self.image_label.config(image=tk_image, text="") # Clear any previous text
                self.image_label.image = tk_image
            except Exception as e:
                messagebox.showerror("Error", f"Failed to display image: {e}")
                self.image_label.config(image=None, text="Error displaying image")
                self.image_label.image = None
        else:
            # This case might be hit if fetch_image_from_url returns None for image_data
            if not self.image_history: # If it's the very first load attempt and it failed
                self.image_label.config(image=None, text="Click 'Next Image' to load.")
            else: # If there was a previous image, keep it or show generic error
                self.image_label.config(text="Failed to load new image.")
            self.image_label.image = None


    def load_next_image(self):
        """Loads the next image, either from history or a new one."""
        self.current_image_index += 1

        if self.current_image_index < len(self.image_history):
            image_data, _ = self.image_history[self.current_image_index]
            self.display_image(image_data)
        else:
            image_data, actual_url = self.fetch_image_from_url()
            if image_data and actual_url:
                self.image_history = self.image_history[:self.current_image_index]
                self.image_history.append((image_data, actual_url))
                self.current_image_index = len(self.image_history) - 1
                self.display_image(image_data)
            else:
                self.current_image_index -= 1 # Revert index if load failed
                # If it was the first attempt and failed, display_image(None) handles message
                if not self.image_history and self.current_image_index < 0:
                    self.display_image(None)


        self.update_button_states()

    def load_previous_image(self):
        """Loads the previous image from history."""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            image_data, _ = self.image_history[self.current_image_index]
            self.display_image(image_data)
        self.update_button_states()

    def update_button_states(self):
        """Updates the state of the Previous and Next buttons."""
        if self.current_image_index <= 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)

    def _translate_to_english(self, text_to_translate: str) -> str:
        """Translates the given text to English using googletrans."""
        if not text_to_translate:
            return ""
        try:
            print(f"Attempting to translate: '{text_to_translate}'")
            # Detect language and translate to English
            # You can also specify src language if you know it, e.g., translator.translate(text_to_translate, src='pt', dest='en')
            translation = self.translator.translate(text_to_translate, dest='en')
            translated_text = translation.text
            detected_lang = LANGUAGES.get(translation.src, translation.src) # Get full language name
            print(f"Detected source language: {detected_lang} ('{translation.src}')")
            print(f"Translated to English: '{translated_text}'")
            return translated_text
        except Exception as e:
            print(f"Error during translation: {e}")
            messagebox.showerror("Translation Error", f"Could not translate text: {e}")
            return text_to_translate # Fallback to original text on error

    def submit_prompt(self, event=None):
        """Handles the submission of text from the prompt_entry widget."""
        prompt_text = self.prompt_entry.get().strip()
        if prompt_text:
            prompt_text_english = self._translate_to_english(prompt_text)
            function_name = returnFunctionCall(["load_next_image", "load_previous_image"], prompt_text_english)

            self.user_prompts.append(prompt_text) # Store original prompt
            self.prompt_entry.delete(0, tk.END)
            print(f"Original prompt: '{prompt_text}', Translated: '{prompt_text_english}', Function: {function_name}")
            print(f"Current prompts array: {self.user_prompts}")

            # --- Handle the function call based on function_name ---
            if function_name == "load_next_image":
                self.load_next_image()
            elif function_name == "load_previous_image":
                self.load_previous_image()
            else:
                # Optionally, provide feedback if the function_name is not recognized
                # or if no specific action is tied to it yet.
                print(f"No specific action defined for function: {function_name}")
        else:
            print("Empty prompt entered, not stored.")

if __name__ == "__main__":
    main_window = tk.Tk()
    app = ImageBrowserApp(main_window)
    main_window.mainloop()

# %%
