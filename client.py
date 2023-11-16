import interface
import socket
import time
import tkinter as tk

HOST_IP = "127.0.0.1"
PORT = 65432

window = tk.Tk()

def connectToServer(skt):
    for i in range(6): #Equivalent to trying for 1min
        try:
            skt.connect((HOST, PORT))
            return 1
        except:
            print("Waiting to Connect...")
            time.sleep(10)
    print("Connection Failed")
    return 0

# STEP 1 - Connect to Server

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if connectToServer(skt):
    
    while skt.recv(5) != "ready":           # Wait for player 2 to connect
        time.wait(5)

# STEP 2 - Setup Game

    cardslots = interface.screenGen(window, skt)     # Load GUI

    cards = skt.recv(1024)                  # Probably could see abt reducing from 1024 ??? CALL_POINT_1

    for i in range(len(cards)-1):           # Sets the cards in the GUI slots
        cardslots[i].config(text=cards[i])

# STEP 3 - Play Game
    # INTERFACE sends button click to SERVER
    # INTERFACE locks buttons
    # SERVER tells outcome to CLIENT
    # INTERFACE updates score
    # If recieves won then INTERFACE displays win screen and CLIENT to Step 4
    # else INTERFACE unlocks buttons
    

# Step 4 - Close Connection
    window.destroy()
    skt.close()




