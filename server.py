import logic
import socket
import time
import threading

TOTAL_CARDS = 5

READY = "ready".encode('utf-8')

ROUND_WIN = 'w'.encode('utf-8')
ROUND_LOSE = 'l'.encode('utf-8')
ROUND_DRAW = 'd'.encode('utf-8')

WIN = 'W'.encode('utf-8')
LOSE = 'L'.encode('utf-8')

HOST = "127.0.0.1"
PORT = 65432

connectedUsers = 0
threads = []
choices = []

remaining = [10,10,10]

checkpoint = threading.Barrier(2)
lock = threading.Lock()

def addPoint(player, position):
    player.points[position] += 1

def main(con, addr):

    while not ready:
        time.sleep(2)

    con.sendall(READY)

      #---> Game Setup <---#
    player = logic.player()     # Initialise a player object for the player

    global remaining
    lock.acquire()
    card, remaining = player.draw2(5, remaining)              # Draw a starting hand of cards
    lock.release()

    msg = '|'.join(player.cards)
    msg = msg.encode('utf-8')
    con.sendall(msg)

    #---> Game Start <---#
    global won
    while not won:                       # Checks if either player has won
        choice = con.recv(1).decode('utf-8')    # Collect Choice

        pointslot = -1

        print(choice)
        lock.acquire()
        choices.append(choice)          # Set Choices array ready for win descision
        lock.release()

        checkpoint.wait()
        
        sorted_choices = sorted(choices)
        if sorted_choices[0] == sorted_choices[1]: # Checks draws
            winner = "draw"
            
        elif sorted_choices[0] == 'p':         # Checks wins
            if sorted_choices[1] == 'r':
                winner = 'p'
                pointslot = 1
                
            else:
                winner = 's'
                pointslot = 2
        else:
            winner = 'r'
            pointslot = 0

        if winner == "draw":          # Sends drawn signal
            con.sendall(ROUND_DRAW)
        elif choice == winner:      # Updates winner
            con.sendall(ROUND_WIN)
            player.points[pointslot] += 1
        else:                       # Updates loser
            con.sendall(ROUND_LOSE)

        if player.hasWon():         # Checks if player has won
            lock.acquire()
            won = True
            lock.release()

        player.bin(choice)
        player.draw2(1, remaining)
        new_card = player.cards[-1]
        card_msg = new_card.encode('utf-8')
        con.sendall(card_msg)

        checkpoint.wait()
        
        lock.acquire()
        choices.pop()
        lock.release()

        print("\nNew Card:", new_card, "\n")

        checkpoint.wait()

    if player.won:              # Tell the Client if they've won or not
        con.sendall(WIN)
    else:
        con.sendall(LOSE)


# -- Main -- #
ready = False
won = False

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

skt.bind((HOST, PORT))
skt.listen(2)

while connectedUsers < 2:
        con, addr = skt.accept()
        thread = threading.Thread(target=main, args=(con, addr))
        thread.start()
        threads.append(thread)
    
        connectedUsers += 1
        print("player connected successfully")

ready = True

for thread in threads:
    thread.join()

skt.close()
