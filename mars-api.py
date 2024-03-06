import requests
import wx
import wx.adv
from PIL import Image, ImageTk
import io

class MarsRoverPhotoViewer(wx.Frame):
    def __init__(self, *args, **kw):
        super(MarsRoverPhotoViewer, self).__init__(*args, **kw)
        
        self.api_key = "oWFaTJ9QHR0MGxjmsKUFNehxWWzo7mmTbeQXfLUQ"
        self.photos = []
        self.current_photos = []
        self.photo_index = 0
        
        self.InitUI()
        
    def InitUI(self):
        pnl = wx.Panel(self)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Date selection
        date_label = wx.StaticText(pnl, label="Select Date:")
        sizer.Add(date_label, 0, wx.ALL, 5)
        
        self.date_entry = wx.adv.DatePickerCtrl(pnl, style=wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY)
        sizer.Add(self.date_entry, 0, wx.ALL, 5)
        
        # Rover selection
        rover_label = wx.StaticText(pnl, label="Select Rover:")
        sizer.Add(rover_label, 0, wx.ALL, 5)
        
        self.rover_combobox = wx.ComboBox(pnl, choices=["curiosity", "opportunity", "spirit"])
        sizer.Add(self.rover_combobox, 0, wx.ALL, 5)
        self.rover_combobox.Bind(wx.EVT_COMBOBOX, self.OnUpdateCameraOptions)
        
        # Camera selection
        camera_label = wx.StaticText(pnl, label="Select Camera:")
        sizer.Add(camera_label, 0, wx.ALL, 5)
        
        self.camera_combobox = wx.ComboBox(pnl, choices=["FHAZ", "RHAZ", "NAVCAM", "MAST", "CHEMCAM", "MAHLI", "MARDI", "PANCAM", "MINITES"])
        sizer.Add(self.camera_combobox, 0, wx.ALL, 5)
        
        # Fetch button
        fetch_button = wx.Button(pnl, label="Fetch Photos")
        fetch_button.Bind(wx.EVT_BUTTON, self.OnFetchPhotosClicked)
        sizer.Add(fetch_button, 0, wx.ALL, 5)
        
        # Photo display
        self.photo_label = wx.StaticBitmap(pnl)
        sizer.Add(self.photo_label, 0, wx.ALL|wx.EXPAND, 5)
        
        # Photo counter
        self.photo_counter_label = wx.StaticText(pnl, label="Total photos: ")
        sizer.Add(self.photo_counter_label, 0, wx.ALL, 5)
        
        pnl.SetSizer(sizer)
        
        self.Centre()
        self.Show(True)
        
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
            self.photo_label.SetLabel("No images available")
            self.photo_counter_label.SetLabel("")
            return
        
        self.photo_index = 0
        self.show_photo(self.photo_index)
        self.update_nav_buttons()

    def show_photo(self, index):
        self.current_photos = self.photos
        photo = self.current_photos[index]
        img_url = photo["img_src"]
        img_response = requests.get(img_url)
        img_data = img_response.content
        img = Image.open(io.BytesIO(img_data))
        
        max_width = self.GetSize()[0] - 100
        max_height = self.GetSize()[1] - 200
        
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height))
        
        img = wx.Image(img.size[0], img.size[1], img.tobytes())
        bmp = wx.Bitmap(img)
        
        self.photo_label.SetBitmap(bmp)
        
        self.update_nav_buttons()

    def prev_photo(self, event):
        if self.photo_index > 0:
            self.photo_index -= 1
            self.show_photo(self.photo_index)

    def next_photo(self, event):
        if self.photo_index < len(self.current_photos) - 1:
            self.photo_index += 1
            self.show_photo(self.photo_index)

    def OnFetchPhotosClicked(self, event):
        selected_date = self.date_entry.GetValue().FormatISODate()
        selected_rover = self.rover_combobox.GetValue()
        selected_camera = self.camera_combobox.GetValue()
        self.photos = self.fetch_photos(selected_rover, selected_date, selected_camera)
        
        self.display_photos()
        
    def update_nav_buttons(self, enable=True):
        prev_button = self.FindWindowById(wx.ID_ANY, "Previous")
        next_button = self.FindWindowById(wx.ID_ANY, "Next")
        
        if enable:
            prev_button.Enable() if self.photo_index > 0 else prev_button.Disable()
            next_button.Enable() if self.photo_index < len(self.current_photos) - 1 else next_button.Disable()
        else:
            prev_button.Disable()
            next_button.Disable()

    def OnUpdateCameraOptions(self, event):
        selected_rover = self.rover_combobox.GetValue()
        cameras = []
        if selected_rover == "curiosity":
            cameras = ["FHAZ", "RHAZ", "NAVCAM", "MAST", "CHEMCAM", "MAHLI", "MARDI", "PANCAM", "MINITES"]
        elif selected_rover == "opportunity" or selected_rover == "spirit":
            cameras = ["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"]
        self.camera_combobox.Set(cameras)
        self.camera_combobox.SetSelection(0)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MarsRoverPhotoViewer(None, title="Mars Rover Photo Viewer", size=(800, 600))
    app.MainLoop()
