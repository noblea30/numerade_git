import tkinter as tk

def remove_newlines(input_text):
    # Replace all newline characters with an empty string
    result = input_text.replace("\n", "")
    return result

def process_text():
    input_text = input_textbox.get("1.0", "end-1c")
    output_text = remove_newlines(input_text)
    
    # Append the output to the existing text in the output textbox
    output_textbox.insert(tk.END, output_text + "\n")
    
    # Clear the input textbox
    input_textbox.delete("1.0", tk.END)

# Create the main application window
app = tk.Tk()
app.title("Remove Newlines")

# Input Textbox
input_label = tk.Label(app, text="Paste your text with newlines:")
input_label.pack()
input_textbox = tk.Text(app, height=10, width=50)
input_textbox.pack()

# Preview Button
preview_button = tk.Button(app, text="Preview", command=process_text)
preview_button.pack()

# Output Textbox
output_label = tk.Label(app, text="Output (newlines removed):")
output_label.pack()
output_textbox = tk.Text(app, height=10, width=50)
output_textbox.pack()

# Run the main event loop
app.mainloop()
