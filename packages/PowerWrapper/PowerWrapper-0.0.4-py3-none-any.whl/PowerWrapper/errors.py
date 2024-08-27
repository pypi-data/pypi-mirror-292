from tkinter import * 
from tkinter import messagebox


# Hiding tkinter root window.
root = Tk()
root.geometry("1x1")
w = Label(root, text ='empty', font = "50")
root.withdraw()
w.pack()

class errors():
        # These 3 show GUI error boxes with the desired text, very convenient for the developer
        
        # Information text box
        def showInfo(title_one, text_one):   
                messagebox.showinfo(title_one, text_one)
        
        # Warning text box
        def showWarning(title_two, text_two):
                messagebox.showwarning(title_two, text_two)

        # Error text box
        def showError(title_three, text_three):
                messagebox.showerror(title_three, text_three)
