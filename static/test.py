import random
board = {
        1: " ",
        2: " ",
        3: " ",
        4: " ",
        5: " ",
        6: " ",
        7: " ", 
        8: " ", 
        9:" ",
        }
def boardNewTurn(board, pos, p):
    if board[pos] == " ":
        if p == "B":
            board[pos] = "0"
        else:
            board[pos] = "X"     
        return {"status": "Done", "board": board}
    else:
        return {"status": "Already Occupied", "board": board}

def robo_chance(board):

    chk = 0
    while True:
        if chk == 1:
            break
        else:
            pos = random.randint(1,9)
            robo = boardNewTurn(board, pos, "B")
            print(robo["status"])
            if(robo["status"] == "Done"):
                chk = 1

def usr_chance(board, usr):
    chk = 0
    while True:
        if chk == 1:
            break
        else:
            robo = boardNewTurn(board, usr, "U")
            print(robo["status"])
            if(robo["status"] == "Done"):
                chk = 1
            else:
                usr = int(input("Enter Again:-"))    

for i in range(9):
    if i % 2 == 0:
        usr = int(input("Enter:-"))
        usr_chance(board, usr)
    else:
        robo_chance(board)

    print(board)    
