from tkinter import Tk, Frame
from container import Container
from login import Login

class Manager(Tk):
    def __init__(self, *args, **kwargs):
        # Inicializa la clase base Tk
        Tk.__init__(self, *args, **kwargs)
        # Configura la ventana principal
        self.title("Licorería Julio Cesar 1.0")
        self.geometry("1024x576+190+70")
        self.configure(bg="#E6D9E3")
        self.resizable(False, False)
        self.frame = Frame(self)

        # Configura el contenedor principal
        self.container = Frame(self, bg="#E6D9E3")
        self.container.pack(side="top", fill="both", expand=True)

        # Diccionario para almacenar los frames
        self.frames = {}
        for i in (Login, Container):
           frame = i(self.container, self)
           self.frames[i] = frame


        self.show_frame(Container)


    def show_frame(self, container):
        # Muestra el frame especificado
        frame = self.frames[container]
        frame.tkraise()

def main():
    app = Manager()
    app.mainloop()

if __name__ == "__main__":
    main()
