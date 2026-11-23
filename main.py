import threading
import customtkinter as ctk
from helper import CITIES, fetch_weather

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SMHIWeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SMHI Väder")
        self.geometry("480x820")
        self.minsize(440, 700)

        self.selected_city = "Vallentuna"

        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=12, pady=12)

        self._build_header()
        self._build_current_card()
        self._build_hourly_section()
        self._build_daily_section()

        self.load_weather_async()

    def _build_header(self):
        header = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        self.city_menu = ctk.CTkOptionMenu(
            header,
            values=list(CITIES.keys()),
            command=self.on_city_change,
            width=180,
            height=36,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.city_menu.set(self.selected_city)
        self.city_menu.pack(side="left")

        self.theme_button = ctk.CTkButton(
            header,
            text="☀️ / 🌙",
            width=60,
            height=36,
            fg_color=("gray80", "gray25"),
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray35"),
            command=self.toggle_appearance_mode,
        )
        self.theme_button.pack(side="right", padx=(6, 0))

        self.refresh_button = ctk.CTkButton(
            header,
            text="↻",
            width=40,
            height=36,
            fg_color=("gray80", "gray25"),
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray35"),
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.load_weather_async,
        )
        self.refresh_button.pack(side="right")

    def _build_current_card(self):
        self.current_card = ctk.CTkFrame(
            self.main_scroll,
            corner_radius=16,
            fg_color=("#E8F1FA", "#1B2838"),
        )
        self.current_card.pack(fill="x", pady=(0, 14))

        self.city_label = ctk.CTkLabel(
            self.current_card,
            text=self.selected_city,
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.city_label.pack(pady=(16, 0))

        self.status_label = ctk.CTkLabel(
            self.current_card,
            text="Hämtar prognos...",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray70"),
        )
        self.status_label.pack(pady=(2, 8))

        temp_row = ctk.CTkFrame(self.current_card, fg_color="transparent")
        temp_row.pack(pady=4)

        self.current_icon_label = ctk.CTkLabel(
            temp_row,
            text="⏳",
            font=ctk.CTkFont(size=54),
        )
        self.current_icon_label.pack(side="left", padx=(0, 12))

        self.current_temp_label = ctk.CTkLabel(
            temp_row,
            text="--°",
            font=ctk.CTkFont(size=56, weight="bold"),
        )
        self.current_temp_label.pack(side="left")

        self.current_desc_label = ctk.CTkLabel(
            self.current_card,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.current_desc_label.pack(pady=(2, 10))

        details_frame = ctk.CTkFrame(
            self.current_card,
            corner_radius=10,
            fg_color=("#D6E6F5", "#243447"),
        )
        details_frame.pack(fill="x", padx=16, pady=(0, 16))

        self.wind_label = ctk.CTkLabel(
            details_frame,
            text="💨 Vind: -- m/s",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.wind_label.pack(side="left", expand=True, pady=10)

        self.precip_label = ctk.CTkLabel(
            details_frame,
            text="💧 Nederbörd: -- mm/h",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.precip_label.pack(side="right", expand=True, pady=10)

    def _build_hourly_section(self):
        title = ctk.CTkLabel(
            self.main_scroll,
            text="Timme för timme",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        title.pack(fill="x", pady=(0, 6))

        # Ökat höjden något för att rymma textbeskrivningen
        self.hourly_scroll = ctk.CTkScrollableFrame(
            self.main_scroll,
            orientation="horizontal",
            height=145,
            corner_radius=14,
            fg_color=("gray90", "#1E1E1E"),
        )
        self.hourly_scroll.pack(fill="x", pady=(0, 14))

    def _build_daily_section(self):
        title = ctk.CTkLabel(
            self.main_scroll,
            text="10-dygnsprognos",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        title.pack(fill="x", pady=(0, 6))

        self.daily_container = ctk.CTkFrame(
            self.main_scroll,
            corner_radius=14,
            fg_color=("gray90", "#1E1E1E"),
        )
        self.daily_container.pack(fill="x", pady=(0, 10))

    def toggle_appearance_mode(self):
        current_mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")

    def on_city_change(self, new_city):
        self.selected_city = new_city
        self.load_weather_async()

    def load_weather_async(self):
        self.city_label.configure(text=self.selected_city)
        self.status_label.configure(text="Uppdaterar från SMHI...")
        lat, lon = CITIES[self.selected_city]

        def worker():
            try:
                weather_data = fetch_weather(lat, lon)
                self.after(0, lambda: self.update_ui(weather_data))
            except Exception as exc:
                self.after(0, lambda: self.status_label.configure(text=f"Kunde inte hämta data: {exc}"))

        threading.Thread(target=worker, daemon=True).start()

    def update_ui(self, data):
        current = data["current"]
        if not current:
            self.status_label.configure(text="Ingen väderdata tillgänglig")
            return

        # 1. Uppdatera nuvarande väder
        self.status_label.configure(text=f"Prognos kl. {current['hour']}")
        self.current_icon_label.configure(text=current["icon"])
        self.current_temp_label.configure(text=f"{current['temp']}°")
        self.current_desc_label.configure(text=current["desc"])
        self.wind_label.configure(text=f"💨 Vind: {current['wind']} m/s")
        self.precip_label.configure(text=f"💧 Nederbörd: {current['precip']} mm/h")

        # 2. Uppdatera timprognosen (med bredare kort och textbeskrivning)
        for widget in self.hourly_scroll.winfo_children():
            widget.destroy()

        for item in data["hourly"]:
            card = ctk.CTkFrame(
                self.hourly_scroll,
                width=100,
                height=130,
                corner_radius=10,
                fg_color=("gray82", "#2A2A2A"),
            )
            card.pack(side="left", padx=4, pady=4)
            card.pack_propagate(False)

            ctk.CTkLabel(card, text=item["hour"], font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 1))
            ctk.CTkLabel(card, text=item["icon"], font=ctk.CTkFont(size=20)).pack(pady=1)
            
            # Beskrivningstext (t.ex. "Kraftigt snöfall" eller "Lätt regn") med radbrytning
            ctk.CTkLabel(
                card,
                text=item["desc"],
                font=ctk.CTkFont(size=9),
                text_color=("gray30", "gray75"),
                wraplength=92,
            ).pack(pady=(1, 2))

            ctk.CTkLabel(
                card,
                text=f"{item['temp']}°",
                font=ctk.CTkFont(size=13, weight="bold"),
            ).pack(pady=(1, 0))

            precip_text = f"{item['precip']} mm" if item["precip"] > 0 else ""
            ctk.CTkLabel(
                card,
                text=precip_text,
                font=ctk.CTkFont(size=10),
                text_color=("#1F6AA5", "#6CB4EE"),
            ).pack()

        # 3. Uppdatera 10-dygnsprognosen
        for widget in self.daily_container.winfo_children():
            widget.destroy()

        for idx, day in enumerate(data["daily"]):
            row = ctk.CTkFrame(self.daily_container, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=8)

            day_col = ctk.CTkFrame(row, fg_color="transparent", width=95)
            day_col.pack(side="left")
            day_col.pack_propagate(False)

            ctk.CTkLabel(
                day_col,
                text=day["day"],
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
            ).pack(fill="x")
            ctk.CTkLabel(
                day_col,
                text=day["date"],
                font=ctk.CTkFont(size=11),
                text_color=("gray40", "gray65"),
                anchor="w",
            ).pack(fill="x")

            weather_desc_col = ctk.CTkFrame(row, fg_color="transparent")
            weather_desc_col.pack(side="left", padx=6, expand=True, anchor="w")

            icon_desc_row = ctk.CTkFrame(weather_desc_col, fg_color="transparent")
            icon_desc_row.pack(anchor="w")

            ctk.CTkLabel(
                icon_desc_row,
                text=day["icon"],
                font=ctk.CTkFont(size=20),
            ).pack(side="left", padx=(0, 6))

            ctk.CTkLabel(
                icon_desc_row,
                text=day["desc"],
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
            ).pack(side="left")

            info_text = f"💧 {day['precip']} mm   💨 {day['wind']} m/s"
            ctk.CTkLabel(
                weather_desc_col,
                text=info_text,
                font=ctk.CTkFont(size=11),
                text_color=("gray40", "gray70"),
                anchor="w",
            ).pack(anchor="w", pady=(1, 0))

            temp_frame = ctk.CTkFrame(row, fg_color="transparent")
            temp_frame.pack(side="right")

            max_color = "#E05A47" if day["max_temp"] > 0 else "#4DA6FF"
            min_color = "#E05A47" if day["min_temp"] > 0 else "#4DA6FF"

            ctk.CTkLabel(
                temp_frame,
                text=f"{day['max_temp']}°",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=max_color,
                width=36,
            ).pack(side="left")

            ctk.CTkLabel(
                temp_frame,
                text=f"{day['min_temp']}°",
                font=ctk.CTkFont(size=14),
                text_color=min_color,
                width=36,
            ).pack(side="left")

            if idx < len(data["daily"]) - 1:
                sep = ctk.CTkFrame(self.daily_container, height=1, fg_color=("gray80", "gray28"))
                sep.pack(fill="x", padx=12)


if __name__ == "__main__":
    app = SMHIWeatherApp()
    app.mainloop()