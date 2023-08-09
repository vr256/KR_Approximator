import os
import tkinter

import customtkinter
from PIL import Image

from controllers import (
    approximate,
    change_dims,
    change_latex,
    change_locale,
    change_plot,
    change_pol_degrees,
    change_theme,
    get_text_results,
    make_plots,
)
from models import Locale, Theme
from tools.config import PATH_DARK, PATH_LIGHT, AppState
from tools.utils import load_locale

current_module = os.path.splitext(os.path.basename(__file__))[0]


class Sidebar(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._master = master
        self.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        self.loc = load_locale(current_module)
        self.logo_label = customtkinter.CTkLabel(
            self,
            text=self.loc["header"],
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=10, pady=(20, 10))
        self.info_label = customtkinter.CTkLabel(
            self,
            text=self.loc["info"],
            anchor="nw",
        )
        self.info_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 0))

        self.locale_label = customtkinter.CTkLabel(
            self,
            text=self.loc["locale_caption"],
            anchor="w",
        )
        self.locale_label.grid(row=4, column=0, padx=10, pady=(0, 30), sticky="sw")
        self.locale_optionemenu = customtkinter.CTkOptionMenu(
            self,
            values=self.loc["locales"],
            command=self.switch_locale,
        )
        self.locale_optionemenu.grid(row=4, column=0, padx=10, pady=(5, 0), sticky="s")

        self.appearance_mode_label = customtkinter.CTkLabel(
            self,
            text=self.loc["theme_caption"],
            anchor="w",
        )
        self.appearance_mode_label.grid(
            row=5,
            column=0,
            padx=10,
            pady=(10, 3),
            sticky="w",
        )
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self,
            values=self.loc["themes"],
            command=change_theme,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=10, pady=(0, 10))

    def switch_locale(self, new_loc: str):
        change_locale(new_loc)
        self._master.update_locale()

    def update_locale(self):
        self.loc = load_locale(current_module)
        self.logo_label.configure(text=self.loc["header"])
        self.info_label.configure(text=self.loc["info"])

        self.locale_label.configure(text=self.loc["locale_caption"])
        self.locale_optionemenu.configure(values=self.loc["locales"])
        selected_loc_index = [e.value for e in Locale].index(AppState().lang)
        self.locale_optionemenu.set(self.loc["locales"][selected_loc_index])

        self.appearance_mode_label.configure(text=self.loc["theme_caption"])
        self.appearance_mode_optionemenu.configure(values=self.loc["themes"])
        selected_theme_index = [e.value for e in Theme].index(AppState().theme)
        self.appearance_mode_optionemenu.set(self.loc["themes"][selected_theme_index])


