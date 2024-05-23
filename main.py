from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.text import LabelBase
from random import random
import time
from updater import get_latest_values

# Local imports
from resources.config import configure

config = configure.Configure('resources/config/config.ini')

TIME24 = config.get_bool(section='RCH', option='TIME24')

# Define a global URL
GLOBAL_OP25DATA = config.get(section='RCH', option='OP25_SERVER')
updater.initialize(GLOBAL_OP25SERVER)

class OutlinedBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_canvas()

    def setup_canvas(self):
        with self.canvas.before:
            # Set a random color
            self.color = Color(random(), random(), random(), 1)
            # Draw the outline
            self.rect = Line(width=1.5, rectangle=(self.x, self.y, self.width, self.height))
        # Bind to size and position changes
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.rectangle = (self.x, self.y, self.width, self.height)


class MainApp(MDApp):
    time_text = StringProperty()
    signal_icon = StringProperty()
    op25_server_address = StringProperty()
    original_color = ListProperty([1, 1, 1, 1])  # Default color
    system_county_label = ObjectProperty(None)  # Reference to the system_county label
    label_color_state = False  # False for original color, True for red

    def build(self):
        self.theme_cls.theme_style = "Light"  # Start with light theme
        self.theme_cls.primary_palette = "Purple"
        root = Builder.load_file("main.kv")
        LabelBase.register("digital", "resources/fonts/digital.ttf")
        LabelBase.register("material", "resources/fonts/material.ttf")
        self.system_county_label = root.ids.system_county  # Bind system_county_label to the label in KV
        Clock.schedule_once(self.delayed_theme_application)  # Apply dark theme after UI load
        Clock.schedule_interval(self.update_time, 1)  # Update time every second
        Clock.schedule_interval(self.update_large_display, 1) # Update large display once every second
        Clock.schedule_interval(self.update_signal_icon, 1)  # Update large display once every second
        return root

    def delayed_theme_application(self, dt):
        self.set_dark_theme()  # Change to dark theme after UI is built

    def update_config(self):
        config.set('RCH', 'TIME24', str(self.root.ids.time24_checkbox.active))
        config.set('RCH', 'OP25_SERVER', self.root.ids.op25_server_textbox.text)


    def hold_talkgroup(self):
        if self.label_color_state:  # If the label is currently red
            # Change the color back to the original color
            self.system_county_label.color = self.original_color
            self.root.ids.system_name.color = self.original_color  # Change system_name color
            self.root.ids.current_talkgroup.color = self.original_color  # Change current_talkgroup color
            self.label_color_state = False  # Update color state to original
        else:  # If the label is not red (original color)
            # Store original colors
            self.original_color = self.system_county_label.color
            original_color_system_name = self.root.ids.system_name.color
            original_color_talkgroup = self.root.ids.current_talkgroup.color

            # Change the color of all labels to red
            self.system_county_label.color = [1, 0, 0, 1]  # Red color
            self.root.ids.system_name.color = [1, 0, 0, 1]  # Red color
            self.root.ids.current_talkgroup.color = [1, 0, 0, 1]  # Red color

            self.label_color_state = True  # Update color state to red

    def set_dark_theme(self, *args):
        self.theme_cls.theme_style = "Dark"  # Switch to dark theme

    def update_time(self, *args):
        if TIME24:
            self.time_text = time.strftime("%H:%M:%S")  # 24H Time
        else:
            self.time_text = time.strftime("%I:%M:%S %p")  # 12H Time

    def update_signal_icon(self, *args):
        try:
            latest_values = get_latest_values(GLOBAL_OP25DATA)
            if latest_values and 'trunk_update' in latest_values:
                tsbks_value = latest_values['trunk_update'].get('tsbks')
                if tsbks_value is None:
                    self.signal_icon = "󰞃"  # Replace "default_icon" with the desired default icon
                else:
                    if int(tsbks_value) < 40:
                        self.signal_icon = "󰞃"
                    elif int(tsbks_value) >= 10000:
                        self.signal_icon = "󰢾"
                    elif int(tsbks_value) >= 2000:
                        self.signal_icon = "󰢽"
                    elif int(tsbks_value) >= 1000:
                        self.signal_icon = "󰢼"


                    else:
                        self.signal_icon = "󰞃"  # Default icon when tsbks_value >= 40
        except Exception as e:
            print(f"Error updating signal icon: {e}")


    def update_large_display(self, *args):
        try:
            # Call get_latest_values to retrieve the latest values
            latest_values = get_latest_values(GLOBAL_OP25DATA)

            #print("Latest values:", latest_values)  # Add this line to see what latest_values contains

            if latest_values is not None and 'trunk_update' in latest_values:
                system_name = latest_values['change_freq'].get('system')
                #print("Latest values:", latest_values)

                current_talkgroup = latest_values['change_freq'].get('tgid')

                # Update UI only if values are not None
                if system_name is not None:
                    self.root.ids.system_name.text = system_name
                if current_talkgroup is not None:
                    self.root.ids.current_talkgroup.text = str(current_talkgroup)
            else:
                # Handle the case where latest_values is None or 'trunk_update' key is not present
                self.root.ids.current_talkgroup.text = "No Active Call"
        except:
            pass

if __name__ == '__main__':
    app = MainApp()
    app.run()
