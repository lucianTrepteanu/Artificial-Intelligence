import sys
import copy
from time import time
import pygame

INF=10**9

#L D R U
dir2idx={'L':0,'D':1,'R':2,'U':3}
directions=[(0,-1),(1,0),(0,1),(-1,0)]

directions_neigh=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

#verifica daca cell-ul de coordonate x,y se afla in interiorul tablei
def in_limits(x,y):
    return x>=0 and x<10 and y>=0 and y<10

#reprezentarea unei piese de joc 1x2
class Piece:
    def __init__(self,x1,y1,dir=None,ch=None):
        # contine celula1,celula2 (care e vecina cu celula1) si caracterul(x/0)
        self.cell1=(x1,y1)
        if dir in dir2idx:
            self.cell2=(x1+directions[dir2idx[dir]][0],y1+directions[dir2idx[dir]][1])
        self.ch=ch

class Board:
    # initializeaza tabla cu starea initiala
    def __init__(self,board=None):
        if board is None:
            self.board=[[' ' for y in range(10)]for x in range(10)]
            self.board[4][4]='X'
            self.board[4][5]='X'
            self.board[5][4]='0'
            self.board[5][5]='0'
        else:
            self.board=board

    # afiseaza tabela de joc in consola
    def print(self):
        horizontal_line='__________'*4
        print(horizontal_line)

        for i in range(10):
            print('|',end='')
            for j in range(10):
                print(' '+str(self.board[i][j])+' ',end='|')
            print('\n'+horizontal_line)

    # verifica daca tabla nu mai are casute libere
    def check_full_board(self):
        for i in range(10):
            for j in range(10):
                if self.board[i][j]==' ':
                    return False
        return True

    # verifica daca mai exista mutari posibile
    def check_final_board(self):
        # 'X' este ales aleator. X poate muta daca si numai daca 0 ar putea muta
        next_states=generate_next_states(self,'X')
        if next_states is None or len(next_states)<1: #daca nu mai exista stari urmatoare
            return True
        return False

    # verifica validitatea amplasarii piesei piece
    def valid_move(self,piece:Piece):
        cell1=piece.cell1
        cell2=piece.cell2

        has_x_neigh=False
        has_0_neigh=False

        # verifica daca celulele ies din tabla de joc
        if cell1[0]>=10 or cell1[1]>=10 or cell2[0]>=10 or cell2[1]>=10:
            return False
        if cell1[0]<0 or cell1[1]<0 or cell2[0]<0 or cell2[1]<0:
            return False

        # verifica daca una din celule e ocupata deja
        if self.board[cell1[0]][cell1[1]]!=' ' or self.board[cell2[0]][cell2[1]]!=' ':
            return False

        # cauta in vecinii lui cell1 daca mai exista un caracter X si unul 0
        for d in directions_neigh:
            newc1=(cell1[0]+d[0],cell1[1]+d[1])
            if newc1==cell2: #nu trebuie sa numere si cealalta jumatate a piesei
                continue

            if newc1[0]>=10 or newc1[1]>=10:
                continue
            if newc1[0]<0 or newc1[1]<0:
                continue

            if self.board[newc1[0]][newc1[1]]=='X':
                has_x_neigh=True
            elif self.board[newc1[0]][newc1[1]]=='0':
                has_0_neigh=True

        # verifica in vecinii lui cell2 daca mai exista un caracter X si unul 0
        for d in directions_neigh:
            newc2=(cell2[0]+d[0],cell2[1]+d[1])
            if newc2==cell1: #nu trebuie sa numere si cealalta jumatate a piesei
                continue

            if newc2[0]>=10 or newc2[1]>=10:
                continue
            if newc2[0]<0 or newc2[1]<0:
                continue

            if self.board[newc2[0]][newc2[1]]=='X':
                has_x_neigh = True
            elif self.board[newc2[0]][newc2[1]]=='0':
                has_0_neigh = True

        # verifica daca avem cel putin un vecin X si unul 0
        if has_x_neigh == False or has_0_neigh == False:
            return False

        return True

    # calculeaza scorul jucatorului turn
    def get_score(self,turn):
        score=0

        # parcurgem tabela de joc
        for i in range(10):
            for j in range(10):
                cell1=(i,j)

                start=(i,j)#fixam capatul de sus al unei potentiale diagonale
                if in_limits(start[0], start[1])==False:
                    continue

                # incercam sa coboram 2 casute in stanga-jos si dreapta-jos
                dr1=(start[0]+1,start[1]+1)
                dr2=(start[0]+2,start[1]+2)
                st1=(start[0]+1,start[1]-1)
                st2=(start[0]+2,start[1]-2)

                # verificam daca celulele pe care vrem sa le verificam se afla in tabela
                if in_limits(dr1[0],dr1[1]):
                    celldr1=self.board[dr1[0]][dr1[1]]
                else:
                    celldr1='$' #daca nu se afla atribuim "celulei inexistente" un caracter diferit de X si 0
                if in_limits(dr2[0],dr2[1]):
                    celldr2=self.board[dr2[0]][dr2[1]]
                else:
                    celldr2='$'
                if in_limits(st1[0],st1[1]):
                    cellst1=self.board[st1[0]][st1[1]]
                else:
                    cellst1='$'
                if in_limits(st2[0],st2[1]):
                    cellst2=self.board[st2[0]][st2[1]]
                else:
                    cellst2='$'
                cellstart = self.board[start[0]][start[1]]

                # daca se face punct pe diagonala dreapta jos
                if cellstart==turn and celldr1==turn and celldr2==turn:
                    score=score+1
                # daca se face punct pe diagonala stanga jos
                if cellstart==turn and cellst1==turn and cellst2==turn:
                    score=score+1

        return score

    # aceasta euristica se uita cate puncte (diagonale complete)
    # ar completa amplasarea piesei piece
    def compute_heuristic_points(self,piece):
        for cell in [piece.cell1,piece.cell2]:
            character=self.board[cell[0]][cell[1]]

            depl=[(-2,-2), (-1,-1), (-1,1), (-2,2), (0,0)]
            # ca cell1 sa faca parte din diagonala stabilim punctul cel mai
            # de sus al acesteia. Cell1 poate fi al 3-lea, al 2-lea sau primul
            # pe o diagonala considerata in jos

            # punctul de start din care incercam sa coboram pentru a verifica diagonala
            starts=[(cell[0]+d[0],cell[1]+d[1]) for d in depl]

            count=0
            # procedam asemanator calcularii scorului din functie get_score()
            for start in starts:
                if in_limits(start[0],start[1]) == False:
                    continue

                dr1=(start[0]+1,start[1]+1)
                dr2=(start[0]+2,start[1]+2)
                st1=(start[0]+1,start[1]-1)
                st2=(start[0]+2,start[1]-2)

                if in_limits(dr1[0],dr1[1]):
                    celldr1=self.board[dr1[0]][dr1[1]]
                else:
                    celldr1='$'
                if in_limits(dr2[0],dr2[1]):
                    celldr2=self.board[dr2[0]][dr2[1]]
                else:
                    celldr2='$'
                if in_limits(st1[0],st1[1]):
                    cellst1=self.board[st1[0]][st1[1]]
                else:
                    cellst1='$'
                if in_limits(st2[0],st2[1]):
                    cellst2=self.board[st2[0]][st2[1]]
                else:
                    cellst2='$'
                cellstart=self.board[start[0]][start[1]]

                if cellstart==character and celldr1==character and celldr2==character:
                    count=count+1
                if cellstart == character and cellst1==character and cellst2==character:
                    count=count+1

        return count

    def compute_heuristic_vecini(self,piece):
        '''
        pentru fiecare cell cautam dr-sus,st-sus,dr-jos,st-jos cate x-uri are.
        '''

        for cell in [piece.cell1,piece.cell2]:
            character = self.board[cell[0]][cell[1]]

            count = 0

            drsus = (cell[0] - 1, cell[1] + 1)
            drjos = (cell[0] + 1, cell[1] + 1)
            stsus = (cell[0] - 1, cell[1] - 1)
            stjos = (cell[0] + 1, cell[1] - 1)

            if in_limits(drsus[0], drsus[1]):
                celldrsus = self.board[drsus[0]][drsus[1]]
            else:
                celldrsus = '$'
            if in_limits(drjos[0], drjos[1]):
                celldrjos = self.board[drjos[0]][drjos[1]]
            else:
                celldrjos = '$'
            if in_limits(stsus[0], stsus[1]):
                cellstsus = self.board[stsus[0]][stsus[1]]
            else:
                cellstsus = '$'
            if in_limits(stjos[0], stjos[1]):
                cellstjos = self.board[stjos[0]][stjos[1]]
            else:
                cellstjos = '$'
            cellstart = self.board[cell[0]][cell[1]]

            if cellstart==character and celldrsus==character:
                count=count+1
            if cellstart==character and cellstsus==character:
                count=count+1
            if cellstart==character and celldrjos==character:
                count=count+1
            if cellstart==character and cellstjos==character:
                count=count+1

        return count

