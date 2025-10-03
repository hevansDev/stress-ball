"""
Stress-gauge with canvas gauge and image visualization
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
            {"min": 601, "max": 750, "image": "level3.png", "label": "Heavy Pressure"},
            {"min": 750, "max": 1000, "image": "level4.png", "label": "Maximum Squeeze!"},
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
        
        # Canvas gauge
        self.canvas = toga.Canvas(style=Pack(width=600, height=100, padding=10))
        self.draw_gauge(0)
        
        # Image display
        try:
            self.image_view = toga.ImageView(
                image=toga.Image(self.paths.app / "resources" / self.stress_levels[0]["image"]),
                style=Pack(padding=10, width=300, height=300)
            )
        except Exception as e:
            print(f"Error loading image: {e}")
            self.image_view = toga.Label(
                'Images not found',
                style=Pack(padding=20, font_size=14)
            )
        
        main_box.add(control_box)
        main_box.add(self.value_label)
        main_box.add(self.status_label)
        main_box.add(self.image_view)
        main_box.add(self.canvas)
        
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    
    def draw_gauge(self, value):
        """Draw a loading bar style gauge."""
        ctx = self.canvas.context
        
        ctx.begin_path()
        ctx.rect(0, 0, 600, 100)
        ctx.fill('white')
        
        ctx.begin_path()
        ctx.rect(50, 30, 500, 40)
        ctx.fill('lightgray')
        
        fill_width = min((value / 1000) * 500, 500)
        
        if value < 200:
            color = 'green'
        elif value < 400:
            color = 'lightgreen'
        elif value < 600:
            color = 'yellow'
        elif value < 800:
            color = 'orange'
        else:
            color = 'red'
        
        if fill_width > 0:
            ctx.begin_path()
            ctx.rect(50, 30, fill_width, 40)
            ctx.fill(color)
        
        ctx.begin_path()
        ctx.rect(50, 30, 500, 40)
        ctx.stroke('black', line_width=2)
        
        for i in range(0, 11):
            x = 50 + (i * 50)
            label_value = i * 100
            
            if i % 2 == 0:
                ctx.begin_path()
                ctx.move_to(x, 30)
                ctx.line_to(x, 20)
                ctx.stroke('black', line_width=2)
                
                ctx.begin_path()
                ctx.write_text(str(label_value), x - 15, 10)
            else:
                ctx.begin_path()
                ctx.move_to(x, 30)
                ctx.line_to(x, 25)
                ctx.stroke('gray', line_width=1)
    
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
                        self.update_gauge(value)
                        self.update_image_for_value(value)
                    except ValueError:
                        pass
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
    
    def update_gauge(self, value):
        self.loop_call(lambda: self.draw_gauge(value))
    
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
