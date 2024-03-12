import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io
from tkcalendar import DateEntry

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
        
        # Configure background color
        self.configure(bg="#D2B48C")  # Sand color
        
        # Create frame
        main_frame = tk.Frame(self, bg="#D2B48C")  # Sand color
        main_frame.pack(expand=True, fill="both", anchor="center")
        
        # Outer border
        outer_border = ttk.LabelFrame(main_frame, text='Photos', style="Outer.TLabelframe")
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
        self.date_entry.bind("<<DateEntrySelected>>", self.on_date_selected)
        
        # Rover selection
        rover_label = ttk.Label(outer_border, text="Select Rover:", style="Label.TLabel")
        rover_label.pack(anchor="center", padx=10, pady=(5, 0))
        
        self.rover_combobox = ttk.Combobox(outer_border, values=[], style="ComboboxRover.TCombobox")
        self.rover_combobox.pack(anchor="center", padx=10, pady=(0, 5))
        self.rover_combobox.bind("<<ComboboxSelected>>", self.on_update_camera_options)
        
        # Camera selection
        camera_label = ttk.Label(outer_border, text="Select Camera:", style="Label.TLabel")
        camera_label.pack(anchor="center", padx=10, pady=(5, 0))
        
        self.camera_combobox = ttk.Combobox(outer_border, values=[], style="ComboboxCamera.TCombobox")
        self.camera_combobox.pack(anchor="center", padx=10, pady=(0, 5))
        
        # Fetch button
        fetch_button = ttk.Button(outer_border, text="Fetch Photos", command=self.on_fetch_photos_clicked, style="Fetch.TButton")
        fetch_button.pack(anchor="center", padx=10, pady=(5, 0))
        
        # Navigation buttons
        nav_frame = ttk.Frame(outer_border, style="Nav.TFrame")
        nav_frame.pack(anchor="center", pady=(10, 5))
        
        prev_button = ttk.Button(nav_frame, text="Previous", command=self.prev_photo, style="Nav.TButton")
        prev_button.pack(side="left", padx=(0, 5))
        
        next_button = ttk.Button(nav_frame, text="Next", command=self.next_photo, style="Nav.TButton")
        next_button.pack(side="left")
        
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
        self.style.configure("Photo.TLabel", background="#000000")  # Photo label: black background
        self.style.configure("Info.TLabel", background="#000000", foreground="#D2B48C")  # Information label: black background, sand color text
        
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

    def on_update_camera_options(self, event):
        selected_rover = self.rover_combobox.get()
        if selected_rover == "all":
            self.camera_combobox.config(values=["all"])
        else:
            available_cameras = self.get_available_cameras(selected_rover, self.date_entry.get())
            self.camera_combobox.config(values=available_cameras)
        self.camera_combobox.set("all")
        
    def on_date_selected(self, event):
        selected_rover = self.rover_combobox.get()
        if selected_rover != "all":
            available_cameras = self.get_available_cameras(selected_rover, self.date_entry.get())
            self.camera_combobox.config(values=available_cameras)
        self.camera_combobox.set("all")
        
    def get_available_cameras(self, rover, date):
        available_cameras = []
        for camera in ["FHAZ", "RHAZ", "NAVCAM", "MAST", "CHEMCAM", "MAHLI", "MARDI", "PANCAM", "MINITES"]:
            photos = self.fetch_photos(rover, date, camera)
            if photos:
                available_cameras.append(camera)
        return available_cameras

if __name__ == "__main__":
    app = MarsRoverPhotoViewer()
    app.mainloop()
