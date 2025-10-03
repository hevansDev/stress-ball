"""
Stress-guage stress-ball
"""

import toga
import serial
from toga.style.pack import COLUMN, ROW, Pack
import threading
import time


class stressball(toga.App):
    def startup(self):
        """Construct and show the Toga application."""
        self.is_reading = False
        
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Button to start/stop reading
        self.read_button = toga.Button(
            'Start Reading',
            on_press=self.toggle_reading,
            style=Pack(padding=5)
        )
        main_box.add(self.read_button)
        
        # Label to show data
        self.data_label = toga.Label(
            'Press button to start reading',
            style=Pack(padding=10)
        )
        main_box.add(self.data_label)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    
    def toggle_reading(self, widget):
        """Start or stop reading from the gauge."""
        if self.is_reading:
            self.is_reading = False
            self.read_button.text = 'Start Reading'
        else:
            self.is_reading = True
            self.read_button.text = 'Stop Reading'
            # Start reading in background thread
            threading.Thread(target=self.read_loop, daemon=True).start()
    
    def read_loop(self):
        """Continuously read from the stress gauge."""
        try:
            ser = serial.Serial('/dev/cu.usbmodem1201', baudrate=115200, timeout=1)
            
            while self.is_reading:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    print(f"Received: {line}")
                    # Update label safely on main thread
                    self.update_label(f"Received: {line}")
                else:
                    time.sleep(0.01)  # Small delay to avoid spinning
            
            ser.close()
        except Exception as e:
            print(f"Error: {e}")
            self.update_label(f"Error: {e}")
            self.is_reading = False
    
    def update_label(self, text):
        """Thread-safe method to update the label."""
        def _update(widget, **kwargs):
            self.data_label.text = text
        
        self.add_background_task(_update)


def main():
    return stressball()