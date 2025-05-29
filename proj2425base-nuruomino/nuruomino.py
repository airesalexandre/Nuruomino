# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 50:
# 110421 Alexandre Aires
# 109416 Pedro Veríssimo

from search import Problem, Node
import sys
from collections import defaultdict
from utils import *
import numpy as np

class NuruominoState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NuruominoState.state_id
        NuruominoState.state_id += 1

    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas. """
        return self.id < other.id

class Board:
    """Representação interna de um tabuleiro do Puzzle Nuruomino."""

    def __init__(self, grid, regions):
        self.grid = grid
        self.regions = regions

    def adjacent_regions(self, region:int) -> list:
        """Devolve uma lista das regiões que fazem fronteira com a região enviada no argumento."""
        adj = set()
        for (row, col) in self.regions[region]:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0]):
                        reg = self.grid[nr][nc]
                        if reg != region:
                            adj.add(reg)
        return list(adj)

    def adjacent_positions(self, row:int, col:int) -> list:
        """Devolve as posições adjacentes à posição (row, col), em todas as direções, incluindo diagonais."""
        positions = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0]):
                    positions.append((nr, nc))
        return positions

    def adjacent_values(self, row:int, col:int) -> list:
        """Devolve os valores das células adjacentes à posição (row, col), em todas as direções, incluindo diagonais."""
        values = []
        for (nr, nc) in self.adjacent_positions(row, col):
            values.append(self.grid[nr][nc])
        return values
    
    def get_value(self, row, col):
        """Retorna o valor preenchido na posição (row, col) do tabuleiro."""
        return self.grid[row][col]
    
    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
        """
        #TODO
        grid = []
        regions = defaultdict(list)
        for r, line in enumerate(sys.stdin):
            tokens = line.strip().split()
            row = [int(tok) for tok in tokens]
            grid.append(row)

            for c, region_id in enumerate(row):
                regions[region_id].append((r, c))

        return Board(grid, dict(regions))  # converte defaultdict em dict normal
    
    def print_instance(self):
        """Imprime o tabuleiro no formato especificado: uma linha por linha, valores separados por tabulação."""
        for row in self.grid:
            print('\t'.join(str(cell) for cell in row))
    # TODO: outros metodos da classe Board
    

class Nuruomino(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        #TODO
        self.initial = NuruominoState(board)
        self.board = board
        pass 

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        #TODO
        pass 

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        #TODO
        pass 
        

    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #TODO
        pass 

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass







#PRINTS PARA DEBUG
if __name__ == "__main__":
    board = Board.parse_instance()
    board.print_instance()
    problem = Nuruomino(board)
    # Criar um estado com a configuração inicial:
    initial_state = NuruominoState(board)
    # Mostrar valor na posição (2, 1):
    print(initial_state.board.get_value(2, 1))