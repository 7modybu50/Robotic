import socket
import time
import threading
import tkinter as tk
from tkinter import *

HOST = "127.0.0.1"
PORT = 65432

TOTAL_CARDS = 5
WIN_SIZE_X = 900
WIN_SIZE_Y = 700

window = tk.Tk()

cardslots = []

def screenGen(window, skt):
    #Window generation
    window.geometry(str(WIN_SIZE_X) + "x" + str(WIN_SIZE_Y))
    window.resizable(False, False)

    #Split screen into sections (Frames)
    topBar = Frame(window, height= 30)
    scorespace = Frame(window, height= 200)
    instructionBar = Frame(window, height= 30)
    handspace = Frame(window)
    
    #Pack to screen
    topBar.pack(side = TOP, fill='x', expand=False)
    scorespace.pack(side = TOP, fill='both', expand=True)
    instructionBar.pack(side = TOP, fill='x', expand=False)
    handspace.pack(side = BOTTOM, fill='both', expand=True)

    #Fill Cardslot with cards (buttons)
    for i in range(TOTAL_CARDS):
        cardslots.append(tk.Button(handspace, text="", command=lambda local = i: sendChoice(local, skt)))
        cardslots[i].pack(side=LEFT, fill="both", expand=True)

    return cardslots

def sendChoice(buttonNumber, skt):
    msg = cards[buttonNumber].encode('utf-8')
    print(cards)
    print(buttonNumber)
    print(cards[buttonNumber])
    skt.sendall(msg)

    
    
    toggleButtons()

def toggleButtons():
    for card in cardslots:
        if card['state'] == "normal":
            card.configure(state="disabled")
        else:
            card.configure(state="normal")

def endScreen(outcome):
    for widget in window.winfo_children():
        widget.destroy()

    endScreenText = Label(window, text=outcome)
    endScreenText.pack(fill="both", expand=True)

def connectToServer(skt):
    for i in range(6):                                      # Equivalent to trying for 1min
        try:
            skt.connect((HOST, PORT))
            return 1
        except:
            print("Waiting to Connect...")
            time.sleep(10)
    print("Connection Failed")
    return 0

def gameProcessor():
    global won
    won = False
    while not won:
        msg = skt.recv(1).decode('utf-8')
        
        if msg == 'w':
            print("Battle Won")
            toggleButtons()
        elif msg == 'l':
            print("Battle Lost")
            toggleButtons()
        elif msg == 'd':
            print("Draw")
            toggleButtons()

        elif msg == 'W':
            endScreen("GAME WON")
            time.sleep(10)
            window.destroy()
            
        elif msg == 'L':
            endScreen("GAME LOST :(")
            time.sleep(10)
            window.destroy()


# -- Connect To Server -- #

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if connectToServer(skt):

    print("Waiting for Player 2...")                        # Waits to recieve ready (or any 5 bytes lol)
    skt.recv(5) 
    print("Player 2 connected")
    
# -- Setup GUI & Game objects -- #

    cardslots = screenGen(window, skt)                                  # Load GUI
    
    cards = skt.recv(10).decode('utf-8').split('|')       # Probably could see abt reducing from 1024 ??? CALL_POINT_1

    for i in range(len(cards)):                           # Sets the cards in the GUI slots
        if cards[i] == 'r':
            cardslots[i].config(text="Rock")
        elif cards[i] == 'p':
            cardslots[i].config(text="Paper")
        elif cards[i] == 's':
            cardslots[i].config(text="Scissors")
        else:
            cardslots[i].config(text="None")

# -- Play Game -- #

    thread = threading.Thread(target=gameProcessor)
    thread.start()

    tk.mainloop()
    # tkinter updates scorebar!!!! - TODO
    

# -- Clean Up Everything -- #
    thread.join()

    skt.close()






