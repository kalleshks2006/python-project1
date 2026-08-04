import tkinter as tk
root=tk.Tk()
root.title("my first tkinter app")
label=tk.label(root,text="hello,tkinter!",font=("Arial",14))
label.pack(pady=20)
root.mainloop()    