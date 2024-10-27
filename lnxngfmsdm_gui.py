#!/usr/bin/python3
# Name:        LNX NG FMS Data Manager
# Description: Navigraph FMS Data Manager alternative for Linux to manage AIRAC cycle databases
# Version:     1.0.1
# Requirement: Google Chrome Webbrowser to use the 'Download' feature via included Selenium WebDriver
# Usage:       Make the AppImage executable and run it
# -----------------------------------------------------------------------------
# Copyright (c) 2024 github.com/berndgz
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import base64
import os
import sys
import webbrowser

import lnxngfmsdm_core as core
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk

wx_opsys = ["Windows", "MacOS", "Linux"]
wx_sim = ["XP10", "XP11", "XP12"]


def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        print("running in a PyInstaller bundle")
        base_path = sys._MEIPASS
    else:
        print("running in a normal Python process")
        base_path = os.path.abspath(".")
    # Return absolute path to resource
    return os.path.join(base_path, relative_path)


# main = tk.Tk()
main = ThemedTk(theme="plastik")
main.title("LNX NG FMS Data Manager")
small_icon = tk.PhotoImage(file=resource_path("images/compass-3-32.png"))
large_icon = tk.PhotoImage(file=resource_path("images/compass-3-256.png"))
main.iconphoto(False, large_icon)
main.geometry("1900x475")
main.resizable(True, False)

list_icon = tk.PhotoImage(file=resource_path("images/list-2-24.png"))
add_row_icon = tk.PhotoImage(file=resource_path("images/add-row-24.png"))
download_icon = tk.PhotoImage(file=resource_path("images/download-24.png"))
update_icon = tk.PhotoImage(file=resource_path("images/installing-updates-24.png"))
settings_icon = tk.PhotoImage(file=resource_path("images/settings-5-24.png"))
refresh_icon = tk.PhotoImage(file=resource_path("images/available-updates-24.png"))
exit_icon = tk.PhotoImage(file=resource_path("images/exit-24.png"))
about_icon = tk.PhotoImage(file=resource_path("images/about-24.png"))
save_icon = tk.PhotoImage(file=resource_path("images/save-24.png"))
delete_icon = tk.PhotoImage(file=resource_path("images/delete-24.png"))
folder_icon = tk.PhotoImage(file=resource_path("images/folder-3-24.png"))
archive_icon = tk.PhotoImage(file=resource_path("images/archive-2-24.png"))


