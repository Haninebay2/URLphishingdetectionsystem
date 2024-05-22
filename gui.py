import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from app import predict_url
import pickle  # Import the prediction 
from PIL import Image, ImageTk


# Load LabelEncoders
with open('protocol_encoder.pkl', 'rb') as f:
    le_protocol = pickle.load(f)
with open('domain_encoder.pkl', 'rb') as f:
    le_domain = pickle.load(f)
with open('suffix_encoder.pkl', 'rb') as f:
    le_suffix = pickle.load(f)

# Load models
models = {
    'SVM': pickle.load(open('svm_model (1).pkl', 'rb')),
    'RF': pickle.load(open('rf_model (1).pkl', 'rb')),
    'LR': pickle.load(open('Lr_model (1).pkl', 'rb'))
}

def check_url(model_name, protocol_encoder, domain_encoder, suffix_encoder):
    """Get URL from entry and check its legitimacy using the specified model."""
    url = url_entry.get()
    if url:
        try:
            model = models[model_name]  # Select the model from the dictionary
            prediction = predict_url(url, model, protocol_encoder, domain_encoder, suffix_encoder)
            result = f"Result: {prediction}"
            messagebox.showinfo("Prediction Result", result)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showerror("Error", "Please enter a URL.")

# Create the main window
root = tk.Tk()

# Layout using frames
frame = ttk.Frame(root, padding="10 10 10 10")
frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

# Label and entry for URL
label = ttk.Label(frame, text="Enter URL:", font=("Helvetica", 16, "bold"), foreground="#000040")
label.grid(column=0, row=0, sticky=(tk.W, tk.E))
url_entry = ttk.Entry(frame)
url_entry.grid(column=0, row=1, pady=10, sticky=(tk.W, tk.E))

# Buttons for each model, linking directly to the prediction function with the correct model type
btn_svm = ttk.Button(frame, text="Check with SVM", command=lambda: check_url('SVM', le_protocol, le_domain, le_suffix))
btn_rf = ttk.Button(frame, text="Check with RF", command=lambda: check_url('RF', le_protocol, le_domain, le_suffix))
btn_lr = ttk.Button(frame, text="Check with LR", command=lambda: check_url('LR', le_protocol, le_domain, le_suffix))
btn_svm.grid(column=0, row=2, sticky=(tk.W, tk.E), pady=(10, 0))
btn_rf.grid(column=0, row=3, sticky=(tk.W, tk.E), pady=(10, 0))
btn_lr.grid(column=0, row=4, sticky=(tk.W, tk.E), pady=(10, 0))


from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def resize_image(event=None):
    # Get the dimensions of the window
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    # Calculate the ratio based on width
    ratio = window_width / initial_width

    # Calculate the tentative new height
    new_height = int(initial_height * ratio)

    # Adjust ratio based on height if it exceeds the window height
    if new_height > window_height:
        ratio = window_height / initial_height

    # Calculate the final size of the new image
    new_size = (int(initial_width * ratio), int(initial_height * ratio))

    # Resize the image using the calculated ratio and LANCZOS filter for quality
    image_resized = img.resize(new_size, Image.LANCZOS)
    photo = ImageTk.PhotoImage(image_resized)
    img_label.config(image=photo)
    img_label.image = photo  # Keep a reference to avoid garbage collection

# Initialize Tkinter root window
root.title("Url Legitimacy Checker")
root.geometry("500x400")  # Initial window size adjusted to provide more space

# Load the image
img = Image.open("urlp.jpg")  # Adjust the file path as needed
initial_width, initial_height = img.size  # Get initial image dimensions

# Create a label to display the image
img_label = ttk.Label(root)
img_label.grid(column=1, row=0, sticky="nsew")

# Configure the grid
root.grid_columnconfigure(0, weight=1)  # This column will not expand as much
root.grid_columnconfigure(1, weight=3)  # This column will expand more, where the image is
root.grid_rowconfigure(0, weight=1)

# Bind the resizing function to window size changes
root.bind('<Configure>', resize_image)

root.mainloop()