import tkinter as tk

window = tk.Tk()

for i in range(3):
    window.columnconfigure(i, weight=1, minsize=75)
    window.rowconfigure(i, weight=1, minsize=50)

    for j in range(0, 3):
        frame = tk.Frame(
            master=window,
            relief=tk.RAISED,
            borderwidth=1
        )
        frame.grid(row=i, column=j, padx=3, pady=3)

        button = tk.Button(master=frame, text=f"Button {3*i+j+1}")
        button.pack(padx=5, pady=5)

window.mainloop()