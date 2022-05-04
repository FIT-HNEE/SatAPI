# Libraries
import rasterio
from landsatxplore.api import API
import json
from landsatxplore.earthexplorer import EarthExplorer
import ntpath
from osgeo import gdal
from pyproj import Proj, transform
from os import remove
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from rasterio.plot import adjust_band
from rasterio.plot import reshape_as_image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from rasterio.plot import show
import tkinter
from tkinter import *
from tkinter import Tk,Label, filedialog, ttk, Entry, Toplevel, StringVar, Menu
from tkcalendar import DateEntry


def open_file():
    """
    Create a string which is the path of a file.
    Returns
    -------
    path : String
    """
    global path
    file = filedialog.askopenfilename(initialdir ='/', title='Open File',
    filetype=(('TIFF files', '*.tif*'),('JP2 files', '*.jp2*'),('All files', '*.*')))
    path = file
    return path

def open_file_2():
    """
    Create a string which is the path of a file.
    Returns
    -------
    path_2 : String
    
    Note: A second function is created to open a file since some functions 
    require two different paths.
    """
    global path_2
    file = filedialog.askopenfilename(initialdir ='/', title='Open File',
    filetype=(('TIFF files', '*.tif*'),('JP2 files', '*.jp2*'),('All files', '*.*')))
    path_2 = file
    return path_2

def open_files():
    """
    Create a string which is the path of some files.
    Returns
    -------
    paths : String
    """
    global paths
    files = filedialog.askopenfilenames(initialdir ='/', title='Open Files',
    filetype=(('TIFF files', '*.tif*'),('JP2 files', '*.jp2*'),('All files', '*.*')))
    paths = files
    return paths

def save_file():
    """
    Create a string which is the path of a new file.
    Returns
    -------
    save_path : String
    """
    global save_path
    files_save = filedialog.asksaveasfilename(initialdir ='/', title='Save as...',
    filetype=(('TIFF files', '*.tif*'),('JP2 files', '*.jp2*'),('All files', '*.*')))
    save_path = files_save
    return save_path

def directory():
    """
    Create a string which is the path of a folder.
    Returns
    -------
    save_dir : String
    """
    global save_dir
    files_save = filedialog.askdirectory()
    save_dir = files_save
    return save_dir