class MainTabview(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._master = master
        self.loc = load_locale(current_module)
        self.grid(
            row=0,
            rowspan=2,
            column=1,
            columnspan=2,
            padx=(7, 0),
            pady=(7, 0),
            sticky="nsew",
        )
        self.res_tab_caption = self.loc["tabs"]["res_tab"]
        self.plot_tab_caption = self.loc["tabs"]["plot_tab"]
        self.add(self.res_tab_caption)
        self.add(self.plot_tab_caption)
        self.tab(self.plot_tab_caption).grid_columnconfigure(0, weight=1)
        self.tab(self.res_tab_caption).grid_columnconfigure(0, weight=1)

        self.results_textbox = customtkinter.CTkTextbox(self.tab(self.res_tab_caption))
        self.results_textbox.grid(row=0, padx=10, pady=5, sticky="nsew")
        self.results_textbox.pack(side="bottom", fill="both", expand="yes")

        plot_image = self.load_plot()
        self.results_plot = customtkinter.CTkLabel(
            self.tab(self.plot_tab_caption),
            text="",
            image=plot_image,
        )
        self.results_plot.pack(side="bottom", fill="both", expand="yes")

    def load_plot(self):
        """Load plot from file to image object"""
        make_plots()
        plot_image = customtkinter.CTkImage(
            light_image=Image.open(PATH_LIGHT),
            dark_image=Image.open(PATH_DARK),
            size=(490, 450),
        )
        return plot_image

    def update_locale(self):
        selected_tab = self.get()
        for tab_name, tab in self.loc["tabs"].items():
            if tab == selected_tab:
                selected_tab_name = tab_name

        self.loc = load_locale(current_module)
        new_res_tab_caption = self.loc["tabs"]["res_tab"]
        new_plot_tab_caption = self.loc["tabs"]["plot_tab"]

        self.delete(self.res_tab_caption)
        self.delete(self.plot_tab_caption)

        self.res_tab_caption = new_res_tab_caption
        self.plot_tab_caption = new_plot_tab_caption
        self.add(self.res_tab_caption)
        self.add(self.plot_tab_caption)

        self.tab(self.plot_tab_caption).grid_columnconfigure(0, weight=1)
        self.tab(self.res_tab_caption).grid_columnconfigure(0, weight=1)

        self.results_textbox = customtkinter.CTkTextbox(self.tab(self.res_tab_caption))
        self.results_textbox.grid(row=0, padx=10, pady=5, sticky="nsew")
        self.results_textbox.pack(side="bottom", fill="both", expand="yes")

        plot_image = self.load_plot()
        self.results_plot = customtkinter.CTkLabel(
            self.tab(self.plot_tab_caption),
            text="",
            image=plot_image,
        )
        self.results_plot.pack(side="bottom", fill="both", expand="yes")
        self.set(self.loc["tabs"][selected_tab_name])
        self._master.plot_selector.update_latex()


class PlotSelector(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._master = master
        self.loc = load_locale(current_module)
        self.grid(row=3, column=1, sticky="nsew", padx=(7, 0), pady=(12, 10))

        self.label_y_function_selector = customtkinter.CTkLabel(
            self,
            text=self.loc["plot_caption"],
        )
        self.label_y_function_selector.grid(row=2, column=1, padx=(10, 3), pady=5)
        self.cur_y = tkinter.StringVar(value="Y1")
        self.plot_y_function_optionmenu = customtkinter.CTkOptionMenu(
            self,
            variable=self.cur_y,
            values=["Y1", "Y2", "Y3", "Y4"],
            command=self.update_plot,
        )
        self.plot_y_function_optionmenu.grid(row=2, column=2, padx=10, pady=5)

        self.render_label = customtkinter.CTkLabel(self, text="Latex")
        self.render_label.grid(row=2, column=3, padx=(10, 5), pady=5)

        self.render_var = customtkinter.StringVar(value="off")
        self.latex_checkbox = customtkinter.CTkCheckBox(
            self,
            command=self.update_latex,
            text="",
            variable=self.render_var,
            onvalue="on",
            offvalue="off",
        )
        self.latex_checkbox.grid(row=2, column=4, padx=5, pady=5)

    def update_plot(self, new_plot: str):
        self.cur_y.set(new_plot)
        change_plot(new_plot)
        plot_image = self._master.main_tabview.load_plot()
        self._master.main_tabview.results_plot.configure(image=plot_image)
        self._master.main_tabview.results_plot.pack(
            side="bottom",
            fill="both",
            expand="yes",
        )

    def update_latex(self):
        change_latex(self.render_var.get() == "on")
        if hasattr(self._master.main_tabview, "latex"):
            self._master.main_tabview.results_textbox.delete("1.0", customtkinter.END)
            self._master.main_tabview.results_textbox.insert(
                "0.0",
                self._master.main_tabview.latex
                if AppState().latex
                else self._master.main_tabview.plain_text,
            )
            plot_image = self._master.main_tabview.load_plot()
            self._master.main_tabview.results_plot.configure(image=plot_image)
            self._master.main_tabview.results_plot.pack(
                side="bottom",
                fill="both",
                expand="yes",
            )

    def update_locale(self):
        self.loc = load_locale(current_module)
        self.label_y_function_selector.configure(text=self.loc["plot_caption"])
        (
            self._master.main_tabview.plain_text,
            self._master.main_tabview.latex,
        ) = get_text_results()
        self.update_latex()


class Approximator(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._master = master
        self.loc = load_locale(current_module)
        self.grid(row=3, column=2, padx=(6, 0), pady=(12, 10), sticky="nsew")
        self.calculate_y_button = customtkinter.CTkButton(
            self,
            text=self.loc["find_approx"],
            command=self.find_approx,
        )
        self.calculate_y_button.grid(row=0, padx=(35, 10), pady=5, sticky="nsew")
        self.calculate_y_button.pack(side="bottom", fill="both", expand="yes")

    def find_approx(self):
        degs = [
            int(self._master.polynom_view.__dict__[f"X{i}_deg"].get())
            for i in range(1, 3 + 1)
        ]
        dims = [
            int(self._master.vector_view.entry_Y_dim.get()),
            int(self._master.vector_view.entry_X1_dim.get()),
            int(self._master.vector_view.entry_X2_dim.get()),
            int(self._master.vector_view.entry_X3_dim.get()),
        ]
        change_pol_degrees(degs)
        change_dims(dims)
        (
            self._master.main_tabview.plain_text,
            self._master.main_tabview.latex,
        ) = approximate()
        self._master.plot_selector.update_latex()

    def update_locale(self):
        self.loc = load_locale(current_module)
        self.calculate_y_button.configure(text=self.loc["find_approx"])