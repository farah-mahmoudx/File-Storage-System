import tkinter as tk
from tkinter import messagebox, filedialog
import socket

serverIP = "127.0.0.1"
serverPort = 12000
BUFFER_SIZE = 2048

# Connect to the server
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))


def list_files():
    clientSocket.send("list_files".encode())
    files = clientSocket.recv(BUFFER_SIZE).decode().split("\n")
    file_list.delete(0, tk.END)
    for i, file in enumerate(files):
        file_list.insert(tk.END, f"{i + 1}. {file.strip()}")


def upload_file():

    filepath = filedialog.askopenfilename()
    if filepath:
        filename = filepath.split("/")[-1]
        clientSocket.send("upload".encode())
        clientSocket.send(filename.encode())
        if clientSocket.recv(BUFFER_SIZE).decode() == "READY":
            with open(filepath, 'rb') as file:
                while chunk := file.read(BUFFER_SIZE):
                    clientSocket.send(chunk)
            clientSocket.send("END".encode())
            messagebox.showinfo("Info", "Upload Successful!")
            list_files()
        else:
            messagebox.showerror("Error", "Upload Failed!")


def download_file():

    selection = file_list.curselection()
    if selection:
        selected_file = file_list.get(selection[0]).split(". ", 1)[1]
        clientSocket.send("download".encode())
        clientSocket.send(selected_file.encode())
        if clientSocket.recv(BUFFER_SIZE).decode() == "READY":
            save_path = filedialog.asksaveasfilename(initialfile=selected_file)
            if save_path:
                with open(save_path, 'wb') as file:
                    while True:
                        chunk = clientSocket.recv(BUFFER_SIZE)
                        if b"END" in chunk:  
                            chunk, _, _ = chunk.partition(b"END")  
                            file.write(chunk)  
                            break
                        file.write(chunk)  
                messagebox.showinfo("Info", "Download Successful!")
        else:
            messagebox.showerror("Error", "File Not Found!")
    else:
        messagebox.showwarning("Warning", "Select a file to download!")


def delete_file():

    selection = file_list.curselection()
    if selection:
        selected_file = file_list.get(selection[0]).split(". ", 1)[1]
        clientSocket.send("delete".encode())
        clientSocket.send(selected_file.encode())
        response = clientSocket.recv(BUFFER_SIZE).decode()
        messagebox.showinfo("Info", response)
        list_files()
    else:
        messagebox.showwarning("Warning", "Select a file to delete!")


def exit_application():

    clientSocket.send("exit".encode())
    clientSocket.close()
    root.destroy()



root = tk.Tk()
root.title("File Storage Client Application")
root.geometry("600x400")
root.resizable(False, False)

file_frame = tk.Frame(root, padx=10, pady=10)
file_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

file_list_label = tk.Label(file_frame, text="File List", font=("Arial", 12, "bold"))
file_list_label.pack(anchor="w")

file_list = tk.Listbox(file_frame, width=50, height=15, font=("Arial", 10))
file_list.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(file_frame, orient=tk.VERTICAL, command=file_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
file_list.config(yscrollcommand=scrollbar.set)


button_frame = tk.Frame(root, pady=10)
button_frame.pack(side=tk.BOTTOM, fill=tk.X)

btn_refresh = tk.Button(button_frame, text="Refresh List", command=list_files, width=12, bg="cornsilk3", fg="black", font=("Arial", 10))
btn_refresh.pack(side=tk.LEFT, padx=5)

btn_upload = tk.Button(button_frame, text="Upload File", command=upload_file, width=12, bg="cornsilk3", fg="black", font=("Arial", 10))
btn_upload.pack(side=tk.LEFT, padx=5)

btn_download = tk.Button(button_frame, text="Download File", command=download_file, width=12, bg="cornsilk3", fg="black", font=("Arial", 10))
btn_download.pack(side=tk.LEFT, padx=5)

btn_delete = tk.Button(button_frame, text="Delete File", command=delete_file, width=12, bg="cornsilk3", fg="black", font=("Arial", 10))
btn_delete.pack(side=tk.LEFT, padx=5)

btn_exit = tk.Button(button_frame, text="Exit", command=exit_application, width=12, bg="brown1", fg="white", font=("Arial", 10))
btn_exit.pack(side=tk.LEFT, padx=5)


list_files()


root.mainloop()