class AddonWidget(ttk.Frame):
    def __init__(self, parent, addon):
        super().__init__(master=parent)

        # styles
        self.style = ttk.Style(self)
        self.style.configure("Label.TLabel", padding=(10, 0, 0, 0))

        # frame
        self["borderwidth"] = 2
        self["relief"] = "solid"
        self["padding"] = (0, 0, 10, 0)

        # widgets
        # ---- DELETE ----
        self.del_btn = ttk.Button(self, image=delete_icon, command=lambda: self.del_btn_pressed(addon))
        self.del_btn.grid(row=0, column=0, sticky=tk.NS, padx=10, pady=5)
        # ---- SAVE ----
        self.save_btn = ttk.Button(self, image=save_icon, command=lambda: self.save_btn_pressed(addon), state=tk.DISABLED)
        self.save_btn.grid(row=0, column=1, sticky=tk.NS, padx=0, pady=5)
        # ---- DIVIDER ----
        ttk.Separator(self, orient="vertical").grid(row=0, column=2, sticky=tk.NS, padx=10, pady=5)
        # ---- UID ----
        ttk.Label(self, text="ID:").grid(row=0, column=3, sticky=tk.NS)
        self.uid_lbl = ttk.Label(self, width=3, anchor=tk.CENTER, relief=tk.SUNKEN, borderwidth=1)
        self.uid_lbl.config(text=addon.uid)
        self.uid_lbl.grid(row=0, column=4, sticky=tk.NS, padx=0, pady=5)
        # ---- NAME ----
        ttk.Label(self, text="SOFTWARE:", style="Label.TLabel").grid(row=0, column=5, sticky=tk.NS)
        self.name_entry = ttk.Entry(self, width=30)
        self.name_entry.insert(0, addon.name)
        self.name_entry.bind("<KeyRelease>", self.entry_changed)
        self.name_entry.bind("<Control-a>", self.select_all)
        self.name_entry.grid(row=0, column=6, sticky=tk.NS, padx=0, pady=5)
        # ---- ARCHIVE ----
        ttk.Label(self, text="ARCHIVE:", style="Label.TLabel").grid(row=0, column=7, sticky=tk.NS)
        self.archive_entry = ttk.Entry(self, width=40)
        self.archive_entry.insert(0, addon.archive)
        self.archive_entry.bind("<KeyRelease>", self.entry_changed)
        self.archive_entry.bind("<Control-a>", self.select_all)
        self.archive_entry.grid(row=0, column=8, sticky=tk.NS, padx=0, pady=5)
        self.archive_btn = ttk.Button(self, image=archive_icon, command=lambda: self.archive_btn_pressed(addon))
        self.archive_btn.grid(row=0, column=9, sticky=tk.NS, padx=0, pady=5)
        # ---- PATH ----
        ttk.Label(self, text="INSTALL:", style="Label.TLabel").grid(row=0, column=10, sticky=tk.NS)
        self.path_entry = ttk.Entry(self, width=50)
        self.path_entry.insert(0, addon.path)
        self.path_entry.bind("<KeyRelease>", self.entry_changed)
        self.path_entry.bind("<Control-a>", self.select_all)
        self.path_entry.grid(row=0, column=11, sticky=tk.NS, padx=0, pady=5)
        self.path_btn = ttk.Button(self, image=folder_icon, command=lambda: self.path_btn_pressed(addon))
        self.path_btn.grid(row=0, column=12, sticky=tk.NS, padx=0, pady=5)
        # ---- OPSYS ----
        ttk.Label(self, text="OS:", style="Label.TLabel").grid(row=0, column=13, sticky=tk.NS)
        self.opsys_cbox = ttk.Combobox(self, state="readonly", values=wx_opsys, width=8)
        self.opsys_cbox.set(addon.opsys)
        self.opsys_cbox.bind("<<ComboboxSelected>>", self.cbox_changed)
        self.opsys_cbox.grid(row=0, column=14, sticky=tk.NS, padx=0, pady=5)
        # ---- SIM ----
        ttk.Label(self, text="SIM:", style="Label.TLabel").grid(row=0, column=15, sticky=tk.NS)
        self.sim_cbox = ttk.Combobox(self, state="readonly", values=wx_sim, width=5)
        self.sim_cbox.set(addon.sim)
        self.sim_cbox.bind("<<ComboboxSelected>>", self.cbox_changed)
        self.sim_cbox.grid(row=0, column=16, sticky=tk.NS, padx=0, pady=5)
        # ---- AIRAC ----
        ttk.Label(self, text="AIRAC:", style="Label.TLabel").grid(row=0, column=17, sticky=tk.NS)
        self.airac_lbl = ttk.Label(self, width=9, anchor=tk.CENTER, relief=tk.SUNKEN, borderwidth=1)
        self.airac_lbl.config(text=f"{addon.cycle}rev{addon.revision}")
        self.airac_lbl.grid(row=0, column=18, sticky=tk.NS, padx=0, pady=5)

        self.pack(anchor=tk.W, padx=10, pady=5)

    # event parameter from event object is mandatory
    def cbox_changed(self, event):
        print("cbox_changed", event)
        event.widget.selection_clear()
        print(event.widget.get())
        self.save_btn.config(state=tk.NORMAL)

    # event parameter from event object is mandatory
    def entry_changed(self, event):
        print("entry_changed", event)
        self.save_btn.config(state=tk.NORMAL)

    def path_btn_pressed(self, addon):
        path = filedialog.askdirectory(initialdir="~", title=f"Choose Addon ID: {addon.uid} install directory")
        print("path =>", path)
        if "/" in path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.save_btn.config(state=tk.NORMAL)

    def archive_btn_pressed(self, addon):
        archive = filedialog.askopenfilename(initialdir="~", title=f"Choose Addon ID: {addon.uid} archive file", filetypes=(("Zip-Archive", "*.zip"),))
        print("archive =>", archive)
        if "/" in archive:
            path = str(archive[:archive.rindex("/")])
            print("path => " + path)
            file = str(archive[archive.rindex("/") + 1:])
            print("file => " + file)
            wildcard = re.sub(r"(?i)[0-9]{4}\.zip$", "*.zip", file)
            print("wildcard => " + wildcard)
            self.archive_entry.delete(0, tk.END)
            self.archive_entry.insert(0, wildcard)
            self.save_btn.config(state=tk.NORMAL)
            # Update download path under settings
            core.Addon.download = path
            core.upsert_setting(core.Addon.download, core.Addon.username, core.Addon.password)
            messagebox.showinfo("Information", "Downloads path under Settings has been updated!")
            core.get_settings()

    def save_btn_pressed(self, addon):
        if self.name_entry.get() and self.archive_entry.get() and self.path_entry.get() and self.sim_cbox.get() and self.opsys_cbox.get():
            self.save_btn.config(state=tk.DISABLED)
            core.upsert_addon(addon.uid, self.name_entry.get(), self.archive_entry.get(), self.path_entry.get(), self.sim_cbox.get(), self.opsys_cbox.get())
            messagebox.showinfo("Information", f"Addon ID: {addon.uid} is saved!")
            core.init()
        else:
            messagebox.showerror("Error", f"Addon ID: {addon.uid} is missing value/s!")

    @staticmethod
    def del_btn_pressed(addon):
        result = messagebox.askquestion("Question", f"Are you sure that you want to delete the Addon ID: {addon.uid} list item?")
        print(result)
        if result == "yes":
            core.delete_addon(addon.uid)
            refresh()

    # event parameter from event object is mandatory
    def select_all(self, event):
        print("select_all", event)
        self.save_btn.config(state=tk.NORMAL)
        # select text
        event.widget.select_range(0, 'end')
        # move cursor to the end
        event.widget.icursor('end')
        # stop propagation
        return 'break'


