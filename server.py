import logic
import socket
import time
import threading

HOST_IP = "127.0.0.1"
PORT = 65432

lock = threading.Lock()
connectedUsers = 0
choices = []
won = False

def startThreads(job):
    try:
        t1 = threading.Thread(job)
        t2 = threading.Thread(job)

        t1.start()
        t2.start()

        return t1, t2
    
    except:
        print("Threading Failed")
        return -1, -1

def connection():
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.bind((HOST_IP, PORT))
    
    skt.listen()
    connection, address = skt.accept()

    lock.acquire()
    connectedUsers += 1
    lock.release()

    while connectedUsers != 2:
        print("Waiting for players: "+ str(connectedUsers) + "/2")
        time.sleep(5)

    skt.sendall("ready")

    return skt, connection, address


def main():
    skt, conn, addr = connection()

    #---> Game Setup <---#
    player = logic.player()     # Initialise a player object for the player
    player.draw(5)              # Draw a starting hand of cards

    skt.sendall(player.cards)   # Send cards to player CALL_POINT_1

    #---> Game Start <---#

    while !won:                 # Checks if either player has won
        
        choice = skt.recv(8)    # Collect Choice
        lock.acquire()
        choices.append(choice)  # Set Choices array ready for win descision
        lock.release()

        sorted_choices = sorted(choices)


        if sorted_choices[0] == sorted_choices[1]: # Checks draws
            winner = "draw"
            
        elif sorted_choices[0] == "paper":         # Checks wins
            if sorted_choices[1] == "rock":
                winner = "paper"
                winslot = 1
            else:
                winner = "scissors"
                winslot = 2
        else:
            winner = "rock"
            winslot = 0


        if winner == draw:          # Sends draw signal
            skt.sendall(2)
        elif choice == winner:      # Updates winner
            player.points[winslot]
            skt.sendall(1)
        else:                       # Updates loser
            skt.sendall(0)
        

        if player.hasWon():         # Checks if player has won
            lock.acquire()
            won = True
            lock.release()
            

    if player.won:              # Tell the Client if they've won or not
        skt.sendall(1)
    else:
        skt.sendall(0)
    
    #---> Clean-up <---#
    skt.close()
    

t1, t2 = startThreads(main)
t1.join()
t2.join()

