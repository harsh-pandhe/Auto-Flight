import tkinter as tk
import socket

# REPLACE WITH YOUR PI'S IP ADDRESS (e.g., 192.168.1.10)
DRONE_IP = "192.168.x.x" 
PORT = 5000

def send_command(cmd):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((DRONE_IP, PORT))
        sock.sendall(cmd.encode())
        response = sock.recv(1024).decode()
        log(f"Sent: {cmd} | Recv: {response}")
        sock.close()
    except Exception as e:
        log(f"Error: {e}")

def log(msg):
    txt_console.insert(tk.END, msg + "\n")
    txt_console.see(tk.END)

root = tk.Tk()
root.title("ASCEND Mission Control")
root.geometry("400x300")

tk.Label(root, text="BASE STATION COMMANDER", font=("Arial", 14, "bold")).pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="ARM", bg="orange", width=15, command=lambda: send_command("ARM")).pack(pady=5)
tk.Button(btn_frame, text="TAKEOFF (1m)", bg="green", fg="white", width=15, command=lambda: send_command("TAKEOFF")).pack(pady=5)
tk.Button(btn_frame, text="LAND", bg="red", fg="white", width=15, command=lambda: send_command("LAND")).pack(pady=5)

txt_console = tk.Text(root, height=8, bg="black", fg="#00ff00")
txt_console.pack(fill="both", padx=10, pady=10)

root.mainloop()