import logic
import socket
import time
import threading

TOTAL_CARDS = 5

READY = "ready".encode()

ROUND_WIN = 'w'.encode()
ROUND_LOSE = 'l'.encode()
ROUND_DRAW = 'd'.encode()

WIN = 'W'.encode()
LOSE = 'L'.encode()

HOST = "127.0.0.1"
PORT = 65432

connectedUsers = 0
threads = []
choices = []

checkpoint = threading.Barrier(2)
lock = threading.Lock()

def main(con, addr):

    while not ready:
        time.sleep(2)

    con.sendall(READY)

      #---> Game Setup <---#
    player = logic.player()     # Initialise a player object for the player
    player.draw(5)              # Draw a starting hand of cards

    msg = '|'.join(player.cards)
    msg = msg.encode('utf-8')
    con.sendall(msg)

    #---> Game Start <---#
    global won
    while not won:                       # Checks if either player has won
        
        choice = con.recv(1).decode()    # Collect Choice
            
        print(choice)
        lock.acquire()
        choices.append(choice)          # Set Choices array ready for win descision
        lock.release()

        sorted_choices = sorted(choices)


        if sorted_choices[0] == sorted_choices[1]: # Checks draws
            winner = "draw"
            
        elif sorted_choices[0] == "paper":         # Checks wins
            if sorted_choices[1] == "rock":
                winner = "paper"
                player.points[1] += 1
            else:
                winner = "scissors"
                player.points[2] += 1
        else:
            winner = "rock"
            player.points[0] += 1


        if winner == "draw":          # Sends draw signal
            skt.sendall(ROUND_DRAW)
        elif choice == winner:      # Updates winner
            player.points[winslot]
            skt.sendall(ROUND_WIN)
        else:                       # Updates loser
            skt.sendall(ROUND_LOSE)
        

        if player.hasWon():         # Checks if player has won
            lock.acquire()
            won = True
            lock.release()

        checkpoint.wait()
            

    if player.won:              # Tell the Client if they've won or not
        skt.sendall(WIN)
    else:
        skt.sendall(LOSE)


# -- Main -- #
ready = False
won = False

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

skt.bind((HOST, PORT))
skt.listen(2)

while connectedUsers < 2:
    #try:
        con, addr = skt.accept()
        thread = threading.Thread(target=main, args=(con, addr))
        thread.start()
        threads.append(thread)
    
        connectedUsers += 1
        print("player connected successfully")

   # except:
        #print("Connection Failed...")


ready = True

for thread in threads:
    thread.join()

skt.close()
