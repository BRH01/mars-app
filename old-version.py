import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io
from tkcalendar import DateEntry

# Function to fetch Mars rover photos based on sol
def fetch_photos(api_key, rover, sol, camera="all", page=1):
    url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos"
    params = {
        "api_key": api_key,
        "earth_date": sol,
        "camera": camera,
        "page": page
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["photos"] if "photos" in data else []

# Function to display photos in GUI
def display_photos(photos):
    global photo_index
    photo_index = 0  # Reset photo index
    show_photo(photo_index)  # Show the first photo
    update_nav_buttons()  # Enable/disable navigation buttons as needed

# Function to show a single photo
def show_photo(index):
    global current_photos
    current_photos = photos
    photo = current_photos[index]
    img_url = photo["img_src"]
    img_response = requests.get(img_url)
    img_data = img_response.content
    img = Image.open(io.BytesIO(img_data))
    
    # Calculate the maximum size for the displayed image
    max_width = root.winfo_screenwidth() - 200
    max_height = root.winfo_screenheight() - 200
    
    # Resize the image if it's too large
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height))
    
    photo_img = ImageTk.PhotoImage(img)
    photo_label.config(image=photo_img)
    photo_label.photo = photo_img  # Keep reference to avoid garbage collection
    
    # Update navigation buttons
    update_nav_buttons()

# Function to handle previous button click
def prev_photo():
    global photo_index
    if photo_index > 0:
        photo_index -= 1
        show_photo(photo_index)

# Function to handle next button click
def next_photo():
    global photo_index
    if photo_index < len(current_photos) - 1:
        photo_index += 1
        show_photo(photo_index)

# Function to handle fetch button click
# Function to fetch Mars rover photos based on sol
def fetch_photos(api_key, rover, sol, camera="all", page=1):
    url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos"
    params = {
        "api_key": api_key,
        "earth_date": sol,
        "camera": camera,
        "page": page
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["photos"] if "photos" in data else []

# Function to display photos in GUI
def display_photos(photos):
    global photo_index
    photo_index = 0  # Reset photo index
    show_photo(photo_index)  # Show the first photo
    num_photos_label.config(text=f"Total photos: {len(photos)}")
    update_nav_buttons()  # Enable/disable navigation buttons as needed

# Function to handle fetch button click
def fetch_photos_clicked():
    global photos
    selected_date = date_entry.get_date().isoformat()
    selected_rover = rover_combobox.get()
    selected_camera = camera_combobox.get()
    photos = fetch_photos(api_key, selected_rover, selected_date, selected_camera)
    
    if not photos:
        photo_label.config(text="No images available")
        num_photos_label.config(text="")
        prev_button.config(state=tk.DISABLED)
        next_button.config(state=tk.DISABLED)
    else:
        display_photos(photos)

# Function to update navigation buttons state
def update_nav_buttons():
    if not current_photos:
        return
    prev_button.config(state=tk.NORMAL if photo_index > 0 else tk.DISABLED)
    next_button.config(state=tk.NORMAL if photo_index < len(current_photos) - 1 else tk.DISABLED)

# Main function
def main():
    global api_key
    global root
    global date_entry
    global rover_combobox
    global camera_combobox
    global photo_label
    global num_photos_label
    global photo_index
    global photos
    
    # Set up GUI
    root = tk.Tk()
    root.title("Mars Rover Photo Viewer")
    
    # API key
    api_key = "oWFaTJ9QHR0MGxjmsKUFNehxWWzo7mmTbeQXfLUQ"  # Your API key
    
    # Date selection
    date_label = ttk.Label(root, text="Select Date:")
    date_label.pack()
    date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
    date_entry.pack(padx=10, pady=10)
    
    # Rover selection
    rover_label = ttk.Label(root, text="Select Rover:")
    rover_label.pack()
    rovers = ["curiosity", "opportunity", "spirit"]
    rover_combobox = ttk.Combobox(root, values=rovers)
    rover_combobox.pack()
    rover_combobox.current(0)  # Select the first rover by default
    rover_combobox.bind("<<ComboboxSelected>>", update_camera_options)  # Update camera options
    
    # Camera selection
    camera_label = ttk.Label(root, text="Select Camera:")
    camera_label.pack()
    cameras = ["FHAZ", "RHAZ", "NAVCAM", "MAST", "CHEMCAM", "MAHLI", "MARDI", "PANCAM", "MINITES"]
    camera_combobox = ttk.Combobox(root, values=cameras)
    camera_combobox.pack()
    camera_combobox.current(0)  # Select the first camera by default
    
    # Fetch button
    fetch_button = ttk.Button(root, text="Fetch Photos", command=fetch_photos_clicked)
    fetch_button.pack(pady=10)
    
    # Frame to hold photo and scrollbars
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Canvas for scrolling
    canvas = tk.Canvas(frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Scrollbars
    v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    h_scrollbar = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # Frame to hold the image
    img_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=img_frame, anchor=tk.NW)
    
    # Photo label
    global photo_label
    photo_label = tk.Label(img_frame)
    photo_label.pack()
    
    # Navigation buttons
    nav_frame = ttk.Frame(root)
    nav_frame.pack(pady=10)
    prev_button = ttk.Button(nav_frame, text="Previous", command=prev_photo, state=tk.DISABLED)
    prev_button.pack(side=tk.LEFT, padx=5)
    next_button = ttk.Button(nav_frame, text="Next", command=next_photo, state=tk.DISABLED)
    next_button.pack(side=tk.LEFT, padx=5)
    
    # Label to display number of photos
    global num_photos_label
    num_photos_label = ttk.Label(root)
    num_photos_label.pack()
    
    # Initialize variables
    photo_index = 0
    photos = []
    
    # Run the GUI
    root.mainloop()

# Function to update camera options based on selected rover
def update_camera_options(event):
    selected_rover = rover_combobox.get()
    cameras = []
    if selected_rover == "curiosity":
        cameras = ["FHAZ", "RHAZ", "NAVCAM", "MAST", "CHEMCAM", "MAHLI", "MARDI", "PANCAM", "MINITES"]
    elif selected_rover == "opportunity":
        cameras = ["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"]
    elif selected_rover == "spirit":
        cameras = ["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"]
    camera_combobox.config(values=cameras)
    camera_combobox.current(0)  # Select the first camera by default

if __name__ == "__main__":
    main()