#stabilim cine urmeaza la rand
def next_turn(turn):
    if turn=='X':
        return '0'
    return 'X'

#returneaza starile urmatoare starii board
#flag-ul sort indica daca lista de stari va fi sau nu sortata
#descrescator in functie de euristica
def generate_next_states(board:Board,turn,sort=False):
    state_list=[]
    for i in range(10):
        for j in range(10):
            c1=(i,j) #fixam prima celula a eventualei piese (fie aceasta cea mai de sus/stanga)
            # pentru a evita duplicatele incercam sa completam piesa in dreapta/jos
            for d in directions[1:3]:
                # a 2a celula a piesei
                c2=(c1[0]+d[0],c1[1]+d[1])
                new_piece=Piece(i,j)
                new_piece.ch=turn
                new_piece.cell2=c2

                # daca piesa poate fi amplasata cream o noua stare
                if board.valid_move(new_piece):
                    new_board=Board(copy.deepcopy(board.board))
                    new_board.board[new_piece.cell1[0]][new_piece.cell1[1]]=turn
                    new_board.board[new_piece.cell2[0]][new_piece.cell2[1]]=turn
                    heuristic=new_board.compute_heuristic_points(new_piece)
                    state_list.append((new_board,heuristic))

    # daca trebuie sortata lista de stari, o facem descrescator dupa euristica
    if sort is True:
        state_list.sort(key=lambda x:-x[1])
    return state_list