def get_info():
    """
    With this function a window is created in which the user data and 
    the reference raster are entered to be able to search for scenes and later 
    download them.
    """
    
    # Window configuration.
    searchWin = Toplevel(root)
    searchWin.title('Search')
    searchWin.geometry('600x450')
    
    # Global variables of type String which are used in different functions.
    global userName, password, entryUser, entryPass
    
    # New variables of type StringVar are created which are necessary to handle
    # widget inputs more effectively.
    userName1 = StringVar()
    password1 = StringVar()
    
    # Label and entry type objects are created to display them in the interface.
    labelUser = Label(searchWin, text='User Name')
    labelUser.grid(row=1,column=1,padx=50,pady=5,columnspan=2)
    entryUser = Entry(searchWin, textvariable = userName1)
    entryUser.grid(row=2,column=1,padx=25,pady=5,columnspan=2)
    labelPass = Label(searchWin, text='Password')
    labelPass.grid(row=3,column=1,padx=25,pady=5,columnspan=2)
    entryPass = Entry(searchWin, textvariable = password1, show='*')
    entryPass.grid(row=4,column=1,padx=25,pady=5,columnspan=2)
    labelPass = Label(searchWin, text='Search from:')
    labelPass.grid(row=6,column=1,padx=25,pady=5,columnspan=2)
    
    # Global variables of type String which are used in different functions.
    global date1, date2
    # Two Tkinter calendar type objects are created, which are used to define the
    # search dates
    cal=DateEntry(searchWin,selectmode='day')
    cal.grid(row=7,column=1,padx=25,pady=5,ipadx=50)
    cal2=DateEntry(searchWin,selectmode='day')
    cal2.grid(row=7,column=2,padx=25,pady=5,ipadx=50)
    
    # Global variables of type String which are used in different functions.
    global lat1, long1, lat2, long2
    # Label and entry type objects are created to display them in the interface.
    labelPass = Label(searchWin, text='Reference coordinates:')
    labelPass.grid(row=8,column=1,padx=25,pady=5,columnspan=2)
    button = Button(searchWin, text="Open reference Raster",command = open_file)
    button.grid(row=9,column=1,padx=25,pady=5,columnspan=2)
    
    def download():
        """
        With this function a new window is created, once you have the user data
        and the reference raster, you can perform the scene search and select
        the scene you want to download.
        
        Note: In order to download, the earthexplorer library was modified.
        """
        
        # Window configuration.
        downWin = Toplevel(searchWin)
        downWin.title('Download')
        downWin.geometry('1500x250')
        
        # The username and password that the user entered are obtained.
        userName = entryUser.get()
        password = entryPass.get()
        
        # The dates selected by the user are converted to strings.
        date1 = cal.get_date().strftime("%Y-%m-%d")
        date2 = cal2.get_date().strftime("%Y-%m-%d")
        
        # An API type object is created to be able to search for scenes, the
        # parameters that are entered in object are the user and the password.
        # Example
        # User: JymEmmanuel
        # Password: J1M3MM4NU31C0C0T1314R4#
        api = API(userName, password)
        
        # The path of the reference raster is opened to obtain the minimum and
        # maximum coordinates
        my_file = rasterio.open(path)
        bounbox = my_file.bounds
        
        # The minimum and maximum coordinates are assigned to minimum and maximum
        # latitude and longitude as appropriate.
        lat_min = bounbox[1]
        lon_min = bounbox[2]
        lat_max = bounbox[3]
        lon_max = bounbox[0]
        
        # With the previously established parameters, the scene search is performed.
        scenes = api.search(
        dataset='sentinel_2a',
        bbox=(lon_min,lat_min,lon_max,lat_max),
        start_date = date1,
        end_date = date2,
        max_cloud_cover=10
        )
        
        # Process the result
        for scene in scenes:
            print(scene['acquisition_date'])
            # Write scene footprints to disk
            fname = f"{scene['sentinel_entity_id']}.geojson"
            with open(fname, "w") as f:
                json.dump(scene['spatial_bounds'], f)        
                
        # Some empty lists are created.
        display_id = []
        cloud_cover = []
        center_latitude_dec = []
        center_longitude_dec = []
        production_date = []
        publish_date = []
        platform = []
        epsg_code = []
        
        # The values ​​of the scenes are added to the lists as appropriate.
        for i in scenes:
            for z in i:
                if z=='display_id':
                    display_id.append(i[z])
                if z =='cloud_cover':
                    cloud_cover.append(i[z])
                if z =='center_latitude_dec':
                    center_latitude_dec.append(i[z])
                if z =='center_longitude_dec':
                    center_longitude_dec.append(i[z])
                if z =='production_date':
                    production_date.append(i[z])
                if z =='publish_date':
                    publish_date.append(i[z])
                if z =='platform':
                    platform.append(i[z])
                if z =='epsg_code':
                    epsg_code.append(i[z])
        
        # Total scenes found
        total = len(scenes)
        
        # A table is created in which we set the names of each column.
        tv = ttk.Treeview(downWin, columns=(1, 2, 3, 4, 5, 6, 7, 8), show='headings', height=8)
        tv.pack()
        tv.heading(1, text="display id")
        tv.heading(2, text="cloud cover")
        tv.heading(3, text="center latitude")
        tv.heading(4, text="center longitude")
        tv.heading(5, text="production date")
        tv.heading(6, text="publish date")
        tv.heading(7, text="platform")
        tv.heading(8, text="epsg code")
        
        # The value of each scene is added to the corresponding column
        for i in range(0, total):
            tv.insert(parent='', index=i, iid=i, values=(display_id[i], cloud_cover[i],
            center_latitude_dec[i],center_longitude_dec[i],production_date[i],publish_date[i]
            ,platform[i],epsg_code[i]))
        
        def download_Raster():
            """
            With this function the selected scene of interest is downloaded.
            """
            
            # Select the directory where you want to download the file.
            directory()
            ee = EarthExplorer(userName,password)
            selected = tv.focus()
            temp = tv.item(selected, 'values')
            ee.download(temp[0], output_dir=save_dir)
        
        # The download button and the table where the scenes are shown are shown
        Button(downWin, text='Download', command=download_Raster).pack()
        style = ttk.Style()
        style.theme_use("default")
        style.map("Treeview")
        
        
    # The button to search for scenes is displayed.
    button = Button(searchWin, text="Search",command = download)
    button.grid(row=11,column=1,padx=25,pady=5,columnspan=2)
    
