"""
Stress-gauge stress-ball visualizer
"""

import toga
import serial
from toga.style.pack import COLUMN, ROW, Pack, BOLD
import threading
import time
import asyncio


class stressball(toga.App):
    def startup(self):
        """Construct and show the Toga application."""
        self.is_reading = False
        self.current_value = 0
        self.event_loop = asyncio.get_event_loop()
        
        self.stress_levels = [
            {"min": 0, "max": 200, "image": "level0.png", "label": "Relaxed"},
            {"min": 201, "max": 400, "image": "level1.png", "label": "Light Pressure"},
            {"min": 401, "max": 600, "image": "level2.png", "label": "Medium Pressure"},
            {"min": 601, "max": 700, "image": "level3.png", "label": "Heavy Pressure"},
            {"min": 701, "max": 1000, "image": "level4.png", "label": "Maximum Squeeze!"},
        ]
        
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        control_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        self.read_button = toga.Button(
            'Start Reading',
            on_press=self.toggle_reading,
            style=Pack(padding=5, flex=1)
        )
        control_box.add(self.read_button)
        
        self.value_label = toga.Label(
            'Value: ---',
            style=Pack(padding=10, font_size=24, font_weight=BOLD)
        )
        
        self.status_label = toga.Label(
            'Not Connected',
            style=Pack(padding=5, font_size=16)
        )
        
        try:
            self.image_view = toga.ImageView(
                image=toga.Image(self.paths.app / "resources" / self.stress_levels[0]["image"]),
                style=Pack(padding=10, width=400, height=400)
            )
        except Exception as e:
            print(f"Error loading image: {e}")
            self.image_view = toga.Label(
                '🎯\n\nImages not found!',
                style=Pack(padding=20, font_size=14)
            )
        
        main_box.add(control_box)
        main_box.add(self.value_label)
        main_box.add(self.status_label)
        main_box.add(self.image_view)
        
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    
    def toggle_reading(self, widget):
        if self.is_reading:
            self.is_reading = False
            self.read_button.text = 'Start Reading'
            self.status_label.text = 'Disconnected'
        else:
            self.is_reading = True
            self.read_button.text = 'Stop Reading'
            self.status_label.text = 'Connecting...'
            threading.Thread(target=self.read_loop, daemon=True).start()
    
    def read_loop(self):
        try:
            ser = serial.Serial('/dev/cu.usbmodem1201', baudrate=115200, timeout=1)
            self.loop_call(lambda: setattr(self.status_label, 'text', 'Connected'))
            
            while self.is_reading:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    
                    try:
                        value = float(line)
                        self.current_value = value
                        self.update_value(value)
                        self.update_image_for_value(value)
                    except ValueError:
                        print(f"Invalid data: {line}")
                else:
                    time.sleep(0.01)
            
            ser.close()
            self.loop_call(lambda: setattr(self.status_label, 'text', 'Disconnected'))
            
        except Exception as e:
            print(f"Error: {e}")
            self.loop_call(lambda: setattr(self.status_label, 'text', f"Error: {e}"))
            self.is_reading = False
            self.loop_call(lambda: setattr(self.read_button, 'text', 'Start Reading'))
    
    def loop_call(self, func):
        self.event_loop.call_soon_threadsafe(func)
    
    def update_value(self, value):
        self.loop_call(lambda: setattr(self.value_label, 'text', f"Value: {int(value)}"))
    
    def update_image_for_value(self, value):
        for level in self.stress_levels:
            if level["min"] <= value <= level["max"]:
                def update():
                    try:
                        if hasattr(self.image_view, 'image'):
                            self.image_view.image = toga.Image(self.paths.app / "resources" / level["image"])
                        self.status_label.text = f"Connected - {level['label']}"
                    except Exception as e:
                        print(f"Error updating image: {e}")
                
                self.loop_call(update)
                break


def main():
    return stressball()