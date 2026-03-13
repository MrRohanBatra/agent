import tkinter as tk
from tkinter import messagebox

def main():
    root = tk.Tk()
    root.title("Hello World")
    
    # Create a label to display the message
    label = tk.Label(root, text="Hello World", font=("Arial", 24))
    label.pack(pady=50)
    
    # Add a button to restart
    def on_button_click():
        root.destroy()
    
    btn = tk.Button(root, text="Restart", command=on_button_click)
    btn.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
