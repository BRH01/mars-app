import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io
from tkcalendar import DateEntry
import threading
import time
from tkinter import filedialog

class MarsRoverPhotoViewer(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.api_key = "oWFaTJ9QHR0MGxjmsKUFNehxWWzo7mmTbeQXfLUQ"
        self.photos = []
        self.current_photos = []
        self.photo_index = 0
        
        self.init_ui()

    
    def init_ui(self):
        self.title("Mars Rover Photo Viewer")
        self.geometry("800x600")
        
        # Centering the window on the screen
        self.center_window()
        
        # Configure background color
        self.configure(bg="#D2B48C")  # Sand color
        
        # Create frame
        main_frame = tk.Frame(self, bg="#D2B48C")  # Sand color
        main_frame.pack(expand=True, fill="both", anchor="center")
        
        # Outer border
        outer_border = ttk.LabelFrame(main_frame, text='Nasa-OpenData', style="Outer.TLabelframe")
        outer_border.pack(expand=True, fill="both", padx=10, pady=10, anchor="center")
        
        # Inner border for image display
        inner_border = ttk.Frame(outer_border, style="Inner.TLabelframe")
        inner_border.pack(expand=True, fill="both", padx=5, pady=5, anchor="center")
        
        # Photo display
        self.photo_label = ttk.Label(inner_border, style="Photo.TLabel")
        self.photo_label.pack(expand=True, fill="both", side="top", anchor="center")
        
        # Additional information display
        self.info_label = ttk.Label(outer_border, text="", style="Info.TLabel")
        self.info_label.pack(anchor="center", padx=10, pady=(0, 5))
        
        # Date selection
        date_label = ttk.Label(outer_border, text="Select Date:", style="Label.TLabel")
        date_label.pack(anchor="center", padx=10, pady=(5, 0))
        
        self.date_entry = DateEntry(outer_border, date_pattern="yyyy-mm-dd", style="Entry.TEntry")
        self.date_entry.pack(anchor="center", padx=10, pady=(0, 5))
        
        # Rover selection
        rover_label = ttk.Label(outer_border, text="Select Rover:", style="Label.TLabel")
        rover_label.pack(anchor="center", padx=10, pady=(5, 0))
        
        self.rover_combobox = ttk.Combobox(outer_border, values=["curiosity", "opportunity", "spirit", "all"], style="ComboboxRover.TCombobox")
        self.rover_combobox.pack(anchor="center", padx=10, pady=(0, 5))
        self.rover_combobox.bind("<<ComboboxSelected>>", self.on_update_camera_options)
        
        # Camera selection
        camera_label = ttk.Label(outer_border, text="Select Camera:", style="Label.TLabel")
        camera_label.pack(anchor="center", padx=10, pady=(5, 0))
        
        self.camera_combobox = ttk.Combobox(outer_border, values=["FHAZ", "RHAZ", "NAVCAM", "MAST", "CHEMCAM", "MAHLI", "MARDI", "PANCAM", "MINITES", "all"], style="ComboboxCamera.TCombobox")
        self.camera_combobox.pack(anchor="center", padx=10, pady=(0, 5))
        
        # Fetch button
        self.fetch_button = ttk.Button(outer_border, text="Fetch Photos", command=self.on_fetch_photos_clicked, style="Fetch.TButton")
        self.fetch_button.pack(anchor="center", padx=10, pady=(5, 0))
        
        # Navigation buttons
        nav_frame = ttk.Frame(outer_border, style="Nav.TFrame")
        nav_frame.pack(anchor="center", pady=(10, 5))
        
        prev_button = ttk.Button(nav_frame, text="Previous", command=self.prev_photo, style="Nav.TButton")
        prev_button.pack(side="left", padx=(0, 5))
        
        next_button = ttk.Button(nav_frame, text="Next", command=self.next_photo, style="Nav.TButton")
        next_button.pack(side="left")
        
        # Save button (initially hidden)
        self.save_button = ttk.Button(outer_border, text="Save", command=self.save_photo, style="Fetch.TButton")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("Outer.TLabelframe", background="#000000", foreground="#D2B48C")  # Outer label frame: black background, sand color text
        self.style.configure("Inner.TLabelframe", background="#000000")  # Inner label frame: black background
        self.style.configure("Label.TLabel", background="#000000", foreground="#D2B48C")  # Labels: black background, sand color text
        self.style.configure("Entry.TEntry", background="#000000", foreground="#000000")  # Entry widgets: black background, black text
        self.style.configure("ComboboxRover.TCombobox", background="#D2B48C", foreground="#000000")  # Rover combobox: sand color background, black text
        self.style.configure("ComboboxCamera.TCombobox", background="#D2B48C", foreground="#000000")  # Camera combobox: sand color background, black text
        self.style.configure("Fetch.TButton", background="#000000", foreground="#000000")  # Fetch button: black background, black text
        self.style.configure("Nav.TFrame", background="#000000")  # Navigation frame: black background
        self.style.configure("Nav.TButton", background="#000000", foreground="#000000")  # Navigation buttons: black background, black text
        self.style.configure("Photo.TLabel", background="#000000", anchor="center")  # Photo label: black background, centered image
        self.style.configure("Info.TLabel", background="#000000", foreground="#D2B48C")  # Information label: black background, sand color text
        self.style.configure("Loading.TLabel", background="#000000", foreground="#FFFFFF")  # Loading label: black background, white text

    def center_window(self):
        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the x and y coordinates to center the window
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2

        # Set the window to center
        self.geometry(f"800x600+{x}+{y}")

    def fetch_photos(self, rover, sol, camera="all", page=1):
        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos"
        params = {
            "api_key": self.api_key,
            "earth_date": sol,
            "camera": camera,
            "page": page
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data["photos"] if "photos" in data else []

    def display_photos(self):
        if not self.photos:
            self.photo_label.config(text="No images available", foreground="white")
            return
        
        # Clear the current photo label
        self.photo_label.config(image="")
        
        # Update current photos list by creating a copy of the photos list
        self.current_photos = self.photos.copy()
        
        # Reset photo index
        self.photo_index = 0  
        
        # Display the first photo
        self.show_photo(self.photo_index)

    def show_photo(self, index):
        if 0 <= index < len(self.current_photos):
            photo = self.current_photos[index]
            img_url = photo["img_src"]
            img_response = requests.get(img_url)
            img_data = img_response.content
            
            # Open image and ensure it's in RGB mode
            img = Image.open(io.BytesIO(img_data))
            
            # Resize image to fit within the photo label while maintaining aspect ratio
            max_width = 780
            max_height = 580
            img.thumbnail((max_width, max_height))
            
            # Convert PIL Image to Tkinter PhotoImage
            self.photo_img = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo_img)
            
            # Display rover and camera info
            rover = photo.get("rover", {}).get("name", "Unknown Rover")
            camera = photo.get("camera", {}).get("full_name", "Unknown Camera")
            self.info_label.config(text=f"Rover: {rover}, Camera: {camera}")

    def prev_photo(self):
        if self.photo_index > 0:
            self.photo_index -= 1
            self.show_photo(self.photo_index)

    def next_photo(self):
        if self.photo_index < len(self.current_photos) - 1:
            self.photo_index += 1
            self.show_photo(self.photo_index)

    def on_fetch_photos_clicked(self):
        self.fetch_button.pack_forget()  # Hide the fetch button
        self.start_loading_animation()
        self.start_rover_animation()

        # Start a new thread to fetch photos
        threading.Thread(target=self.fetch_photos_async).start()

    def start_loading_animation(self):
        self.loading_text = "Loading"
        self.loading_label = ttk.Label(self, text=self.loading_text, style="Loading.TLabel")
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.loading_animation()

    def loading_animation(self):
        self.loading_text += "."
        if len(self.loading_text) > 10:
            self.loading_text = "Loading"
        self.loading_label.config(text=self.loading_text)
        self.after(500, self.loading_animation)

    def start_rover_animation(self):
        self.rover_square = ttk.Label(self, width=2, height=2, background="black")
        self.rover_square.place(relx=0, rely=0, anchor="nw")
        self.animate_rover()

    def animate_rover(self):
        self.move_rover()
        if self.rover_square.winfo_x() >= 785 and self.rover_square.winfo_y() == 0:
            self.rover_square.destroy()  # Destroy the rover square after completing the animation loop
        else:
            self.after(50, self.animate_rover)

    def move_rover(self):
        x = self.rover_square.winfo_x()
        y = self.rover_square.winfo_y()
        if x < 785 and y == 0:
            x += 5
        elif x == 785 and y < 585:
            y += 5
        elif x > 0 and y == 585:
            x -= 5
        elif x == 0 and y > 0:
            y -= 5
        self.rover_square.place(x=x, y=y)

    def fetch_photos_async(self):
        selected_date = self.date_entry.get()
        selected_rover = self.rover_combobox.get()
        selected_camera = self.camera_combobox.get()
        
        if selected_rover == "all":
            rovers = ["curiosity", "opportunity", "spirit"]
        else:
            rovers = [selected_rover]
        
        if selected_camera == "all":
            cameras = ["FHAZ", "RHAZ", "NAVCAM", "MAST", "CHEMCAM", "MAHLI", "MARDI", "PANCAM", "MINITES"]
        else:
            cameras = [selected_camera]
        
        self.photos = []
        for rover in rovers:
            for camera in cameras:
                self.photos.extend(self.fetch_photos(rover, selected_date, camera))
        
        self.display_photos()
        self.loading_label.destroy()  # Remove the loading label after fetching photos

    def on_update_camera_options(self, event):
        selected_rover = self.rover_combobox.get()
        if selected_rover == "all":
            self.camera_combobox.config(values=["all"])
        else:
            self.camera_combobox.config(values=["FHAZ", "RHAZ", "NAVCAM", "MAST", "CHEMCAM", "MAHLI", "MARDI", "PANCAM", "MINITES", "all"])
        self.camera_combobox.set("all")

    def save_photo(self):
        if not self.current_photos:
            return
        
        photo = self.current_photos[self.photo_index]
        img_url = photo["img_src"]
        img_response = requests.get(img_url)
        img_data = img_response.content
        
        # Open file dialog to choose save location
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
        
        if file_path:
            with open(file_path, "wb") as f:
                f.write(img_data)
            print("Image saved successfully.")

if __name__ == "__main__":
    app = MarsRoverPhotoViewer()
    app.mainloop()