#algoritmul minimax
def minimax(board:Board,depth,maximizing_player,turn):
    # generam starile urmatoare
    next_states=generate_next_states(board,turn)

    # daca nu exista mutari posibile sau am epuizat depth-ul, nu continuam calculul
    if board.check_final_board() or depth==0:
        return (1,None)

    value=0
    best_move=None

    if maximizing_player:
        value=-2*INF
        for next_state in next_states:
            result=minimax(next_state[0],depth-1,not maximizing_player,next_turn(turn))

            if result[0]>value:
                value,best_move=result[0],next_state[0]

        return (value,best_move)
    else:
        value=2*INF
        for next_state in next_states:
            result=minimax(next_state[0],depth-1,not maximizing_player,next_turn(turn))

            if result[0]<value:
                value,best_move=result[0],next_state[0]

        return (value,best_move)

#algoritmul alfa-beta
def alphabeta(board:Board,depth,alpha,beta,maximizing_player,turn):
    # generam starile urmatoare, sortate dupa euristica
    next_states=generate_next_states(board,turn,sort=True)

    # daca nu mai avem mutari posibile sau am epuizat depth-ul
    if board.check_final_board()==True or depth==0:
        return (0,None)

    #if len(next_states)==0:
    #    return alphabeta(board,depth-1,alpha,beta,not maximizing_player,next_turn(turn))

    value=0
    best_move=None
    if maximizing_player:
        value=-2*INF
        for next_state in next_states:
            result=alphabeta(next_state[0],depth-1,alpha,beta,not maximizing_player,next_turn(turn))
            if result[0]>value:
                value,best_move=result[0],next_state[0]
            alpha=max(alpha,result[0])
            if alpha>=beta:
                break
    else:
        value=2*INF
        for next_state in next_states:
            result=alphabeta(next_state[0],depth-1,alpha,beta,not maximizing_player,next_turn(turn))
            if result[0]<value:
                value,best_move=result[0],next_state[0]
            beta=min(beta,result[0])
            if alpha>=beta:
                break

    return (value,best_move)

