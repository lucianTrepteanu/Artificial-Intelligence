import sys
import copy
from time import time
import bintrees

#constanta pentru INFINIT
K_MAX=10**9

#intoarce cate litere distincte sunt intr-un string
def get_cardinal(string:str):
    temp_dict={} #folosim un dictionar cu frecvente de caractere
    for i in range(len(string)):
        ch=string[i]
        if ch in temp_dict:
            temp_dict[ch]=temp_dict[ch]+1
        else:
            temp_dict[ch]=1
    dist_chars=temp_dict.keys().__len__() #intoarcem cate chei are dictionarul
    del temp_dict
    return dist_chars

#verifica daca o stiva e formata doar din cuvinte anagrame
def good_stack(stack):
    temp_dict={}
    if len(stack)<1: #daca stiva nu are cel putin 2 elemente
        return True

    string1=stack[0] #facem un dictionar cu aparitiile literelor in primul cuvant (frecvente)
    for i in range(len(string1)):
        ch=string1[i]
        if ch in temp_dict:
            temp_dict[ch]=temp_dict[ch]+1
        else:
            temp_dict[ch]=1

    for string in stack[1:]: #pentru celelalte cuvinte facem un dictionar cu frecventele literelor si compara
        new_dict={}
        for i in range(len(string)):
            ch=string[i]
            if ch in new_dict:
                new_dict[ch]=new_dict[ch]+1
            else:
                new_dict[ch]=1

        if temp_dict != new_dict: #daca are alt multiset de litere nu e anagrama si stiva nu poate face parte din stare finala
            return False

    return True

#verifica daca o stare este finala
def final_state(state):
    for stack in state: #verifica daca fiecare stiva este corecta (formata doar din anagrame)
        if good_stack(stack) == False:
            return False
    return True

#nodul grafului pentru astra
class Node:
    def __init__(self,state,parent):
        self.state=state #stare
        self.parent=parent #parinte in parcurgere
        self.parent_cost=1 #costul muchiei de la parinte

        self.g=K_MAX
        self.h=K_MAX
        self.f=K_MAX

    #reconstituie drumul in graf
    def get_path(self):
        node_list=[]
        node=self
        while node is not None:
            node_list.append(node)
            node=node.parent

        path=""
        for i in range(len(node_list)-1,-1,-1):
            path+=node_list[i].__repr__()
        return path

    #Starea se va afisa ca stive puse una sub alta, cu top-ul in stanga
    def __repr__(self):
        string="State (top of stack on leftside):\n"

        stack_list=[]
        for i in range(len(self.state)):
            stack_string="["
            for j in range(len(self.state[i])):
                stack_string+=str(self.state[i][j])
                if j<len(self.state[i])-1:
                    stack_string+=" "
            stack_string+="]\n"
            stack_list.append(stack_string)

        for stack_string in stack_list:
            string+=stack_string
        string+="\n"
        return string

    def __eq__(self, other):
        return self.f==other.f and self.state==other.state

    def __lt__(self, other):
        return (self.f<other.f) or (self.f==other.f and self.state<other.state)

    def __le__(self, other):
        return self==other or self<other

#graf pentru astar
class Graph:
    def __init__(self,start_config):
        self.start_config=start_config #configuratia de start
        self.size=len(start_config) #numar de stive

    def expand(self,node:Node)->list: #determinarea succesorilor unui nod
        expand_list=[]

        for i in range(self.size): #parcurgem fiecare stiva nevida
            if len(node.state[i])>0:
                state_copy=copy.deepcopy(node.state)
                aux_node=Node(state_copy,node)
                element=aux_node.state[i].pop(0)

                for j in range(self.size): #incercam sa mutam varful stivei i in stiva j(fiecare din celelalte stive)
                    if i != j:
                        state_new=copy.deepcopy(aux_node.state)
                        next_node=Node(state_new,node)

                        dist1=get_cardinal(element)
                        if(next_node.state[j].__len__()>0): #daca in stiva j exista elemente
                            dist2=get_cardinal(next_node.state[j][0])
                        else: #daca stiva j este vida
                            dist2=0

                        if abs(dist1-dist2)<K: #verificam daca se poate efectua mutarea
                            next_node.parent_cost=len(element)
                            next_node.state[j].insert(0,element)
                            expand_list.append(next_node)

        return expand_list

#euristica 1:
#pentru fiecare stiva parcurgem de la top catre bottom, pana la intalnirea primei perechi de anagrame
#presupunem ca e suficienta o singura mutare pentru fiecare element nepotrivit,
#si ca odata gasite 2 elemente potrivite, cele de jos ar fi si ele anagrame(nefiind nevoie sa fie mutate)
#adaugam la rezultat lungimile string-urilor "nepotrivite"
def compute_heuristic_len(state):
    result=0
    for stack in state:
        for i in range(len(stack)-1):
            test=[]
            test.append(stack[i])
            test.append(stack[i+1])
            if good_stack(test)==True: #daca sunt anagrame
                break
            result+=len(stack[i])

    return result

