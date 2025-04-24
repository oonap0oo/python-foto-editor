# This python code implements a simple photo editor
# this code is written for educational purposes
# in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# it uses the following external modules:
# numpy==2.2.5
# pillow==11.2.1

# import modules
from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageTk
import numpy as np
import sys
import os


class PythonPhotoEdit(Tk):
    def __init__(self):
        self.print_enviroment_info()
        
        super().__init__()
        
        # settings window
        self.title("Python Photo Editor")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # instance variable
        self.path_original_image = None
        self.image_original = None
        self.image_original_small = None
        self.image_contrast_mask = None
        self.image_modified = None
        self.image_tk = None
        self.width_small_image = 900
        self.height_small_image = 500
        self.color_background = "#303030"
        self.color_foreground = "#E0E0E0"
        self.menu_font = ("FreeSans", 10, "bold")
        self.widget_font = ("FreeSans", 10, "bold")
        self.scale_length = 200

        # ttk styles
        ttk.Style().configure("TFrame", 
            background = self.color_background, 
            foreground = self.color_foreground)
        ttk.Style().configure("TLabel",
            font = self.widget_font, 
            background = self.color_background, 
            foreground = self.color_foreground)
        ttk.Style().configure("TButton", 
            font = self.widget_font, 
            background = self.color_background, 
            foreground = self.color_foreground)
        ttk.Style().configure("TScale", 
            font = self.widget_font, 
            background = self.color_background, 
            foreground = self.color_foreground)
        ttk.Style().configure("TNotebook", 
            font = self.widget_font, 
            background = self.color_background, 
            foreground = self.color_foreground)
        ttk.Style().configure("TNotebook.Tab", 
            font = self.widget_font, 
            background = self.color_background, 
            foreground = self.color_foreground)

        #ttk frame which covers Tk window
        self.mainframe=ttk.Frame(self, padding = 10)
        self.mainframe.grid(row=0,column=0 , sticky = "WENS")
        self.mainframe.columnconfigure(0, weight = 1)
        self.mainframe.columnconfigure(1, weight = 0)
        for row in range(10):
            self.mainframe.rowconfigure(row, weight = 0)
        
        # tkinter instance variables 
        self.blur_radius_ratio_image_size = DoubleVar()
        self.factor_alpha = DoubleVar()
        self.factor_saturation = DoubleVar()
        self.factor_contrast = DoubleVar()
        self.factor_brightness= DoubleVar()
        self.color_balance_blue_yellow = DoubleVar()
        self.color_balance_green_magenta = DoubleVar()
        self.initialise_tkinter_variables()
        
                
        # Tk and ttk widgets
        # v-canvas to show the photo
        self.canvas_image = Canvas(self.mainframe,
            width = self.width_small_image,
            height = self.height_small_image,
            bg = self.color_background)
        self.canvas_image.grid(row = 0, column = 0, rowspan = 4, sticky = "WENS", padx = (0, 10))
        # buttons for openening and saving photo
        self.button_open = ttk.Button(self.mainframe,
            text="Open",
            command = self.button_open_handler)
        self.button_open.grid(row = 0, column = 1, sticky = "WE", pady = 3)
        self.button_save = ttk.Button(self.mainframe,
            text="Save",
            command = self.button_save_handler)
        self.button_save.grid(row = 1, column = 1, sticky = "WE", pady = 3)
        
        # the other widgets are contained in two tabs
        self.tabcontrol = ttk.Notebook(self.mainframe, padding = (0, 10, 0, 0))
        self.frame_tab_1 = ttk.Frame(self.tabcontrol) # each tab has a frame
        self.frame_tab_2 = ttk.Frame(self.tabcontrol)
        self.tabcontrol.add(self.frame_tab_1, text = "Sett. 1")
        self.tabcontrol.add(self.frame_tab_2, text = "Sett. 2")
        self.tabcontrol.grid(row = 3, column = 1, sticky = "WENS")
        
        # widgets of first tab
        # color balance settings
        self.label_color_balance = ttk.Label(self.frame_tab_1,
            text = "Color balance")
        self.label_color_balance.grid(row = 0, column = 0, sticky = "WE", pady = (15, 3), padx = 10)
        self.scale_blue_yellow = Scale(self.frame_tab_1, 
            variable = self.color_balance_blue_yellow,
            bg = self.color_background,
            fg = self.color_foreground,
            from_ = -0.5, to = 0.5, 
            orient = HORIZONTAL,
            label="Blue - Yellow", 
            length = self.scale_length, 
            tickinterval = 0.25, 
            resolution = 0.01,
            command = self.scale_blue_yellow_handler)
        self.scale_blue_yellow.grid(row = 1, column = 0, sticky = "WE", pady = 3)
        self.scale_green_magenta = Scale(self.frame_tab_1, 
            variable = self.color_balance_green_magenta,
            bg = self.color_background,
            fg = self.color_foreground,
            from_ = -0.5, to = 0.5, 
            orient = HORIZONTAL,
            label="Green - Magenta", 
            length = self.scale_length, 
            tickinterval = 0.25, 
            resolution = 0.01,
            command = self.scale_green_magenta_handler)
        self.scale_green_magenta.grid(row = 2, column = 0, sticky = "WE", pady = 3)
        
        # contrast mask settings
        self.label_contrast_mask = ttk.Label(self.frame_tab_1,
            text = "Contrast mask")
        self.label_contrast_mask.grid(row = 3, column = 0, sticky = "WE",  pady = (15, 3), padx = 10)
        self.scale_strength = Scale(self.frame_tab_1, 
            variable = self.factor_alpha,
            bg = self.color_background,
            fg = self.color_foreground,
            from_ = 0.0, to = 1.0, 
            orient = HORIZONTAL,
            label="Strength", 
            length = self.scale_length, 
            tickinterval = 0.25, 
            resolution = 0.01,
            command = self.scale_strength_handler)
        self.scale_strength.grid(row = 4, column = 00, sticky = "WE", pady = 3)
        self.scale_radius_ratio = Scale(self.frame_tab_1, 
            variable = self.blur_radius_ratio_image_size,
            bg = self.color_background,
            fg = self.color_foreground,
            from_ = 0, to = 0.2, 
            orient = HORIZONTAL,
            label="Radius", 
            length = self.scale_length, 
            tickinterval = 0.1, 
            resolution = 0.01,
            command = self.scale_radius_ratio_handler)
        self.scale_radius_ratio.grid(row = 5, column = 0, sticky = "WE", pady = 3)
        
        # widgets of second tab
        # adjustemnts saturation, contast and brightness
        self.label_adjustments = ttk.Label(self.frame_tab_2,
            text = "Adjustments")
        self.label_adjustments.grid(row = 0, column = 0, sticky = "WE",  pady = (15, 3), padx = 10)
        self.scale_saturation = Scale(self.frame_tab_2, 
            variable = self.factor_saturation,
            bg = self.color_background,
            fg = self.color_foreground,
            from_ = 0, to = 2, 
            orient = HORIZONTAL,
            label="Saturation", 
            length = self.scale_length, 
            tickinterval = 0.5, 
            resolution = 0.05,
            command = self.scale_saturation_handler)
        self.scale_saturation.grid(row = 1, column = 0, sticky = "WE", pady = 3)
        self.scale_contrast = Scale(self.frame_tab_2, 
            variable = self.factor_contrast,
            bg = self.color_background,
            fg = self.color_foreground,
            from_ = 0.5, to = 2, 
            orient = HORIZONTAL,
            label="Contrast", 
            length = self.scale_length, 
            tickinterval = 0.5, 
            resolution = 0.05,
            command = self.scale_contrast_handler)
        self.scale_contrast.grid(row = 2, column = 0, sticky = "WE", pady = 3)
        self.scale_brightness = Scale(self.frame_tab_2, 
            variable = self.factor_brightness,
            bg = self.color_background,
            fg = self.color_foreground,
            from_ = 0.5, to = 2, 
            orient = HORIZONTAL,
            label="Brightness", 
            length = self.scale_length, 
            tickinterval = 0.5, 
            resolution = 0.05,
            command = self.scale_brightness_handler)
        self.scale_brightness.grid(row = 3, column = 0, sticky = "WE", pady = 3)
        
        # defime menus
        self.menubar = Menu(self,background = self.color_background,
            foreground = self.color_foreground, 
            font = self.menu_font)
        self.menufile = Menu(self.menubar,
            tearoff = 0,
            background = self.color_background, 
            foreground = self.color_foreground,
            font = self.menu_font)
        self.menufile.add_command(label = "Open", command = self.button_open_handler)
        self.menufile.add_command(label = "Save", command = self.button_save_handler)
        self.menufile.add_separator()
        self.menufile.add_command(label = "Exit", command = self.destroy)
        self.menubar.add_cascade(label="File", menu = self.menufile)
        self.menuedit = Menu(self.menubar,
            tearoff = 0,
            background = self.color_background, 
            foreground = self.color_foreground,
            font = self.menu_font)
        self.menuedit.add_command(label = "Reset settings", command = self.menu_reset_settings_handler)
        self.menubar.add_cascade(label="Edit", menu = self.menuedit)
        self.config(menu = self.menubar) 
        
    # at start show which python interpreter is running etc.
    def print_enviroment_info(self):
        print("Python executable: ", sys.executable)
        print("Python version: ", sys.version)
        print("sys.path:")
        for item in sys.path:
            print("\t" + item)
        print("Installed packages:")
        stream = os.popen("pip list")
        pip_list = stream.read()
        print(pip_list)
        
    # reset the tkinter variables to default        
    def initialise_tkinter_variables(self):
        self.blur_radius_ratio_image_size.set(0.025)
        self.factor_alpha.set(0.0)
        self.factor_saturation.set(1.0)
        self.factor_contrast.set(1.0)
        self.factor_brightness.set(1.0)
        self.color_balance_blue_yellow.set(0.0)
        self.color_balance_green_magenta.set(0.0)

    
    
    def button_open_handler(self):
        print("open")
        file_path = filedialog.askopenfilename(title="Open an image file", 
            filetypes=[("JPG files", "*.jpg *.jpeg"), ("TIFF files", "*.tif *.tiff"), ("All files", "*.*")])
        if file_path:
            self.path_original_image = file_path
            print(file_path)
            self.image_original = self.open_image_file(self.path_original_image)
            self.image_original_small = self.generate_small_image(self.image_original)
            self.perform_all_operations(self.image_original_small)
            self.update_canvas(self.image_modified)
            print(self.image_modified.size)

            
    def button_save_handler(self):
        if self.image_original_small == None: return
        print("save")
        path_parts = self.path_original_image.split(".")
        path_modified_image = path_parts[0] + "_mod.jpg" # prepare path for modified image file
        file_path = filedialog.asksaveasfilename(initialfile = path_modified_image,
            defaultextension=".jpg",
            filetypes=[("JPG files", "*.jpg")])
        if file_path:
            self.save_image_to_jpg_file(file_path)

    def scale_blue_yellow_handler(self, value):
        if self.image_original_small == None: return            
        self.perform_all_operations(self.image_original_small)
        self.update_canvas(self.image_modified)
        
    
    def scale_green_magenta_handler(self, value):
        if self.image_original_small == None: return            
        self.perform_all_operations(self.image_original_small)
        self.update_canvas(self.image_modified)
    
        
    def scale_strength_handler(self, value):
        if self.image_original_small == None: return            
        self.perform_all_operations(self.image_original_small)
        self.update_canvas(self.image_modified)
        
    def scale_radius_ratio_handler(self, value):
        if self.image_original_small == None: return            
        self.perform_all_operations(self.image_original_small)
        self.update_canvas(self.image_modified)
        
    def scale_saturation_handler(self, value):
        if self.image_original_small == None: return 
        self.perform_all_operations(self.image_original_small)
        self.update_canvas(self.image_modified)
        
    def scale_contrast_handler(self, value):
        if self.image_original_small == None: return 
        self.perform_all_operations(self.image_original_small)
        self.update_canvas(self.image_modified)

    def scale_brightness_handler(self, value):
        if self.image_original_small == None: return 
        self.perform_all_operations(self.image_original_small)
        self.update_canvas(self.image_modified)
        
    def menu_reset_settings_handler(self):
        if self.image_original_small == None: return
        self.initialise_tkinter_variables() 
        self.perform_all_operations(self.image_original_small)
        self.update_canvas(self.image_modified)
        
        
    def update_canvas(self, base_image):
        self.image_tk = ImageTk.PhotoImage(base_image)
        self.canvas_image.delete('all')
        self.canvas_image.create_image(1, 1, anchor = NW, image = self.image_tk)
        
    def open_image_file(self, path):    
        image_from_file = Image.open(path) # open the image file and create image object
        ImageOps.exif_transpose(image_from_file, in_place = True) # apply EXIF orientation if necessary
        return(image_from_file)
        
    def save_image_to_jpg_file(self, path):  
        self.perform_all_operations(self.image_original)
        try:
            self.image_modified.save(path, format='JPEG', quality = 90, subsampling = 0)
        except OSError:
            print(f"Error: could not save {path}")
        else:
            print(f"{path} was saved")

        
    def generate_small_image(self, base_image):
        # generating small version of image for viewing
        self.height_small_image = self.canvas_image.winfo_height()
        self.width_small_image = self.canvas_image.winfo_width()
        width_base_image = base_image.size[0]
        height_base_image = base_image.size[1]
        factor_scale_from_width = self.width_small_image / width_base_image
        factor_scale_from_height = self.height_small_image / height_base_image
        if factor_scale_from_width < factor_scale_from_height:
            factor_scale = factor_scale_from_width
        else:
            factor_scale = factor_scale_from_height
        
        image_small = ImageOps.scale(base_image, factor_scale)
        return(image_small)
        
    def generate_contrast_map(self, base_image, blur_radius_ratio):
        blur_radius = base_image.size[0] * self.blur_radius_ratio_image_size.get()
        contrast_mask = base_image.filter( ImageFilter.GaussianBlur(radius = blur_radius) )
        contrast_mask = ImageOps.invert(contrast_mask)
        contrast_mask = ImageOps.grayscale(contrast_mask) # make the contrast map grayscale
        contrast_mask = contrast_mask.convert("RGB") # needs to be RGB mode as the original for the blend function
        return(contrast_mask)

    def blend_overlay_images(self, base_image, top_image, alpha):
        # this functions calculates the values for the "overlay" blend mode
        def blend_overlay(a, b, alpha):
            b = 0.5 * (1 - alpha) + alpha * b
            result = 2 * a * b * (a < 0.5)
            result +=  (1 - 2 * (1 - a) * (1 - b)) * (a >= 0.5)
            return(result)
        # generating numpy arrays from the Pillow image objects, normalising all values to float64 between 0.0 and 1.0    
        base_image_numpy = np.asarray(base_image).astype(np.float64) / 255.0
        top_image_numpy = np.asarray(top_image).astype(np.float64) / 255.0
        # using the "overlay" blend mode on original image with the contrast mask
        image_blended_numpy = blend_overlay(base_image_numpy, top_image_numpy, alpha)
        # converting the resulting numpy array from float64 to unsigned integer 8 bit
        image_blended_numpy = (image_blended_numpy * 255).astype(np.uint8)
        # generating a Pillow image from the numpy array, facilitates saving as image file
        image_blended = Image.fromarray(image_blended_numpy)
        return(image_blended)
        
    def adjust_color_balace_image(self, base_image, blue_yellow, green_magenta):
        # generating numpy arrays from the Pillow image objects, normalising all values to float64 between 0.0 and 1.0    
        base_image_numpy = np.asarray(base_image).astype(np.float64) / 255.0
        
        image_adjusted_numpy = np.zeros(base_image_numpy.shape)
        # red channel
        image_adjusted_numpy[:,:,0] = base_image_numpy[:,:,0] 
        # green channel
        image_adjusted_numpy[:,:,1] = base_image_numpy[:,:,1] * (1 - green_magenta)
        # blue channel
        image_adjusted_numpy[:,:,2] = base_image_numpy[:,:,2] * ( 1 - blue_yellow) 
        # scale back to 0.0 - 1.0
        image_adjusted_numpy /= np.max(image_adjusted_numpy)
        
        # converting the resulting numpy array from float64 to unsigned integer 8 bit
        image_adjusted_numpy = (image_adjusted_numpy * 255).astype(np.uint8)
        # generating a Pillow image from the numpy array, facilitates saving as image file
        image_adjusted = Image.fromarray(image_adjusted_numpy)
        return(image_adjusted)
        
        
    def enchance_image(self, base_image, brightness, contrast, saturation):
        enhancer = ImageEnhance.Brightness(base_image)
        image_enchanced = enhancer.enhance(brightness)
        enhancer = ImageEnhance.Color(image_enchanced)
        image_enchanced = enhancer.enhance(saturation)
        enhancer = ImageEnhance.Contrast(image_enchanced)
        image_enchanced = enhancer.enhance(contrast)
        return(image_enchanced)
        
    def perform_all_operations(self, base_image):
        blur_radius_ratio = self.blur_radius_ratio_image_size.get()
        alpha = self.factor_alpha.get()
        brightness = self.factor_brightness.get()
        contrast = self.factor_contrast.get()
        saturation = self.factor_saturation.get()
        blue_yellow = self.color_balance_blue_yellow.get()
        green_magenta = self.color_balance_green_magenta.get()
        
        # adjust color balance
        self.image_modified = self.adjust_color_balace_image(base_image, blue_yellow, green_magenta) 
        
        # generate a contrast map
        self.image_contrast_mask = self.generate_contrast_map(self.image_modified, blur_radius_ratio)
        
        # blend contrastmap and original image after color balance
        self.image_modified = self.blend_overlay_images(self.image_modified, self.image_contrast_mask, alpha)

        # enchancing modified image
        self.image_modified = self.enchance_image(self.image_modified, brightness, contrast, saturation)
    
        
    
pythonphotoedit = PythonPhotoEdit()
pythonphotoedit.mainloop()
