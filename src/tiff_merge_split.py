"""
    Title
        Tiff Merge/Split Utility

    Description
        Merge a collection of Tiff files into a single file, or split a
        single files into multiple image files.

    Author
        Israel Dryer, israel.dryer@gmail.com

    Date Created
        2020-07-16

    Date Modified
        2021-09-02


    -------------------------------------------------------------------

    2020-09-02 : Refactor entire program.
"""
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk
from PIL.TiffImagePlugin import AppendingTiffWriter
from PIL.TiffImagePlugin import TiffImageFile


def resource_path() -> str:
    """Get the absolute path of the temp PyInstaller folder; otherwise 
    return the relative path.
    """
    try:
        base_path = getattr(sys, '_MEIPASS')
        return Path(base_path)
    except:
        return Path('.')


class TiffUtility(tk.Tk):

    def __init__(self):
        super().__init__()
        self.withdraw() # hide window until drawn
        
        self.path = resource_path()
        self.title('Tiff Merge/Split Utility')
        self.geometry('600x425')
        self.iconbitmap(self.path / 'icon.ico')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.theme_use('xpnative')
        self.window = ttk.Frame(self, padding=10)
        self.today = datetime.today().strftime(r'%Y%m%d')
        self.default_path = Path(os.environ['USERPROFILE']) / 'Desktop'

        # help button
        self.head_frame = ttk.Frame(self.window)
        self.img_help = ImageTk.PhotoImage(file=self.path / 'help.ico')
        self.style.configure('Help.TButton', relief=tk.FLAT, border=0, 
            highlighthickness=0)
        self.btn_help = ttk.Label(self.head_frame, image=self.img_help,
            padding=0)

        # treeview
        self.treeview = ttk.Treeview(self.window, selectmode=tk.BROWSE)
        self.treeview['columns'] = ('path',)
        self.treeview.column('#0',width=50)
        self.treeview.heading('#0', text='File Name', anchor=tk.W)
        self.treeview.heading('path', text='File Path', anchor=tk.W)

        # option menu
        self.file_frame = ttk.Frame(self.window, padding=5)
        self.file_var = tk.StringVar(
            value=self.default_path / f'converted_{self.today}.tif')
        self.file_label = ttk.Label(self.file_frame, text='Output file:')
        self.file_entry = ttk.Entry(self.file_frame, 
            textvariable=self.file_var)
        self.btn_frame = ttk.Frame(self.window)
    
        # option settings
        self.img_split = ImageTk.PhotoImage(file=self.path / 'split.png')
        self.img_merge = ImageTk.PhotoImage(file=self.path / 'merge.png')
        self.option_var = tk.IntVar(value=1)
        self.option_frame = ttk.Labelframe(self.window, 
            text='Conversion Settings', padding=5)
        self.option_merge = ttk.Radiobutton(
            self.option_frame, image=self.img_merge, compound=tk.LEFT, 
            text='merge to single file', value=1, 
            variable=self.option_var)
        self.option_split = ttk.Radiobutton(
            self.option_frame, image=self.img_split, compound=tk.LEFT,
            text='split to multi-files', value=2,
            variable=self.option_var)
        
        # action buttons
        self.btn_open = ttk.Button(self.btn_frame, text='Open', 
            underline=0, command=self.on_open)
        self.btn_convert = ttk.Button(self.btn_frame, text='Convert',
            underline=3, command=self.on_convert)
        self.btn_clear = ttk.Button(self.btn_frame, text='Clear list',
            underline=4, command=self.on_clear)

        # pack widgets
        self.btn_help.pack(side=tk.RIGHT)
        self.file_label.pack(side=tk.LEFT, padx=(0, 10))
        self.file_entry.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.btn_open.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        self.btn_convert.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        self.btn_clear.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        self.treeview.pack(fill=tk.BOTH, expand=tk.YES)
        self.option_merge.pack(side=tk.LEFT, fill=tk.X)
        self.option_split.pack(side=tk.LEFT, fill=tk.X, padx=15)
        self.option_frame.pack(fill=tk.X, expand=tk.YES)

        # pack element containers
        self.head_frame.pack(fill=tk.X, expand=tk.YES, before=self.treeview)
        self.file_frame.pack(fill=tk.X, pady=5)
        self.btn_frame.pack(fill=tk.X)
        self.window.pack(fill=tk.BOTH, expand=tk.YES)

        # final window setup
        self._do_bindings()
        self.deiconify()

    def _do_bindings(self):
        """Setup binding for the application"""
        self.treeview.bind("<Prior>", self.item_move_up)
        self.treeview.bind("<Next>", self.item_move_down)
        self.treeview.bind("<Delete>", self.item_delete)
        self.btn_help.bind("<Button-1>", self.on_help)

    def _center_window(self):
        ...

    def on_help(self, *_):
        """Open a help file in the default"""
        file = self.path / 'help.html'
        webbrowser.open(file.absolute().as_uri())

    def on_open(self, *_):
        """Open file(s) to process"""
        filenames = filedialog.askopenfilenames(
            parent=self.treeview,
            filetypes=[('TIFF file', '*.tif *.tiff')],
            initialdir=self.default_path
            )
        self.update_idletasks()
        if not filenames:
            return
        for name in filenames:
            short_name = Path(name).stem
            self.treeview.insert('', tk.END, text=short_name, 
                values=(str(name),))

    def on_convert(self, *_):
        """Combine all tiff files into a single tiff file, then open"""
        items = self.treeview.get_children()
        if items:
            if self.option_var.get() == 1:
                # merge must include more than 1 file else return error
                if len(items) > 1:
                    self.file_merge(items)
                else:
                    message = "Please select 2 or more files to merge."
                    messagebox.showerror("Missing files", message)
            else:
                # only 1 file selected when splitting the file
                if len(items) > 1:
                    message = "Select a single file only to split."
                    messagebox.showerror("Too many files", message)
                else:
                    self.file_split(items)
        else:
            message = "Please select file(s) to continue."
            messagebox.showerror('Missing files', message)

    def on_clear(self, *_):
        """Delete all items from the list"""
        items = self.treeview.get_children()
        for item in items:
            self.treeview.delete(item)

    def file_merge(self, items):
        """Merge all files into a single file
        
        Parameters
        ----------
        items : List
            A list of treeview iid's.
        """
        files = [self.treeview.item(item, 'values') for item in items]
        try:
            images = [TiffImageFile(file[0]) for file in files]
            outfile = self.file_entry.get()
            with AppendingTiffWriter(fn=outfile, new=True) as writer:
                for img in images:
                    img.save(writer)
                    writer.newFrame()
        except Exception as err:
            messagebox.showerror(message=f'Error converting file:\n\n{err}')
        else:
            messagebox.showinfo(message="Finished!")

    def file_split(self, items):
        """Split a single file into multiple files
        
        Parameters
        ----------
        items : List
            A list of treeview iid's.        
        """
        file = self.treeview.item(items[0], 'values')[0]
        image = TiffImageFile(file)
        frame_count = image.n_frames
        # can only split a file iwth more than one frame
        if frame_count == 1:
            message = ''.join([
                "This file contains only 1 frame.",
                "There is nothing to split."
            ])
            messagebox.showerror("Not enough frames", message)
        else:
            try:
                for i in range(frame_count):
                    image.seek(i)
                    filestem = Path(file).stem
                    image.save(f'{filestem}_{i}.tif')
            except Exception as err:
                messagebox.showerror(
                    message=f'Error converting file:\n\n{err}')
            else:
                messagebox.showinfo(message='Finished!')

    def item_move_up(self, *_):
        """Move current item up the list"""
        curr = self.treeview.focus()
        index = self.treeview.index(curr)
        self.treeview.move(curr, '', index - 1)

    def item_move_down(self, *_):
        """Move current item down the list"""
        curr = self.treeview.focus()
        index = self.treeview.index(curr)
        self.treeview.move(curr, '', index + 1)

    def item_delete(self, *_):
        """Remove the current item from the list"""
        curr = self.treeview.focus()
        prev = self.treeview.prev(curr)
        if not prev:
            next = self.treeview.next(curr)
        item = prev or next
        self.treeview.delete(curr)
        self.treeview.selection_set(item)
        self.treeview.focus(item)

    

if __name__ == '__main__':

    t = TiffUtility()
    t.mainloop()