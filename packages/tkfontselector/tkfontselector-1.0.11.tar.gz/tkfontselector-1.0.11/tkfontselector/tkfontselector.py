"""
Forked from https://github.com/j4321/tkFontChooser and improved. Was going to do a PR
to clean some things up, but the repo hasn't been active for over 5 years.
"""

from tkinter import Tk, Toplevel, Listbox, StringVar, BooleanVar, TclError
from tkinter.ttk import Checkbutton, Frame, Label, Button, Scrollbar, Style, Entry
from tkinter.font import families, Font
from typing import Union, List

from tkfontselector.translations import LANGUAGES
from tkfontselector.translations.get_system_locale import system_locale

TR = LANGUAGES["en"]
detect_language = system_locale()
if detect_language and detect_language in LANGUAGES.keys():
    TR = LANGUAGES[detect_language]


class FontSelector(Toplevel):
    """Font Selector dialog."""

    def __init__(
        self,
        master: Union[Tk, Toplevel] = None,
        text: str = "Abcd",
        title: str = "Font Selector",
        fixed_only: Union[bool, None] = None,
        families_only: bool = False,
        font_dict: dict = {},
        **kwargs
    ):
        """
        Create a new FontSelector instance.
        Arguments:
            master: Tk or Toplevel instance
                master window
            text: str
                text to be displayed in the preview label
            title: str
                window title
            fixed_only: (bool, None)
                if set to `True` will display mono spaced fonts only, if set to `False`
                will only show regular fonts, if set to `None` will show everything
            families_only: bool
                will only display the family part of the UI
            font_dict: dict
                dictionary, like the one returned by the ``actual`` method of a ``Font`` object:
                    {'family': str,
                     'size': int,
                     'weight': 'bold'/'normal',
                     'slant': 'italic'/'roman',
                     'underline': bool,
                     'overstrike': bool}
            kwargs: dict
                additional keyword arguments to be passed to ``Toplevel.__init__``
        """
        super().__init__(master, **kwargs)
        self.title(title)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self._validate_family = self.register(self.validate_font_family)
        self._validate_size = self.register(self.validate_font_size)

        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=500)

        # --- variable storing the chosen font
        self.res = ""

        self.style = Style(self)
        self.style.configure("prev.TLabel", background="white")

        # --- family list
        if fixed_only is None:
            self.fonts = list(families())
        elif fixed_only:
            self.fonts = self._get_fixed_families()
        else:
            self.fonts = self._get_non_fixed_families()
        self.fonts.append("TkDefaultFont")
        self.fonts.sort()
        for i in range(len(self.fonts)):
            self.fonts[i] = self.fonts[i].replace(" ", "\ ")
        self.sizes = ["%i" % i for i in (list(range(6, 17)) + list(range(18, 32, 2)))]
        # --- font default
        font_dict["weight"] = font_dict.get("weight", "normal")
        font_dict["slant"] = font_dict.get("slant", "roman")
        font_dict["underline"] = font_dict.get("underline", False)
        font_dict["overstrike"] = font_dict.get("overstrike", False)
        font_dict["family"] = font_dict.get("family", self.fonts[0].replace("\ ", " "))
        self.passed_size = font_dict["size"] = font_dict.get("size", 10)

        # --- creation of the widgets
        # ------ style parameters (bold, italic ...)
        self.options_frame = Frame(self, relief="groove", borderwidth=2)
        self.font_family = StringVar(self, " ".join(self.fonts))
        self.font_size = StringVar(self, " ".join(self.sizes))
        self.var_bold = BooleanVar(self, font_dict["weight"] == "bold")
        self.b_bold = Checkbutton(
            self.options_frame,
            text=TR["Bold"],
            command=self.toggle_bold,
            variable=self.var_bold,
        )
        self.b_bold.grid(row=0, sticky="w", padx=4, pady=(4, 2))
        self.var_italic = BooleanVar(self, font_dict["slant"] == "italic")
        self.b_italic = Checkbutton(
            self.options_frame,
            text=TR["Italic"],
            command=self.toggle_italic,
            variable=self.var_italic,
        )
        self.b_italic.grid(row=1, sticky="w", padx=4, pady=2)
        self.var_underline = BooleanVar(self, font_dict["underline"])
        self.b_underline = Checkbutton(
            self.options_frame,
            text=TR["Underline"],
            command=self.toggle_underline,
            variable=self.var_underline,
        )
        self.b_underline.grid(row=2, sticky="w", padx=4, pady=2)
        self.var_overstrike = BooleanVar(self, font_dict["overstrike"])
        self.b_overstrike = Checkbutton(
            self.options_frame,
            text=TR["Overstrike"],
            variable=self.var_overstrike,
            command=self.toggle_overstrike,
        )
        self.b_overstrike.grid(row=3, sticky="w", padx=4, pady=(2, 4))
        # ------ Size and family
        self.var_size = StringVar(self)
        self.entry_family = Entry(
            self,
            validate="key",
            validatecommand=(self._validate_family, "%d", "%S", "%i", "%s", "%V"),
        )
        self.entry_size = Entry(
            self,
            width=8,
            validate="key",
            textvariable=self.var_size,
            validatecommand=(self._validate_size, "%d", "%P", "%V"),
        )
        self.list_family = Listbox(
            self,
            selectmode="browse",
            listvariable=self.font_family,
            highlightthickness=0,
            exportselection=False,
        )
        self.list_size = Listbox(
            self,
            selectmode="browse",
            listvariable=self.font_size,
            highlightthickness=0,
            exportselection=False,
            width=8,
        )
        self.scroll_family = Scrollbar(
            self, orient="vertical", command=self.list_family.yview
        )
        self.scroll_size = Scrollbar(
            self, orient="vertical", command=self.list_size.yview
        )
        self.preview_font = Font(self, **font_dict)
        if len(text) > 30:
            text = text[:30]
        self.preview = Label(
            self,
            relief="groove",
            style="prev.TLabel",
            text=text,
            font=self.preview_font,
            anchor="center",
        )

        # --- widget configuration
        self.list_family.configure(yscrollcommand=self.scroll_family.set)
        self.list_size.configure(yscrollcommand=self.scroll_size.set)

        self.entry_family.insert(0, font_dict["family"])
        self.entry_family.selection_clear()
        self.entry_family.icursor("end")
        self.entry_size.insert(0, font_dict["size"])

        try:
            i = self.fonts.index(self.entry_family.get().replace(" ", "\ "))
        except ValueError:
            # unknown font
            i = 0
        self.list_family.selection_clear(0, "end")
        self.list_family.selection_set(i)
        self.list_family.see(i)
        try:
            i = self.sizes.index(self.entry_size.get())
            self.list_size.selection_clear(0, "end")
            self.list_size.selection_set(i)
            self.list_size.see(i)
        except ValueError:
            # size not in list
            pass

        if families_only:
            self._families_only()
        else:
            self._full_ui()

        self.preview.grid(
            row=2,
            column=0,
            columnspan=5,
            sticky="eswn",
            padx=10,
            pady=(0, 10),
            ipadx=4,
            ipady=4,
        )

        button_frame = Frame(self)
        button_frame.grid(row=3, column=0, columnspan=5, pady=(0, 10), padx=10)

        self.okay_btn = Button(button_frame, text="Ok", command=self.ok)
        self.okay_btn.grid(row=0, column=0, padx=14, sticky="ew")
        self.cancel_btn = Button(button_frame, text=TR["Cancel"], command=self.quit)
        self.cancel_btn.grid(row=0, column=1, padx=14, sticky="ew")
        self.list_family.bind("<<ListboxSelect>>", self.update_entry_family)
        self.list_size.bind("<<ListboxSelect>>", self.update_entry_size, add=True)
        self.list_family.bind("<KeyPress>", self.keypress)
        self.entry_family.bind("<Return>", self.change_font_family)
        self.entry_family.bind("<Tab>", self.tab)
        self.entry_size.bind("<Return>", self.change_font_size)

        self.entry_family.bind("<Down>", self.down_family)
        self.entry_size.bind("<Down>", self.down_size)

        self.entry_family.bind("<Up>", self.up_family)
        self.entry_size.bind("<Up>", self.up_size)

        # bind Ctrl+A to select all instead of go to beginning
        self.bind_class("TEntry", "<Control-a>", self.select_all)

        self._update_widget_font_sizes()

        self.wait_visibility(self)
        self.grab_set()
        self.entry_family.focus_set()
        self.lift()

    def _update_widget_font_sizes(self):
        self._update_tk_widget_font_size()
        self._update_ttk_widget_font_size()

    def _update_tk_widget_font_size(self):
        for widget in (
            self.entry_family,
            self.entry_size,
            self.list_family,
            self.list_size,
        ):
            widget.configure(font=(None, self.passed_size))

    def _update_ttk_widget_font_size(self):
        self.style.configure(".", font=(None, self.passed_size))

    def _families_only(self):
        self.entry_family.grid(
            row=0, column=0, columnspan=4, sticky="ews", pady=(10, 1), padx=(10, 10)
        )
        self.list_family.grid(
            row=1, column=0, columnspan=3, sticky="nsew", pady=(1, 10), padx=(10, 0)
        )
        self.scroll_family.grid(
            row=1, column=3, sticky="nsw", pady=(1, 10), padx=(0, 10)
        )

    def _full_ui(self):
        self.entry_family.grid(
            row=0, column=0, columnspan=2, sticky="ews", pady=(10, 1), padx=(10, 0)
        )
        self.entry_size.grid(
            row=0, column=2, columnspan=2, sticky="ews", pady=(10, 1), padx=(10, 0)
        )
        self.list_family.grid(
            row=1, column=0, sticky="nsew", pady=(1, 10), padx=(10, 0)
        )
        self.list_size.grid(row=1, column=2, sticky="nsew", pady=(1, 10), padx=(10, 0))
        self.scroll_family.grid(row=1, column=1, sticky="nsw", pady=(1, 10))
        self.scroll_size.grid(row=1, column=3, sticky="nsw", pady=(1, 10))
        self.options_frame.grid(
            row=0, column=4, rowspan=2, padx=10, pady=10, ipadx=10, sticky="nsew"
        )

    def select_all(self, event):
        """Select all entry content."""
        event.widget.selection_range(0, "end")

    def keypress(self, event):
        """Select the first font whose name begin by the key pressed."""
        key = event.char.lower()
        l = [i for i in self.fonts if i[0].lower() == key]
        if l:
            i = self.fonts.index(l[0])
            self.list_family.selection_clear(0, "end")
            self.list_family.selection_set(i)
            self.list_family.see(i)
            self.update_entry_family()

    def up_family(self, event):
        """Navigate in the family listbox with up key."""
        try:
            i = self.list_family.curselection()[0]
            self.list_family.selection_clear(0, "end")
            if i <= 0:
                i = len(self.fonts)
            self.list_family.see(i - 1)
            self.list_family.select_set(i - 1)
        except TclError:
            self.list_family.selection_clear(0, "end")
            i = len(self.fonts)
            self.list_family.see(i - 1)
            self.list_family.select_set(i - 1)
        self.list_family.event_generate("<<ListboxSelect>>")

    def up_size(self, event):
        """Navigate in the size listbox with up key."""
        try:
            s = self.var_size.get()
            if s in self.sizes:
                i = self.sizes.index(s)
            elif s:
                sizes = list(self.sizes)
                sizes.append(s)
                sizes.sort(key=lambda x: int(x))
                i = sizes.index(s)
            else:
                i = 0
            self.list_size.selection_clear(0, "end")
            if i <= 0:
                i = len(self.sizes)
            self.list_size.see(i - 1)
            self.list_size.select_set(i - 1)
        except TclError:
            i = len(self.sizes)
            self.list_size.see(i - 1)
            self.list_size.select_set(i - 1)
        self.list_size.event_generate("<<ListboxSelect>>")

    def down_family(self, event):
        """Navigate in the family listbox with down key."""
        try:
            i = self.list_family.curselection()[0]
            self.list_family.selection_clear(0, "end")
            if i >= len(self.fonts):
                i = -1
            self.list_family.see(i + 1)
            self.list_family.select_set(i + 1)
        except TclError:
            self.list_family.selection_clear(0, "end")
            self.list_family.see(0)
            self.list_family.select_set(0)
        self.list_family.event_generate("<<ListboxSelect>>")

    def down_size(self, event):
        """Navigate in the size listbox with down key."""
        try:
            s = self.var_size.get()
            if s in self.sizes:
                i = self.sizes.index(s)
            elif s:
                sizes = list(self.sizes)
                sizes.append(s)
                sizes.sort(key=lambda x: int(x))
                i = sizes.index(s) - 1
            else:
                s = len(self.sizes) - 1
            self.list_size.selection_clear(0, "end")
            if i < len(self.sizes) - 1:
                self.list_size.selection_set(i + 1)
                self.list_size.see(i + 1)
            else:
                self.list_size.see(0)
                self.list_size.select_set(0)
        except TclError:
            self.list_size.selection_set(0)
        self.list_size.event_generate("<<ListboxSelect>>")

    def toggle_bold(self):
        """Update font preview weight."""
        b = self.var_bold.get()
        self.preview_font.configure(weight=["normal", "bold"][b])

    def toggle_italic(self):
        """Update font preview slant."""
        b = self.var_italic.get()
        self.preview_font.configure(slant=["roman", "italic"][b])

    def toggle_underline(self):
        """Update font preview underline."""
        b = self.var_underline.get()
        self.preview_font.configure(underline=b)

    def toggle_overstrike(self):
        """Update font preview overstrike."""
        b = self.var_overstrike.get()
        self.preview_font.configure(overstrike=b)

    def change_font_family(self, event=None):
        """Update font preview family."""
        family = self.entry_family.get()
        if family.replace(" ", "\ ") in self.fonts:
            self.preview_font.configure(family=family)

    def change_font_size(self, event=None):
        """Update font preview size."""
        size = int(self.var_size.get())
        self.preview_font.configure(size=size)

    def validate_font_size(self, d, ch, V):
        """Validation of the size entry content."""
        l = [i for i in self.sizes if i[: len(ch)] == ch]
        i = None
        if l:
            i = self.sizes.index(l[0])
        elif ch.isdigit():
            sizes = list(self.sizes)
            sizes.append(ch)
            sizes.sort(key=lambda x: int(x))
            i = min(sizes.index(ch), len(self.sizes))
        if i is not None:
            self.list_size.selection_clear(0, "end")
            self.list_size.selection_set(i)
            deb = self.list_size.nearest(0)
            fin = self.list_size.nearest(self.list_size.winfo_height())
            if V != "forced":
                if i < deb or i > fin:
                    self.list_size.see(i)
                return True
        if d == "1":
            return ch.isdigit()
        else:
            return True

    def tab(self, event):
        """Move at the end of selected text on tab press."""
        self.entry_family = event.widget
        self.entry_family.selection_clear()
        self.entry_family.icursor("end")
        return "break"

    def validate_font_family(self, action, modif, pos, prev_txt, V):
        """Completion of the text in the entry with existing font names."""
        if self.entry_family.selection_present():
            sel = self.entry_family.selection_get()
            txt = prev_txt.replace(sel, "")
        else:
            txt = prev_txt
        if action == "0":
            txt = txt[: int(pos)] + txt[int(pos) + 1 :]
            return True
        else:
            txt = txt[: int(pos)] + modif + txt[int(pos) :]
            ch = txt.replace(" ", "\ ").lower()
            l = [i for i in self.fonts if i[: len(ch)].lower() == ch]
            if l:
                i = self.fonts.index(l[0])
                self.list_family.selection_clear(0, "end")
                self.list_family.selection_set(i)
                deb = self.list_family.nearest(0)
                fin = self.list_family.nearest(self.list_family.winfo_height())
                index = self.entry_family.index("insert")
                self.entry_family.delete(0, "end")
                self.entry_family.insert(0, l[0].replace("\ ", " "))
                self.entry_family.selection_range(index + 1, "end")
                self.entry_family.icursor(index + 1)
                if V != "forced":
                    if i < deb or i > fin:
                        self.list_family.see(i)
                return True
            else:
                return False

    def update_entry_family(self, event=None):
        """Update family entry when an item is selected in the family listbox."""
        #  family = self.list_family.get("@%i,%i" % (event.x , event.y))
        family = self.list_family.get(self.list_family.curselection()[0])
        self.entry_family.delete(0, "end")
        self.entry_family.insert(0, family)
        self.entry_family.selection_clear()
        self.entry_family.icursor("end")
        self.change_font_family()

    def update_entry_size(self, event):
        """Update size entry when an item is selected in the size listbox."""
        #  size = self.list_size.get("@%i,%i" % (event.x , event.y))
        size = self.list_size.get(self.list_size.curselection()[0])
        self.var_size.set(size)
        self.change_font_size()

    def ok(self):
        """Validate choice."""
        self.res = self.preview_font.actual()
        self.quit()

    def get_res(self) -> dict:
        """Return chosen font."""
        return self.res

    def quit(self):
        self.destroy()

    @staticmethod
    def _get_fixed_families() -> List[families]:
        families_list = []
        for family in families():
            get_font = Font(family=family)
            if get_font.metrics("fixed"):
                families_list.append(family)
        return families_list

    @staticmethod
    def _get_non_fixed_families() -> List[families]:
        families_list = []
        for family in families():
            get_font = Font(family=family)
            if not get_font.metrics("fixed"):
                families_list.append(family)
        return families_list