#functie care determina urmatoarea mutare tinand cont de algoritmul
#ce se doreste a fi folosit pentru computer
def get_next_state(board,algo_type,depth,turn):
    if algo_type=='1':
        return minimax(board,depth,True,turn)[1]
    else:
        return alphabeta(board,depth,-INF,+INF,True,turn)[1]

#afisarea in consola a statisticilor:
#timp total de joc, punctaj X, punctaj 0, invingator,numar mutari
def print_scores(board,player_moves,computer_moves,start_time):
    score_x=board.get_score('X')
    score_0=board.get_score('0')
    print("X score: ",score_x)
    print("0 score: ",score_0)
    if score_x==score_0:
        print('DRAW')
    elif score_x<score_0:
        print('0 WINS')
    else:
        print('X WINS')

    stop_time=time()
    print("Player moves: "+str(player_moves))
    print("Computer moves: "+str(computer_moves))
    print("Total gametime: "+str(round(1000*(stop_time-start_time),2))+" ms.")

#functia de initiere a jocului
def play_game(algo_type,depth,player_character):
    board = Board()

    pygame.init() #pornim pygame
    pygame.display.set_caption("XO v2") #dam titlu ferestrei
    screen = pygame.display.set_mode(size=[500, 500]) #setam dimensiunea ferestrei de joc
    grid = draw_table(screen, board.board) #o structura ce va memora tabela de desenat in ecranul de pygame
    pygame.display.update()

    turn='X'
    computer_moves=0
    player_moves=0
    start_time=time()

    not_over=True
    while not_over: #flag boolean care spune daca s-a terminat sau nu jocul
        if board is None: #daca s-a terminat jocul
            break
        if board.check_final_board()==True: #daca nu mai exista mutari posibile
            break

        if turn==player_character:#daca la rand este jucatorul
            row=None
            col=None
            d=None
            print('Your move.')
            time0=time()

            #de data aceasta inputul va consta intr-un click pe una din celule(celula de start)
            #si o apasare de buton UP,LEFT,RIGHT,DOWN pentru selectarea directiei celeilalte celule
            #in caz ca prima celula a fost selectata "din greseala" jucatorul poate apasa tasta Q pentru undo
            while True:
                not_clicked=True
                while not_clicked==True: #cat timp nu s-a selectat prima celula (nu s-a capturat click)
                    for event in pygame.event.get():
                        if event.type==pygame.QUIT: #daca se iese din joc, afisam statisticile si inchidem programul
                            print_scores(board,player_moves,computer_moves,start_time)
                            pygame.quit()
                            sys.exit()
                        if event.type==pygame.MOUSEBUTTONUP: #daca s-a realizat un click,vedem in ce celula s-a intamplat
                            position=pygame.mouse.get_pos()
                            for line in range(10):
                                for column in range(10):
                                    if grid[line][column].collidepoint(position):
                                        row=line
                                        col=column
                                        not_clicked=False #s-a selectat celula acum

                undo=False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print_scores(board, player_moves, computer_moves, start_time)
                        pygame.quit()
                        sys.exit()
                    if event.type==pygame.KEYDOWN and event.key==pygame.K_u: #daca a fost apasata tasta Q, jucatorul doreste sa deselecteze celula
                        undo=True

                if undo==True: #daca s-a facut undo la selectia initiala, ne intoarcem la inceputul loop-ului
                    continue

                not_pressed=True
                while not_pressed==True: #asteptam sa se apese o directie (valida) pentru a 2a celula
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            print_scores(board, player_moves, computer_moves, start_time)
                            pygame.quit()
                            sys.exit()
                        if event.type==pygame.KEYDOWN: #daca s-a apasat un buton, verificam daca a fost una din cele 4 directii
                            if event.key==pygame.K_LEFT:
                                d='L'
                                not_pressed=False
                            elif event.key==pygame.K_RIGHT:
                                d='R'
                                not_pressed=False
                            elif event.key==pygame.K_UP:
                                d='U'
                                not_pressed=False
                            elif event.key==pygame.K_DOWN:
                                d='D'
                                not_pressed=False

                if d in dir2idx: #verificam daca piesa dorita este o miscare valida. In caz afirmativ realizam miscarea
                    first_piece=Piece(row,col,d,turn)
                    if board.valid_move(first_piece):
                        board.board[first_piece.cell1[0]][first_piece.cell1[1]]=turn
                        board.board[first_piece.cell2[0]][first_piece.cell2[1]]=turn
                        player_moves+=1
                        break

            time1 = time()
            print("Player thought: " + str(round(1000 * (time1 - time0), 2)) + " ms.")
            grid=draw_table(screen,board.board)
            pygame.display.update()
        else: #este randul computerului sa mute
            time0=time()
            board=get_next_state(board,algo_type,depth,turn)
            if board is None:
                break
            computer_moves+=1

            if board.check_final_board() == True:
                break

            time1=time()
            print("Computer thought: "+str(round(1000*(time1-time0),2))+" ms.")
            grid=draw_table(screen,board.board)
            pygame.display.update()

        turn=next_turn(turn)