class SettingsWidget(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)

        # styles
        self.style = ttk.Style(self)
        self.style.configure("Label.TLabel", padding=(10, 0, 0, 0))

        # frame
        self["borderwidth"] = 2
        self["relief"] = "solid"
        self["padding"] = (10, 0)

        # widgets
        # ---- SAVE ----
        self.save_btn = ttk.Button(self, image=save_icon, command=lambda: self.save_btn_pressed(), state=tk.DISABLED)
        self.save_btn.grid(row=0, column=1, sticky=tk.NS, padx=0, pady=5)
        # ---- DIVIDER ----
        ttk.Separator(self, orient="vertical").grid(row=0, column=2, sticky=tk.NS, padx=10, pady=5)
        # ---- USERNAME ----
        ttk.Label(self, text="USERNAME:").grid(row=0, column=5, sticky=tk.NS)
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.insert(0, core.Addon.username)
        self.username_entry.bind("<KeyRelease>", self.entry_changed)
        self.username_entry.bind("<Control-a>", self.select_all)
        self.username_entry.grid(row=0, column=6, sticky=tk.NS, padx=0, pady=5)
        # ---- PASSWORD ----
        ttk.Label(self, text="PASSWORD:", style="Label.TLabel").grid(row=0, column=7, sticky=tk.NS)
        self.password_entry = ttk.Entry(self, width=40, show="*")
        self.password_entry.insert(0, base64.b64decode(core.Addon.password).decode("utf-8"))
        self.password_entry.bind("<KeyRelease>", self.entry_changed)
        self.password_entry.bind("<Control-a>", self.select_all)
        self.password_entry.grid(row=0, column=8, sticky=tk.NS, padx=0, pady=5)
        # ---- DOWNLOADS ----
        ttk.Label(self, text="DOWNLOADS:", style="Label.TLabel").grid(row=0, column=10, sticky=tk.NS)
        self.downloads_entry = ttk.Entry(self, width=50)
        self.downloads_entry.insert(0, core.Addon.download)
        self.downloads_entry.bind("<KeyRelease>", self.entry_changed)
        self.downloads_entry.bind("<Control-a>", self.select_all)
        self.downloads_entry.grid(row=0, column=11, sticky=tk.NS, padx=0, pady=5)
        self.downloads_btn = ttk.Button(self, image=folder_icon, command=lambda: self.downloads_btn_pressed())
        self.downloads_btn.grid(row=0, column=12, sticky=tk.NS, padx=0, pady=5)

        self.pack(anchor=tk.W, padx=10, pady=5)

    # event parameter from event object is mandatory
    def entry_changed(self, event):
        print("entry_changed", event)
        self.save_btn.config(state=tk.NORMAL)

    def downloads_btn_pressed(self):
        downloads = filedialog.askdirectory(initialdir="~", title="Choose Downloads directory")
        print("path =>", downloads)
        if "/" in downloads:
            self.downloads_entry.delete(0, tk.END)
            self.downloads_entry.insert(0, downloads)
            self.save_btn.config(state=tk.NORMAL)

    def save_btn_pressed(self):
        if self.downloads_entry.get() and self.username_entry.get() and self.password_entry.get():
            self.save_btn.config(state=tk.DISABLED)
            core.upsert_setting(self.downloads_entry.get(), self.username_entry.get(), base64.b64encode(self.password_entry.get().encode("utf-8")).decode("utf-8"))
            messagebox.showinfo("Information", "Settings are saved!")
            core.get_settings()
        else:
            messagebox.showerror("Error", "Settings are missing value/s!")

    # event parameter from event object is mandatory
    def select_all(self, event):
        print("select_all", event)
        self.save_btn.config(state=tk.NORMAL)
        # select text
        event.widget.select_range(0, 'end')
        # move cursor to the end
        event.widget.icursor('end')
        # stop propagation
        return 'break'


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.configure(xscrollcommand=scrollbar_h.set)
        scrollbar_h.pack(side="bottom", fill="x")
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)


