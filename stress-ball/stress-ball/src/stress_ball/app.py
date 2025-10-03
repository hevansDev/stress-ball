"""
Stress-gauge with canvas gauge and image visualization
"""

import toga
import serial
from toga.style.pack import COLUMN, Pack, BOLD
import threading
import time
import asyncio


class stressball(toga.App):
    def startup(self):
        """Construct and show the Toga application."""
        self.is_reading = True
        self.current_value = 0
        self.event_loop = asyncio.get_event_loop()
        
        self.stress_levels = [
            {"min": 0, "max": 200, "image": "level0.png", "label": "Relaxed"},
            {"min": 201, "max": 400, "image": "level1.png", "label": "Light Pressure"},
            {"min": 401, "max": 600, "image": "level2.png", "label": "Medium Pressure"},
            {"min": 601, "max": 750, "image": "level3.png", "label": "Heavy Pressure"},
            {"min": 751, "max": 1000, "image": "level4.png", "label": "Maximum Squeeze!"},
        ]
        
        main_box = toga.Box(
            style=Pack(direction=COLUMN, padding=10, alignment='center', background_color='#ced9ed')
        )
        
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
        
        # Canvas gauge - wider to accommodate overflow
        self.canvas = toga.Canvas(style=Pack(width=350, height=100, padding=10))
        self.draw_gauge(0)
        
        main_box.add(self.image_view)
        main_box.add(self.canvas)
        
        self.main_window = toga.MainWindow(title=self.formal_name, size=(370, 500))
        self.main_window.content = main_box
        self.main_window.show()
        
        threading.Thread(target=self.read_loop, daemon=True).start()

    def draw_gauge(self, value):
        """Draw a loading bar style gauge."""
        ctx = self.canvas.context
        
        # Clear the entire canvas
        ctx.begin_path()
        ctx.rect(0, 0, 350, 100)
        ctx.fill('#ced9ed')
        
        bar_x = 45  # Centered in 350px canvas
        bar_width = 260
        bar_y = 30
        bar_height = 40
        
        # Draw background bar
        ctx.begin_path()
        ctx.rect(bar_x, bar_y, bar_width, bar_height)
        ctx.fill('lightgray')
        
        # Scale: 0-750 maps to bar width, overflow up to 50px
        fill_width = (value / 750) * bar_width
        fill_width = min(fill_width, bar_width + 50)  # Allow 50px overflow
        
        # Color based on value
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
        
        # Draw filled portion
        if fill_width > 0:
            ctx.begin_path()
            ctx.rect(bar_x, bar_y, fill_width, bar_height)
            ctx.fill(color)
        
        # Draw border
        ctx.begin_path()
        ctx.rect(bar_x, bar_y, bar_width, bar_height)
        ctx.stroke('black', line_width=2)
        
        # Draw tick marks
        tick_values = [0, 150, 300, 450, 600, 750]
        for val in tick_values:
            x = bar_x + (val / 750) * bar_width
            
            ctx.begin_path()
            ctx.move_to(x, bar_y)
            ctx.line_to(x, bar_y - 10)
            ctx.stroke('black', line_width=2)
            
            offset = 15 if val >= 100 else 10
            ctx.begin_path()
            ctx.write_text(str(val), x - offset, bar_y - 15)
    
    def read_loop(self):
        """Continuously read from the stress gauge with auto-reconnect."""
        while self.is_reading:
            try:
                # Auto-detect Pico port
                port = self.find_pico_port()
                if not port:
                    print("Waiting for Pico...")
                    time.sleep(2)  # Wait before trying again
                    continue
                
                print(f"Connecting to Pico on {port}")
                ser = serial.Serial(port, baudrate=115200, timeout=1)
                
                # Read loop - will exit if device disconnects
                while self.is_reading:
                    try:
                        if ser.in_waiting > 0:
                            line = ser.readline().decode('utf-8').strip()
                            
                            try:
                                value = float(line)
                                self.current_value = value
                                self.update_gauge(value)
                                self.update_image_for_value(value)
                            except ValueError:
                                pass
                        else:
                            time.sleep(0.01)
                    except (serial.SerialException, OSError):
                        # Device disconnected
                        print("Pico disconnected, waiting for reconnect...")
                        break
                
                ser.close()
                
            except (serial.SerialException, OSError) as e:
                # Failed to connect or device disconnected
                print(f"Connection error: {e}")
                time.sleep(2)  # Wait before retrying

    def find_pico_port(self):
        """Find the Raspberry Pi Pico USB port automatically."""
        import serial.tools.list_ports
        
        ports = serial.tools.list_ports.comports()
        
        # Look for Pico by manufacturer or device pattern
        for port in ports:
            if 'usb' in port.device.lower():
                # Check for MicroPython or Raspberry Pi manufacturer
                if port.manufacturer and ('micropython' in port.manufacturer.lower() or 
                                        'raspberry' in port.manufacturer.lower()):
                    return port.device
                # Check description
                if 'pico' in str(port.description).lower() or 'board in fs mode' in str(port.description).lower():
                    return port.device
                # Any usbmodem device
                if 'usbmodem' in port.device.lower():
                    return port.device
        
        return None
    
    def loop_call(self, func):
        self.event_loop.call_soon_threadsafe(func)
    
    def update_gauge(self, value):
        self.loop_call(lambda: self.draw_gauge(value))
    
    def update_image_for_value(self, value):
        for level in self.stress_levels:
            if level["min"] <= value <= level["max"]:
                def update():
                    try:
                        if hasattr(self.image_view, 'image'):
                            self.image_view.image = toga.Image(self.paths.app / "resources" / level["image"])
                    except Exception as e:
                        print(f"Error updating image: {e}")
                
                self.loop_call(update)
                break


def main():
    return stressball()