def draw_table(display,table): #desenarea tabelei de joc in pygame
    width_box=height_box=50 #inaltimea si latimea unei celule
    x_piece_image=pygame.image.load("x_piece.jpg") #resursa pentru imaginea piesei cu X
    o_piece_image=pygame.image.load("0_piece.jpg") #resursa pentru imaginea piesei cu 0
    x_piece_image=pygame.transform.scale(x_piece_image,(width_box,height_box)) #scalam imaginile pentru a se potrivi celulelor
    o_piece_image=pygame.transform.scale(o_piece_image,(width_box,height_box))

    grid=[]
    for row in range(10):
        grid_row=[] #fiecare linie va contine un dreptunghi 50x50
        for col in range(10):
            box=pygame.Rect(col*(width_box+1),row*(height_box+1),width_box,height_box) #desenam un dreptunghi corespunzator coordonatelor celulei
            grid_row.append(box)
            pygame.draw.rect(display,(0,250,0),box)
            #adaugam peste celula poza cu caracterul (daca este cazul)
            if table[row][col]=='X':
                display.blit(x_piece_image,(col*(width_box+1),row*(height_box+1)))
            elif table[row][col]=='0':
                display.blit(o_piece_image,(col*(width_box+1),row*(height_box+1)))
        grid.append(grid_row)

    pygame.display.flip()
    return grid

def main():
    algo_type=None
    while True: #loop pentru selectarea algoritmului de joc
        algo_type=input('Which algorithm shall the computer use?\n1. Minimax\n2. Alpha-beta\n')
        if algo_type in ['1','2']:
            break
        else:
            print('Invalid algo')

    player_character=None
    while True: #loop pentru selectarea caracterului jucatorului
        player_character = input('Choose a character. Keep in mind that X always starts. Press 1 or 2.\n1. Play with X\n2. Play with O\n')
        if player_character=='1':
            player_character='X'
            break
        elif player_character=='2':
            player_character='0'
            break
        else:
            print('Wrong pick. Try again' + player_character)

    depth=None
    while True:#loop pentru selectarea dificultatii (depth-ului algoritmilor)
        difficulty=input('Choose difficulty. Press 1, 2 or 3.\n1. Easy\n2. Medium\n3. Hard\n')

        if difficulty=='1':
            depth=2
            break
        elif difficulty=='2':
            depth=3
            break
        elif difficulty=='3':
            depth=4
            break
        else:
            print('Unclear instructions. Try again.')

    play_game(algo_type,depth,player_character) #incepem jocul

if __name__=='__main__':
    main()