#euristica 2:
#pentru fiecare stiva parcurgem de la top catre bottom, pana la intalnirea primei perechi de anagrame
#presupunem ca e suficienta o singura mutare pentru fiecare element nepotrivit,
#si ca odata gasite 2 elemente potrivite, cele de jos ar fi si ele anagrame(nefiind nevoie sa fie mutate)
#adaugam la rezultat numarul string-urilor "nepotrivite" (ca si cum costurile ar fi 1)
def compute_heuristic_count(state):
    result=0
    for stack in state:
        for i in range(len(stack)-1):
            test=[]
            test.append(stack[i])
            test.append(stack[i+1])
            if good_stack(test)==True:
                break
            result+=1

    return result

#euristica 3: inadmisibila
#pentru fiecare stiva parcurgem de la top catre bottom, pana la intalnirea primei perechi de anagrame
#presupunem ca e suficienta o singura mutare pentru fiecare element nepotrivit,
#si ca odata gasite 2 elemente potrivite, cele de jos ar fi si ele anagrame(nefiind nevoie sa fie mutate)
#adaugam la rezultat numarul string-urilor "nepotrivite" de deasupra primei potriviri, inmultit cu
#lungimea maxima a unui element din stare (ca si cum costurile elementelor ce trebuie mutate ar fi cat
#mai mari posibile
#se observa ca pe inputul inputbig.txt aceasta supraestimeaza si da rezultat final gresit
def compute_heuristic_maxlen(state):
    result=0
    max_len=0
    for stack in state: #calculam lungimea maxima a unui string din stare (indiferent de stiva)
        for string in stack:
            if len(string)>max_len:
                max_len=len(string)

    for stack in state:
        for i in range(len(stack)-1):
            test=[]
            test.append(stack[i])
            test.append(stack[i+1])
            if good_stack(test)==True:
                break
            result+=(i+1)*max_len

    return result

#implementarea algoritmului astar pe un graf
#al 2-lea parametru este numele euristicii
def astar(graph:Graph,heuristic):
    open_nodes=bintrees.AVLTree() #folosim AVLTree din motive de performanta (optimizare)
    fg_values=bintrees.AVLTree()

    start_node=Node(graph.start_config,None)

    start_node.g=0
    if heuristic=="len": #in functie de euristica daca, initializam euristica nodului de start
        start_node.h=compute_heuristic_len(start_node.state)
    elif heuristic=="count":
        start_node.h=compute_heuristic_count(start_node.state)
    else:
        start_node.h=compute_heuristic_maxlen(start_node.state)

    start_node.f=start_node.g+start_node.h

    open_nodes[start_node]=0
    fg_values[start_node.state]=(start_node.f,start_node.g)

    max_states=0
    while len(open_nodes)>0:
        max_states=max(max_states,open_nodes.__len__())
        curr_node=open_nodes.pop_min()[0]

        if curr_node is None:
            print("Current node is None.")
            exit(0)

        if final_state(curr_node.state):
            print("Total nr of states visited: "+str(fg_values.__len__()))
            print("Maximum nr of states in open_list: "+str(max_states))
            return curr_node.get_path(),curr_node.g


        neighbours=graph.expand(curr_node)
        for next_node in neighbours:
            next_node.g=curr_node.g+next_node.parent_cost
            if heuristic=="len":
                next_node.h=compute_heuristic_len(next_node.state)
            elif heuristic=="count":
                next_node.h=compute_heuristic_count(next_node.state)
            else:
                next_node.h=compute_heuristic_maxlen(next_node.state)

            next_node.f=next_node.g+next_node.h

            if fg_values.__contains__(next_node.state) == False:
                fg_values[next_node.state]=(next_node.f,next_node.g)
                open_nodes[next_node]=next_node.g
            elif next_node.g<fg_values[next_node.state][1]:
                aux_node=Node(next_node.state,None)
                aux_node.f=fg_values[next_node.state][0]

                fg_values[next_node.state]=(next_node.f,next_node.g)
                if open_nodes.__contains__(aux_node) == False:
                    open_nodes[next_node]=next_node.g
                else:
                    open_nodes.remove(aux_node)
                    open_nodes[next_node]=next_node.g

    return None,None

#functie de citire a input-ului dintr-un fisier text
#formatul este: K pe prima linie
# pe fiecare linie de dupa, separate prin spatii, configuratiile stivelor
def read_data(input_file):
    file=open(input_file,"r")
    K=int(file.readline())
    start_config=[]
    for line in file:
        stack=line.rstrip().split(' ')
        start_config.append(stack)

    return start_config,K

if __name__=="__main__":
    input_file=sys.argv[1] #dam numele inputului ca argument
    start_config,K=read_data(input_file) #citim datele

    graph=Graph(start_config)#initializam graful

    for heuristic in ["len","count","maxlen"]: #pentru fiecare euristica rulam inputul
        t0=time()
        res,cost=astar(graph,heuristic)
        t1=time()

        output=open("output"+heuristic+".txt","w") #scriem rezultatele si statisticile in fisierele corespunzatoare
        if res is not None:
            output.write(res)
        else:
            output.write("No solution found\n")
        output.write("Cost: "+str(cost)+"\n")

        output.write("Execution time: "+str(round(1000*(t1-t0),2))+" ms\n")
        output.close()