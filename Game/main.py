import game_console
import game_ui
import argparse
import sys

if __name__=="__main__":
    if len(sys.argv)==1: #daca nu avem argumente la executie
        game_console.main()
    else:
        if sys.argv[1]=='-gui': #daca avem primul argument (dupa numele programului,evident) '-gui'
            game_ui.main()
        else: #daca avem un alt prim argument invalid
            print("Parametri incorecti. Reincercati!")