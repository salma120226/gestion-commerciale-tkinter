
import tkinter as tk
from pages.dashboard import Dashboard

root = tk.Tk()
root.title("Nova-Commerce")
root.geometry("1250x750")
root.minsize(1000, 650)
root.configure(bg="#F4F6FB")

Dashboard(root)

root.mainloop()