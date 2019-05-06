import serial
import tkinter as tk

class RFRec():
    def __init__(self, port, bps = 9600):
        self.port = port
        self.bps = bps
        self.sp = serial.Serial(self.port, self.bps)
        self.sp.flushInput()

    def readSerialLine(self):
        if self.sp.inWaiting() > 0:
            return self.sp.readline()
        else:
            return None


class App():
    def __init__(self, root):
        self.window = root
        self.sp = RFRec('/dev/ttyACM0',9600)
        self._createWidgets()
        self._createLayout()
        self.last_serial_read = None
        self.serial_delay = 20
        self._checkSerial()

    def _createWidgets(self):
        self.recBox = tk.Listbox(self.window)
        self.clearRec =tk.Button(self.window, text='CLEAR', command=self.clear)
    def _createLayout(self):
        self.recBox.grid(row=1, column=1)
        self.clearRec.grid(row=5, columns =1)

    def _checkSerial(self):
        self.window.after(self.serial_delay, self._checkSerial)
        self.last_serial_read = self.sp.readSerialLine()
        if self.last_serial_read:
            self.recBox.insert(tk.END, self.last_serial_read[:-2])
        self.last_serial_read = None
    
    def clear(self):
        self.recBox.delete(0,tk.END)
        
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("400x400")
    root.title("Serial Reader")
    display = App(root)
    root.mainloop()




