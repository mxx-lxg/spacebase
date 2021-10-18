from tkinter import *
import tk_tools
import threading


class Dashboard(threading.Thread):

    wOpen = 0

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        tkFenster = Tk()
        tkFenster.title('Gewächshaus')
        tkFenster.geometry('600x400')

        self.temp = StringVar()
        self.hum = StringVar()


        # Label für die Anzeige der Daten
        tempLabel = Label(master=tkFenster, text='Temperatur', fg='white', bg='gray', font=('Arial', 24))
        tempLabel.place(x=5, y=5, width=180, height=30)

        tempDisp = Label(master=tkFenster, textvariable = self.temp, fg='black', bg='#FFCFC9', font=('Arial', 32))
        tempDisp.place(x=5, y=40, width=180, height=50)

        tempLabel = Label(master=tkFenster, text='Luftfeuchte', fg='white', bg='gray', font=('Arial', 24))
        tempLabel.place(x=190, y=5, width=180, height=30)

        tempDisp = Label(master=tkFenster, textvariable = self.hum, fg='black', bg='#FFCFC9', font=('Arial', 32))
        tempDisp.place(x=190, y=40, width=180, height=50)

        
        #w = Canvas(tkFenster)
        #w.place(x=10, y=10)
        #for window in range(5):
        #    if window > 0:
        #        if self.wOpen >= window:
        #            w.create_rectangle((window-1)*60+5, 5, (window-1)*60+55, 55, fill="blue", outline = 'blue')
        #        else:
        #            w.create_rectangle((window-1)*60+5, 5, (window-1)*60+55, 55, fill="red", outline = 'blue') 
        #w.pack()

        #schriftfarbe = labelTag.cget('fg')              # lesender Zugriff auf Attribute von labelTag
        #hintergrundfarbe = labelTag.cget('bg')          # lesender Zugriff auf Attribute von labelTag
        #schriftformat = labelTag.cget('font')           # lesender Zugriff auf Attribute von labelTag

        #labelMonat = Label(master=tkFenster, textvariable = self.temp)
        #labelMonat.config(fg=schriftfarbe)              # schreibender Zugriff auf Attribute von labelMonat
        #labelMonat.config(bg=hintergrundfarbe)          # schreibender Zugriff auf Attribute von labelMonat
        #labelMonat.config(font=schriftformat)           # schreibender Zugriff auf Attribute von labelMonat
        #labelMonat.place(x=70, y=30, width=55, height=50)

        # Aktivierung des Fensters
        tkFenster.mainloop()
    
    def callback(self):
        self.root.quit()

    def set(self, temp, hum, wOpen):
        self.temp.set(str(temp) + "°C")
        self.hum.set(str(hum) + "%")
        self.wOpen = wOpen


# https://stackoverflow.com/questions/459083/how-do-you-run-your-own-code-alongside-tkinters-event-loop