def addon_list():
    # Iterate through every widget inside the frame and delete it
    for widget in content_frame.scrollable_frame.winfo_children():
        widget.destroy()
    # Iterate through every addon and create custom widget
    for addon in core.addons:
        AddonWidget(content_frame.scrollable_frame, addon)
    # Set button state
    add_addon_btn.config(state=tk.NORMAL)


def add_addon():
    core.create_addon("Addon name", "addon_*.zip", "/path/to/install/directory", "XP11", "Linux")
    refresh()


def update():
    pbar["value"] = 1
    main.update()
    items = len(core.addons)
    if items > 0:
        step = 100 / items
        for addon in core.addons:
            result = core.update(addon)
            print(result)
            pbar["value"] += step
            main.update()
            if result == 1:
                messagebox.showwarning("Warning", f"Archive file for Addon ID: {addon.uid} is missing!")
    messagebox.showinfo("Information", "Update is done!")
    refresh()


def settings():
    # Iterate through every widget inside the frame and delete it
    for widget in content_frame.scrollable_frame.winfo_children():
        widget.destroy()
    # Create settings widget
    SettingsWidget(content_frame.scrollable_frame)
    # Set button state
    add_addon_btn.config(state=tk.DISABLED)


def refresh():
    pbar["value"] = 1
    main.update()
    core.init()
    for i in range(2, 101):
        pbar["value"] = i
        main.update()
        # sleep(0.01)
    pbar["value"] = 0
    addon_list()


def about():
    messagebox.showinfo("About", "lnxngfmsdm-x86_64\nver. 1.0.1\nⒸ 2024 github.com/berndgz")


