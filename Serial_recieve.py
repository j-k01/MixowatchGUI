import serial
import tkinter as tk
import time

class RFRec():
    def __init__(self, port, bps = 9600):
        self.port = port
        self.bps = bps
        self.sp = serial.Serial(self.port, self.bps)
        self.sp.flushInput()
        self.sp = None

    def readSerialLine(self):
        if self.sp.inWaiting() > 0:
            return self.sp.readline()
        else:
            return None
from PIL import Image
from PIL import ImageTk

class Bottle():
    def __init__(self, frame,tag, data):
        print('test')
        print(frame)
        self.canvas = tk.Canvas(frame, width = 100, height = 120)
        self.red = self.canvas.create_rectangle(0, 0, 100, 100, fill = 'white')
        self.green = self.canvas.create_rectangle(0,112-106*(float(data[1])/float(data[0])), 100, 112, fill='teal')
        self.name = tk.Label(frame, text=tag)
        self.name.pack()
        self.oz = tk.Label(frame, text="Remaining Oz: {}".format(data[1]))
        self.percent = tk.Label(frame, text="{:3f}%".format(float(data[1])/float(data[0])))
        
        img = Image.open("transparent.gif")
        img = img.resize((100,120), Image.ANTIALIAS)
        self.bottle_gif = ImageTk.PhotoImage(img)
        self.canvas.create_image(0,0, image = self.bottle_gif, anchor=tk.NW)
        self.name.grid(row=0, column=1)
        self.oz.grid(row=1, column = 1)

        self.percent.grid(row=2, column = 1)

        self.canvas.grid(row=0, column = 0, rowspan =5)
        
    def update(self):
        data = [20,60,40]
        #self.canvas.coords(self.green, 0,112-106*(float(data[2])/float(data[1])), 100, 112)
        
class App():
    def __init__(self, root):
        self.window = root
        self.sp = RFRec('/dev/ttyACM0',9600)
        self._createWidgets()
        self._createLayout()
        self.last_serial_read = None
        self.serial_delay = 20
        
        self.data = {}
        self._fillData()
        self._checkSerial()
        self.makeBottles()
        for bottle in self.bottles:
            bottle.update()

    def _createWidgets(self):
        self.recFrame =tk.Frame(self.window, width = 70, height = 100)
        self.recBox = tk.Listbox(self.recFrame, width = 40, height = 20)
        self.clearRec =tk.Button(self.window, text='CLEAR', command=self.clear)
    def _createLayout(self):
        self.recBox.pack()
        self.recFrame.grid(row=0, column=2, rowspan = 3)
        self.window.grid_columnconfigure(1, minsize=50)
        self.clearRec.grid(row=4, column =2)

    def _checkSerial(self):
        self.window.after(self.serial_delay, self._checkSerial)
        self.last_serial_read = self.sp.readSerialLine()
        if self.last_serial_read:
            self.addPour()
        self.last_serial_read = None
    
    def addPour(self,last_read):
        tag = self.last_serial_read.split()[0]
        self.last_serial_read = None
        timeout = time.time()
        while self.last_serial_read == None:
             self.last_serial_read = self.sp.readSerialLine()
             if ((time.time()-timeout)>1000):
                 break
        full = tag + ' ' +self.last_serial_read
        self.recBox.insert(tk.END, full)

    
            
    def _fillData(self):
        with open('database.txt', 'r') as d:
            for x in d:
                line = x.split(',')
                self.data[line[0]] = line[1:].copy()
                
    def makeBottles(self):
        self.bFrames = [(tk.Frame(self.window), data) for data in self.data]
        for x in range(len(self.bFrames)):
            self.bFrames[x][0].grid(row=x, column = 0)
        self.bottles = [Bottle(frame[0], frame[1], self.data[frame[1]]) for frame in self.bFrames]

            
                
    
    
    def clear(self):
        self.recBox.delete(0,tk.END)
        
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("800x400")
    root.title("Serial Reader")
    display = App(root)
    root.mainloop()