def stack():
    """
    With this function you can perform a stacking of the raster files that are
    required and in the order that you want.
    """
    # Window configuration
    stackWin = Toplevel(root)
    stackWin.title('Stack Images')
    stackWin.geometry('650x350')
    
    def open_rasters():
        """
        With this function, the path of the different files is obtained to later
        order them as an array.
        """
        open_files()
        paths1 = []
        
        # The names of the open files are shown as well as their paths.
        for i in range(0, len(paths)):
            paths1.append((f'{i+1}', paths[i], ntpath.basename(paths[i])))
        for path1 in paths1:
             tree.insert('', tkinter.END, values=path1)
     
    def stack_rasters():
        """
        Once you have the array with the paths of the files to be stacked, 
        you can stack the Raster images.
        """
        
        # Path where you want to save the file
        save_file()
        # A list is created which contains the paths of the files.
        paths2 = list(paths)
        # An auxiliary file is created to be able to perform the stacking.
        outvrt = './stacked.vrt'
        # The stacking of the images is done.
        outds = gdal.BuildVRT(outvrt, paths2, separate=True)
        outds = gdal.Translate(save_path, outds, creationOptions=['TILED:YES']) 
        # The data in the table is deleted
        tree.delete(*tree.get_children())
        # Auxiliary file is removed
        del outvrt
    
    # The button to open the images to be stacked is created and displayed.
    button = Button(stackWin, text="Open files",command=open_rasters)
    button.grid(row=1,column=1,padx=50,pady=5,columnspan=2)
    
    # The titles of the columns of the table are defined.
    columns = ('id', 'path', 'name')
    tree = ttk.Treeview(stackWin, columns=columns, show='headings')
    tree.heading('id', text='id')
    tree.heading('path', text='path')
    tree.heading('name', text='Name')
    
    # Table configuration.
    tree.grid(row=2, column=2, columnspan=5)
    
    # The button to Stack the images is created and displayed.
    button2 = Button(stackWin, text="Stack Raster",command=stack_rasters)
    button2.grid(row=3,column=1,padx=50,pady=5,columnspan=2)

def clip_big_raster():
    """
    With this function you can cut a raster with large dimensions so that it
    can be delimited to an area of ​​interest.
    """
    
    # Window configuration
    clipBkWin = Toplevel(root)
    clipBkWin.title('Clip Raster')
    clipBkWin.geometry('250x350')
    
    # Label and buttons type objects are created to display them in the interface.
    labelUser = Label(clipBkWin, text='Open Reference Raster')
    labelUser.grid(row=1,column=1,padx=50,pady=5,columnspan=2)
    button = Button(clipBkWin, text="Open...",command = open_file)
    button.grid(row=2,column=1,padx=25,pady=5,columnspan=2)
    labelUser = Label(clipBkWin, text='Open Raster to clip')
    labelUser.grid(row=3,column=1,padx=50,pady=5,columnspan=2)
    button = Button(clipBkWin, text="Open...",command = open_file_2)
    button.grid(row=4,column=1,padx=25,pady=5,columnspan=2)
   
    def clip_raster():
        """
        Once you have the file paths, you can cut the Raster of large dimensions
        based on a reference raster.
        """
        
        # Path where the file is saved
        save_file()
        
        # The reference file and the file that will be cut with the help of the 
        # rasterio library are opened.
        my_file = rasterio.open(path)
        my_file_2 = rasterio.open(path_2)
        
        # The minimum and maximum coordinates of the reference raster are obtained.
        bounbox = my_file.bounds
        
        # The minimum and maximum coordinates are assigned to minimum and maximum
        # latitude and longitude as appropriate.
        xmin = bounbox[2]
        ymin = bounbox[1]
        xmax = bounbox[0]
        ymax = bounbox[3]
        
        # The cartographic representations that the files have are obtained.
        proj_1 = str(my_file.crs)
        proj_2 = str(my_file_2.crs)
        inProj = Proj(init= proj_1)
        outProj = Proj(init= proj_2)
        
        # The minimum and maximum coordinates are transformed to be able to make the clip.
        x1,y1 = xmin,ymin
        x2,y2 = transform(inProj,outProj,x1,y1)
        x_1,y_1 = xmax, ymax
        x_2,y_2 = transform(inProj,outProj,x_1,y_1)
        window = (x_2,y_2,x2,y2)
        gdal.Translate(save_path, path_2, projWin = window)
    
    # Label and button type objects are created to display them in the interface.
    labelUser = Label(clipBkWin, text='Save clip')
    labelUser.grid(row=6,column=1,padx=50,pady=5,columnspan=2)
    button = Button(clipBkWin, text="Save...",command = clip_raster)
    button.grid(row=7,column=1,padx=25,pady=5,columnspan=2)

