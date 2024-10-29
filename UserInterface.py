import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror
from serial import Serial, SerialException
from serial.tools.list_ports import comports
from threading import Thread, Lock

# Constants for device responses
S_OK = 0xaa
S_ERR = 0xff

# Decorator to make callbacks run in separate threads
def detached_callback(f):
    return lambda *args, **kwargs: Thread(target=f, args=args, kwargs=kwargs).start()

# A thread-safe serial class
class LockedSerial(Serial):
    _lock = Lock()

    def read(self, size=1) -> bytes:
        with self._lock:
            return super().read(size)

    def write(self, b: bytes) -> int:
        with self._lock:
            return super().write(b)

    def close(self):
        with self._lock:
            super().close()

# Serial connection selection popup
class SerialPortal(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.withdraw()  # Hide main app window until connected

        # Serial port options menu
        self.port_var = tk.StringVar()
        ttk.OptionMenu(self, self.port_var, '', *[port.device for port in comports()]).pack()
        ttk.Button(self, text='Connect', command=self.connect, default='active').pack()

    def connect(self):
        try:
            self.parent.ser = LockedSerial(self.port_var.get(), 9600)
            self.destroy()
            self.parent.deiconify()  # Show the main app window
        except SerialException:
            showerror('Connection Error', 'Could not open the selected port.')

# Main application
class App(tk.Tk):
    ser: LockedSerial

    def __init__(self):
        super().__init__()
        self.title("LED Blinker")

        self.port = tk.StringVar()
        self.led = tk.BooleanVar()  # Checkbox state

        # UI elements
        ttk.Checkbutton(self, text='Toggle LED', variable=self.led, command=self.update_led).pack()
        ttk.Button(self, text='Send Invalid', command=self.send_invalid).pack()
        ttk.Button(self, text='Disconnect', command=self.disconnect, default='active').pack()

        # Open serial selection popup
        SerialPortal(self)

    def write(self, b: bytes):
        try:
            self.ser.write(b)
            response = int.from_bytes(self.ser.read(), 'big')
            if response == S_ERR:
                showerror('Device Error', 'The device reported an invalid command.')
        except SerialException:
            showerror('Serial Error', 'Write failed.')

    @detached_callback
    def update_led(self):
        self.write(bytes([self.led.get()]))

    @detached_callback
    def send_invalid(self):
        self.write(bytes([0x10]))

    def disconnect(self):
        if hasattr(self, 'ser'):
            self.ser.close()
            SerialPortal(self)  # Show serial selection popup again

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.disconnect()

# Run the application
if __name__ == '__main__':
    with App() as app:
        app.mainloop()