def tk_exit():
    main.destroy()


def btn_pressed():
    pass


def pbar_enter():
    pbar.config(cursor="hand2")


# ----------------------
# ---- Header Frame ----
# ----------------------
header_frame = ttk.Frame(main)
# ---- Icon ----
icon_lbl = ttk.Label(header_frame, image=small_icon, compound=tk.LEFT)
icon_lbl.grid(row=0, column=0, sticky=tk.NS, padx=10)
# ---- Addon List ----
addon_list_btn = ttk.Button(header_frame, text="Addon List", image=list_icon, compound=tk.LEFT, command=lambda: addon_list())
addon_list_btn.grid(row=0, column=1, sticky=tk.NS, padx=0, pady=5)
# ---- Add Addon ----
add_addon_btn = ttk.Button(header_frame, text="Add Addon", image=add_row_icon, compound=tk.LEFT, command=lambda: add_addon())
add_addon_btn.grid(row=0, column=2, sticky=tk.NS, padx=10, pady=5)
# ---- Download ----
download_btn = ttk.Button(header_frame, text="Download", image=download_icon, compound=tk.LEFT, command=lambda: core.download())
download_btn.grid(row=0, column=3, sticky=tk.NS, padx=0, pady=5)
# ---- Update ----
update_btn = ttk.Button(header_frame, text="Update", image=update_icon, compound=tk.LEFT, command=lambda: update())
update_btn.grid(row=0, column=4, sticky=tk.NS, padx=10, pady=5)
# ---- Settings ----
settings_btn = ttk.Button(header_frame, text="Settings", image=settings_icon, compound=tk.LEFT, command=lambda: settings())
settings_btn.grid(row=0, column=5, sticky=tk.NS, padx=0, pady=5)
# ---- Refresh ----
refresh_btn = ttk.Button(header_frame, text="Refresh", image=refresh_icon, compound=tk.LEFT, command=lambda: refresh())
refresh_btn.grid(row=0, column=6, sticky=tk.NS, padx=10, pady=5)
# ---- About ----
about_btn = ttk.Button(header_frame, text="About", image=about_icon, compound=tk.LEFT, command=lambda: about())
about_btn.grid(row=0, column=7, sticky=tk.NS, padx=0, pady=5)
# ---- Exit ----
exit_btn = ttk.Button(header_frame, text="Exit", image=exit_icon, compound=tk.LEFT, command=lambda: tk_exit())
exit_btn.grid(row=0, column=8, sticky=tk.NS, padx=10, pady=5)
# ---- [/] ----
header_frame.pack(fill=tk.X)
# ---- SEPARATOR ----
ttk.Separator(main, orient="horizontal").pack(fill=tk.X)
# -----------------------
# ---- Content Frame ----
# -----------------------
content_frame = ScrollableFrame(main)
# ---- [/] ----
content_frame.pack(fill=tk.BOTH, expand=tk.TRUE)
# ---- SEPARATOR ----
ttk.Separator(main, orient="horizontal").pack(fill=tk.X)
# ----------------------
# ---- Footer Frame ----
# ----------------------
# ttk.Label(footer_frame, text="Made with ♥ by github.com/berndgz", anchor=tk.CENTER).pack()
footer_frame = ttk.Frame(main)
style = ttk.Style(main)
style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})], 'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': 'nswe'})])
style.configure('text.Horizontal.TProgressbar', text='Made with ♥ by github.com/berndgz', anchor='center', foreground='#155ca2')
pbar = ttk.Progressbar(footer_frame, style='text.Horizontal.TProgressbar')
pbar.bind("<Enter>", pbar_enter())
pbar.bind("<Button-1>", lambda x: webbrowser.open("https://github.com/berndgz/lnxngfmsdm"))
pbar.pack(fill=tk.X)
# ---- [/] ----
footer_frame.pack(fill=tk.X)
# ----------------------

# main.after(1000, refresh())
refresh()
main.mainloop()