class Cursor:
    """
    A cursor in the form of a rectangle that spans the axes and moves each time 
    a click is made.
    
    Parameters
    ----------
    ax : `matplotlib.axes.Axes`
    """
    
    def __init__(self, ax):
        self.ax = ax
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')
        self.horizontal_line_2 = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line_2 = ax.axvline(color='k', lw=0.8, ls='--')
        self.text = ax.text(0.2, 1.02, '', transform=ax.transAxes)

    def set_rectangle_visible(self, visible):
        """
        Internal event handler to update the position of the rectangle.
        """
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.horizontal_line_2.set_visible(visible)
        self.vertical_line_2.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw
    
    def on_mouse_click(self, event):
        """
        Internal event handler to get the position on the X and Y axis of the mouse.

        Returns
        -------
        x : float64
            Is the X-axis position of the mouse.
        y : float64
            Is the Y-axis position of the mouse.
        """
        
        if event.inaxes:
            global x, y
            self.set_rectangle_visible(True)
            x, y = event.xdata, event.ydata
            # Update the rectangle positions
            self.horizontal_line.set_ydata(y-dim)
            self.vertical_line.set_xdata(x-dim)
            self.horizontal_line_2.set_ydata(y+dim)
            self.vertical_line_2.set_xdata(x+dim)
            # Coordinates are displayed in the frame.
            self.text.set_text('x= %1.9f, y= %1.9f' % (x, y))
            self.ax.figure.canvas.draw()
            # The coordinates are printed in the python console.
            print("x = %f y = %f"%(x,y))
        return x, y
   
def clip_two_raster():
    """
    With this function you can cut two rasters from the dimensions you want.
    """
    
    # Window configuration
    clipTwokWin = Toplevel(root)
    clipTwokWin.title('Clip Raster')
    clipTwokWin.geometry('250x350')
    
    # New variable of type StringVar is created.
    dim1 = StringVar()
    
    # Label and entry type objects are created to display them in the interface.
    labelUser = Label(clipTwokWin, text='Type clip dimention [pixels]')
    labelUser.grid(row=1,column=1,padx=50,pady=5,columnspan=2)
    entryDim = Entry(clipTwokWin, textvariable = dim1)
    entryDim.grid(row=2,column=1,padx=25,pady=5,columnspan=2)
    
    def act_dim_and_open():
        """
        Since you need to know the dimensions of the bounding box to cut, you 
        to update the value of the dimension, and since you don't want to place
        a special button for this action, this action is included when you open 
        the Raster file.

        Returns
        -------
        dim : float
            This value represents the dimension of the cut to be made.
        """
        global dim
        open_file()
        dim2 = entryDim.get()
        dim = int(dim2)*0.1
        dim = dim/2
        
        return dim
    
    # Labels and buttons type objects are created to display them in the interface.
    labelUser = Label(clipTwokWin, text='Reference Raster')
    labelUser.grid(row=4,column=1,padx=50,pady=5,columnspan=2)
    button = Button(clipTwokWin, text="Open...",command = act_dim_and_open)
    button.grid(row=5,column=1,padx=25,pady=5,columnspan=2)
    labelUser = Label(clipTwokWin, text='Satelital image to clip')
    labelUser.grid(row=6,column=1,padx=50,pady=5,columnspan=2)
    button2 = Button(clipTwokWin, text="Open...",command = open_file_2)
    button2.grid(row=7,column=1,padx=25,pady=5,columnspan=2)
    
    def cut_two_raster():
        """
        With this function the reference raster is opened and its resolution is
        reduced because if you use the original resolution, the program slows down
        too much, so the original image is reduced to 10 percent and this image
        is the one that is shown in the interface.
        """
        
        # Window configuration
        clipTworWin = Toplevel(root)
        clipTworWin.title('Clip two Raster')
        
        # The file paths obtained from the functions are matched with other variables.
        dataset1 = path
        dataset2 = path_2
        
        # This path is used to create an auxiliary file.
        dataset3 = 'output_10_por.tif'
        
        # Parameters used to change the image resolution to 10 percent.
        kwargs = {
            'widthPct': 10,
            'heightPct': 10,
        }
        # The resolution change is made.
        gdal.Translate(dataset3, dataset1, **kwargs)
        
        # Auxiliary file is opened.
        dataset = rasterio.open(dataset3)
        image = dataset.read()
        
        # Take the first three channels and restructure the array.
        rgb = image[0:3]
        rgb_norm = adjust_band(rgb)
        rgb_reshaped = reshape_as_image(rgb_norm)
        
        #Create a figure with axis to plot.
        fig = Figure()
        ax = fig.add_subplot()
        
        # Show the restructured image.
        ax.imshow(rgb_reshaped)
        
        # Put the fig inside the frame.
        canvas = FigureCanvasTkAgg(fig, master=clipTworWin)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        
        # Toolbar is added to frame
        toolbar = NavigationToolbar2Tk(canvas, clipTworWin)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        
        def cut_ras():
            """
            Once the coordinates of the reference rectangle are obtained, these
            coordinates are transformed into geographic coordinates which can be
            used to clip the satellite image and the UAV image.
            """
            
            # Path of the file to be saved
            save_file()
            
            # The coordinates of the rectangle are transformed and put in an array.
            xcutmin, ycutmin = dataset.transform * (x-dim, y-dim)
            xcutmax, ycutmax = dataset.transform * (x+dim, y+dim)
            window = (xcutmin,ycutmin,xcutmax,ycutmax)
            
            # The files to be clip are opened
            cut_file_1 = rasterio.open(dataset1)
            cut_file_2 = rasterio.open(dataset2)
            
            # The cartographic representations that the files have are obtained.
            proj_1 = str(cut_file_1.crs)
            proj_2 = str(cut_file_2.crs)
            inProj = Proj(init= proj_1)
            outProj = Proj(init= proj_2)
            
            # The reference coordinates are transformed according to the files
            # that will be clip.
            xcutmin2, ycutmin2 = transform(inProj,outProj,xcutmin,ycutmin)
            xcutmax2, ycutmax2 = transform(inProj,outProj,xcutmax,ycutmax)
            window2 = (xcutmin2,ycutmin2,xcutmax2,ycutmax2)
            
            # The files are clip.
            gdal.Translate(save_path, dataset1, projWin = window)
            gdal.Translate(save_path + str('2.tif'), dataset2, projWin = window)
            
        # A button is created and displayed that calls the function to clip the raster.
        button = tkinter.Button(master=clipTworWin, text="cut", command=cut_ras)
        button.pack(side=tkinter.BOTTOM)
        
        # An object belonging to the Cursor class is defined, and the event is set to a click.
        cursor = Cursor(ax)
        cid = fig.canvas.mpl_connect('button_press_event', cursor.on_mouse_click)
        return cid, err
    
    # A button is created and displayed.
    button3 = Button(clipTwokWin, text="Clip...",command = cut_two_raster)
    button3.grid(row=8,column=1,padx=25,pady=5,columnspan=2)
    
