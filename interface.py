import socket
import tkinter

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
    cardslot = []
    for i in range(TOTAL_CARDS):
        cardslot.append(Button(handspace, text="", command=sendClick(i, skt)))
        cardslot[i].pack(side=LEFT, fill="both", expand=True)

    return cardslot

def sendClick(bNum, skt):
    skt.sendall()

def toggleButtons():
    print("Locked / Unlocked or whatever")

# COMBINE WITH CLIENT, IT WILL BE EASIER, SOURCE: TRUST ME 
