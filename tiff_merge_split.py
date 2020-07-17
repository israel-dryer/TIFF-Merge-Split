"""
    Name: Tiff Split/Merge Utility
    Description: The purpose of this program is to split and/or merge tiff files.
    Author: Israel Dryer
    Modified: 2020-07-16
"""
import os
import datetime
import pathlib
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk
from PIL.TiffImagePlugin import AppendingTiffWriter
from PIL.TiffImagePlugin import TiffImageFile

"""
    This resource path stuff is required to make a single-file executable work for pyinstaller. Change the `DEV_MODE` to True if running
    directly from a python script. Otherwise, set to False
"""

DEV_MODE = True
def resource_path(relative_path, devmode=DEV_MODE):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if not devmode:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    else:
        return relative_path

class Application(tk.Tk):

    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title('TIFF Merge/Split Utility')
        self.geometry('600x425')
        self.iconbitmap(resource_path('icon.ico'))
        self.style = ttk.Style()
        self.style.theme_use('vista')
        self.main_frame = ttk.Frame(self, padding=10)
        self.date = datetime.datetime.today().date().strftime('%Y%m%d')

        # help
        self.head_frame = ttk.Frame(self.main_frame)
        self.img_help = ImageTk.PhotoImage(file=resource_path('help.ico'))
        self.style.configure('Help.TButton', relief='flat', border=0, highlightthickness=0)
        self.help_btn = ttk.Label(self.head_frame, image=self.img_help, padding=0)

        # treeview
        self.treeview = ttk.Treeview(self.main_frame, selectmode='browse')
        self.treeview['columns'] = ('path',)
        self.treeview.column('#0', width=50)
        self.treeview.heading('#0', text='  File Name', anchor='w')
        self.treeview.heading('path', text='   File Path', anchor='w')

        # option menu
        self.file_frame = ttk.Frame(self.main_frame, padding=5)
        self.file_var = tk.StringVar()
        self.file_var.set(pathlib.Path().cwd() / f'converted_{self.date}.tif')
        self.file_label = ttk.Label(self.file_frame, text='Output file:')
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_var)
        self.btn_frame = ttk.Frame(self.main_frame)

        # option settings
        self.img_split = ImageTk.PhotoImage(file=resource_path('split.png'))
        self.img_merge = ImageTk.PhotoImage(file=resource_path('merge.png'))
        self.option_var = tk.IntVar()
        self.option_var.set(1)
        self.option_frame = ttk.LabelFrame(self.main_frame, text='Conversion Settings', padding=5)
        self.option_merge = ttk.Radiobutton(self.option_frame, image=self.img_merge, compound='left', text='merge to single file', value=1, variable=self.option_var)
        self.option_split = ttk.Radiobutton(self.option_frame, image=self.img_split, compound='left', text='split to multi-files', value=2, variable=self.option_var)

        self.btn_open = ttk.Button(self.btn_frame, text='Open', underline=0, command=self.on_open)
        self.btn_convert = ttk.Button(self.btn_frame, text='Convert', underline=3, command=self.on_convert)
        self.btn_clear = ttk.Button(self.btn_frame, text='Clear List', underline=4, command=self.on_clear)

        # pack items to frame
        self.help_btn.pack(side='right')
        self.head_frame.pack(fill='x', expand='yes')
        self.file_label.pack(side='left', padx=(0, 10))
        self.file_entry.pack(side='left', expand='yes', fill='x')
        self.btn_open.pack(side='left', fill='x', expand='yes')
        self.btn_convert.pack(side='left', fill='x', expand='yes')
        self.btn_clear.pack(side='left', fill='x', expand='yes')
        self.treeview.pack(fill='both', expand='yes')
        self.option_merge.pack(side='left', fill='x')
        self.option_split.pack(side='left', fill='x', padx=15)
        self.option_frame.pack(fill='x', expand='yes')
        self.file_frame.pack(fill='x', pady=5)
        self.btn_frame.pack(fill='x')        
        self.main_frame.pack(fill='both', expand='yes')

        # bindings
        self.do_bindings()

        # other initial settings
        self.center_window()

    def move_up(self, _):
        """Move current item up the list"""
        curr = self.treeview.focus()
        index = self.treeview.index(curr)
        self.treeview.move(curr, '', index-1)

    def move_down(self, _):
        """Move current item down the list"""
        curr = self.treeview.focus()
        index = self.treeview.index(curr)
        self.treeview.move(curr, '', index+1)

    def delete(self, _):
        """Delete current item"""
        curr = self.treeview.focus()
        # find next focus item
        next_item = self.treeview.prev(curr)
        if not next_item:
            next_item = self.treeview.next(curr)
        # delete current item and set new focus
        self.treeview.delete(curr)
        self.treeview.selection_set(next_item)
        self.treeview.focus(next_item)

    def on_open(self):
        """Open single or multiple files"""
        filenames = filedialog.askopenfilenames(parent=self.treeview, filetypes = [("TIFF file", "*.tif *.tiff")])
        self.update_idletasks() # without this update the gui becomes temporarily unresponsive
        if filenames:
            for name in filenames:
                short_name = pathlib.Path(name).stem
                self.treeview.insert('', 'end', text=short_name, values=(str(name),))

    def on_clear(self):
        """Delete all items from the list"""
        items = self.treeview.get_children()
        for item in items:
            self.treeview.delete(item)

    def on_convert(self):
        """Combine all tiff files into single tiff file, then open"""
        items = self.treeview.get_children()
        if items:
            if self.option_var.get() == 1:
                # merge must include more than 1 file else return error
                if len(items) > 1:
                    self.merge_files(items)
                else:
                    message = "Please select 2 or more files to perform a merge."
                    messagebox.showerror(title='Missing files', message=message)
            else:
                # only 1 file shold be selected when splitting the file
                if len(items) > 1:
                    message = "Select 1 file only when splitting to multiple files."
                    messagebox.showerror(title='Too many files', message=message)
                else:
                    self.split_files(items)
        else:
            message = "Please select file(s) to continue."
            messagebox.showerror(title='Missing files', message=message)

    def merge_files(self, items):
        """Merge all files into single file"""
        files = [self.treeview.item(item, 'values') for item in items]
        try:
            images = [TiffImageFile(file[0]) for file in files]
            outfile = self.file_entry.get()
            with AppendingTiffWriter(fn=outfile, new=True) as writer:
                for img in images:
                    img.save(writer)
                    writer.newFrame()
        except Exception as err:
            messagebox.showerror(message=f"Error converting file:\n\n{err}")
        else:
            messagebox.showinfo(message="Finished!")

    def split_files(self, items):
        """Split a single file in to multiple files"""
        file = self.treeview.item(items[0],'values')[0]
        image = TiffImageFile(file)
        frame_count = image.n_frames
        # can only split a file with more than one frame
        if frame_count == 1:
            message = "This file contains only 1 frame. There is nothing to split."
            messagebox.showerror(title='Not enough frames', message=message)
        else:
            try:
                for i in range(frame_count):
                    image.seek(i)
                    filestem = pathlib.Path(file).stem
                    image.save(f'{filestem}_{i}.tif')
            except Exception as err:
                messagebox.showerror(message=f"Error converting file:\n\n{err}")
            else:
                messagebox.showinfo(message="Finished!")

    def do_bindings(self):
        """Setup bindings for the application"""
        self.treeview.bind("<Prior>", self.move_up)
        self.treeview.bind("<Next>", self.move_down)
        self.treeview.bind("<Delete>", self.delete)
        self.help_btn.bind("<Button-1>", lambda e: HelpPopup(self))

    def center_window(self):
        """Center a tkinter window"""
        self.update_idletasks()
        width = self.winfo_width()
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = self.winfo_height()
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.deiconify()

class HelpPopup(tk.Toplevel):
    """A top level class that generates a help widget"""
    def __init__(self, parent):
        super().__init__(master=parent)
        self.set_position()
        self.transient(parent)
        self.iconbitmap(resource_path('help.ico'))
        self.text = ScrolledText(self, font='-size 8', padx=10, pady=10, wrap='word')
        self.text.pack(fill='both', expand='yes')
        # add help text to widget
        text = pathlib.Path(resource_path('help.txt')).read_text(encoding='utf-8')
        self.text.insert('end', text)
        self.text.configure(state='disabled')
             
    def set_position(self):
        """Move toplevel to master window position"""
        x = self.master.winfo_rootx()
        y = self.master.winfo_rooty()
        self.geometry(f'+{x}+{y}')


if __name__ == '__main__':
    app = Application()
    app.mainloop()