def open_raster():
    """
    With this function a raster file can be opened and displayed on the main 
    screen of the interface.
    """
    open_file()
    ax = figu.add_subplot(111)
    figu.subplots_adjust(bottom=0, right=1, top=1, left=0, wspace=0, hspace=0)
 
    with rasterio.open(path) as src_plot:
        show(src_plot, ax=ax, cmap='gist_gray')
        
    plt.close()
    ax.set(title="",xticks=[], yticks=[])
    canvas1.draw()

def donothing():
    
    filewin = Toplevel(root)
    button = Button(filewin, text="Do nothing button")
    button.pack()
    
# Main window configuration.
root = Tk()
root.minsize(width=950, height=700)
root.wm_title("Raster: Download and clip")
root["bg"] = "#6DBFD3"

#  Menu bar configuration.
menubar = Menu(root)
# Options available for the file menu.
filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Download", command=get_info)
filemenu.add_command(label="Open", command=open_raster)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
# Options available for the edit menu.
editmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=editmenu)
editmenu.add_command(label="Stack", command=stack)
editmenu.add_separator()
editmenu.add_command(label="Cut Big Raster", command=clip_big_raster)
editmenu.add_separator()
editmenu.add_command(label="Cut two raster", command=clip_two_raster)
# Options available for the help menu.
helpmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
root.config(menu=menubar)

# Configuration of the figure that is in the main window.
figu = Figure(figsize=(5, 4), dpi=100)
canvas1 = FigureCanvasTkAgg(figu, master=root)
canvas1.draw()

# Toolbar to manipulate the figure in the main window.
toolbar = NavigationToolbar2Tk(canvas1,root)
toolbar.update()
toolbar.pack(side=tkinter.TOP, fill=tkinter.X, padx=8)
canvas1.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1, padx=10, pady=5)
canvas1._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1, padx=10, pady=5)

# The main window is displayed.
root.mainloop()

# The auxiliary file is removed.
remove("output_10_por.tif")