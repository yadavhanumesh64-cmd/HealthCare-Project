import tkinter as tk
import time

# Function to update time every second
def update_time():
    current_time = time.strftime("%H:%M:%S")  # 24-hour format
    clock_label.config(text=current_time)
    clock_label.after(1000, update_time)  # update every 1 sec

# Create main window
root = tk.Tk()
root.title("Digital Clock")
root.geometry("400x200")
root.resizable(False, False)
root.configure(bg="black")

# Label to display clock
clock_label = tk.Label(
    root,
    font=("Helvetica", 60, "bold"),
    background="black",
    foreground="cyan"
)
clock_label.pack(expand=True)

# Start the clock
update_time()

# Run the app
root.mainloop()
