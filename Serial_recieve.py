import serial
import tkinter as tk
import time
from datetime import datetime

class RFRec():
    def __init__(self, port, bps = 9600):
        self.port = port
        self.bps = bps
        self.sp = serial.Serial(self.port, self.bps)
        #print(self.sp)
        self.sp.flushInput()
        #self.sp = None

    def readSerialLine(self):
        if self.sp.inWaiting() > 0:
            return self.sp.readline()
        else:
            return None
from PIL import Image
from PIL import ImageTk

class Bottle():
    def __init__(self, frame,tag, data):
        self.data = data
        self.oz_var = tk.StringVar()
        self.percent_var = tk.StringVar()
        self.canvas = tk.Canvas(frame, width = 100, height = 120)
        self.red = self.canvas.create_rectangle(0, 0, 100, 100, fill = 'white')
        self.green = self.canvas.create_rectangle(0,112-106*(float(data[1])/float(data[0])), 100, 112, fill='teal')
        self.name = tk.Label(frame, text=tag)
        self.name.pack()
        self.oz_var.set("Remaining Oz: {}".format(data[1]))
        self.percent_var.set("{:3f}%".format(data[1]/data[0]))
        self.oz = tk.Label(frame, textvariable=self.oz_var)
        self.percent = tk.Label(frame, textvariable=self.percent_var)

        img = Image.open("transparent.gif")
        img = img.resize((100,120), Image.ANTIALIAS)
        self.bottle_gif = ImageTk.PhotoImage(img)
        self.canvas.create_image(0,0, image = self.bottle_gif, anchor=tk.NW)
        self.name.grid(row=0, column=1)
        self.oz.grid(row=1, column = 1)

        self.percent.grid(row=2, column = 1)

        self.canvas.grid(row=0, column = 0, rowspan =5)
        
    def update(self):
        #data = [20,60,40]
        self.canvas.coords(self.green, 0,112-106*(float(self.data[1])/float(self.data[0])), 100, 112)
        self.oz_var.set("Remaining Oz: {:.2f}".format(self.data[1]))
        self.percent_var.set("{:.1f}%".format(100*self.data[1]/self.data[0]))
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
       # self._checkSerial()
        self.makeBottles()
        for bottle in self.bottles:
            bottle.update()
        self._checkSerial()
    
    def _createWidgets(self):
        self.recFrame =tk.Frame(self.window, width = 70, height = 100)
        self.scrollRec = tk.Scrollbar(self.recFrame, orient = 'vertical')
        self.recBox = tk.Listbox(self.recFrame, width = 40, height = 20, yscrollcommand=self.scrollRec.set)
        self.clearRec =tk.Button(self.window, text='CLEAR', command=self.clear)

        logo = Image.open("mixowatch_logo.png")
        logo = logo.resize((120,120), Image.ANTIALIAS)
        self.logo = ImageTk.PhotoImage(logo)
        self.logo_canvas = tk.Canvas(self.window, width = 120, height = 120)
        self.logo_canvas.create_image(0,0, anchor=tk.NW, image=self.logo)
        self.quit = tk.Button(self.window, text='QUIT', command=self.window.destroy)

    def _createLayout(self):
        self.quit.grid(row=4, column = 4)
        self.recBox.pack(side = tk.LEFT)
        self.scrollRec.config(command = self.recBox.yview)
        self.scrollRec.pack(side = tk.RIGHT, fill=tk.Y)
        self.recFrame.grid(row=0, column=2, rowspan = 3)
        self.window.grid_columnconfigure(1, minsize=50)
        self.window.grid_columnconfigure(3, minsize=30)
        self.clearRec.grid(row=4, column =2)
        self.logo_canvas.grid(row = 1, column = 4)

    def _checkSerial(self):
        self.window.after(self.serial_delay, self._checkSerial)
        self.last_serial_read = self.sp.readSerialLine()
        if self.last_serial_read:
            self.addPour()
        self.last_serial_read = None
    
    def addPour(self):
        cur_time = datetime.now().strftime('%H:%M:%S  |   %Y-%m-%d')
        tag = self.last_serial_read.split()[1]
        self.last_serial_read = None
        timeout = time.time()
        while self.last_serial_read == None:
             self.last_serial_read = self.sp.readSerialLine()
             if ((time.time()-timeout)>1000):
                 break
        tag = "".join(map(chr,tag))
        tagline = "Tag : " + tag
        oz = "{:.3f} Oz".format(float(self.last_serial_read)/1000/1.507)
        newline = '{:<12}|{:^10}|{:>27}'.format(tagline, oz, cur_time) 
        update_data = self.data[tag][1] - float(self.last_serial_read)/1000/1.507
        if (update_data > 0):
            self.data[tag][1] = update_data
            self.recBox.insert(tk.END, newline)
            self.recBox.select_clear(self.recBox.size()-2)
            self.recBox.select_set(tk.END)
            self.recBox.yview(tk.END)
        else:
            self.data[tag][1] = 0
        for bottle in self.bottles:
            bottle.update()

        with open('database.txt', 'w') as f:
            for tag in self.data:
                line = "Tag {},{},{}\n".format(tag, self.data[tag][0], self.data[tag][1])
                f.write(line)
        
    
            
    def _fillData(self):
        with open('database.txt', 'r') as d:
            for x in d:
                line = x.split(',')
                self.data[line[0].split()[1]] = list(map(float,line[1:].copy()))
                
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
    root.title("MixoWatch")
    display = App(root)
    root.mainloop()




