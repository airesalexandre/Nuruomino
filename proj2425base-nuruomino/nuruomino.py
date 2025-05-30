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
import copy


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
    
    def print(self):
        """Retorna uma string com o tabuleiro no formato especificado: uma linha por linha, valores separados por tabulação."""
        lines = []
        for row in self.grid:
            lines.append('\t'.join(str(cell) for cell in row))
        return '\n'.join(lines)
    # TODO: outros metodos da classe Board

    
    def place_piece(self, region_id, symbol, shape):
        """
        Coloca a peça (shape) na primeira posição possível da região region_id,
        preenchendo as células correspondentes com o símbolo dado.
        shape: matriz de 0/1 (linhas x colunas)
        symbol: valor a colocar (ex: 'S')
        region_id: região onde tentar encaixar
        Retorna um novo Board com a peça colocada (não altera o original).
        Só coloca se não ligar a peça a outra da mesma letra e não criar 2x2 com letras.
        """
        region_cells = set(self.regions[region_id])
        sh_rows, sh_cols = len(shape), len(shape[0])
        for (base_r, base_c) in region_cells:
            fits = True
            cells_to_fill = []
            for dr in range(sh_rows):
                for dc in range(sh_cols):
                    if shape[dr][dc]:
                        r, c = base_r + dr, base_c + dc
                        if (r, c) not in region_cells:
                            fits = False
                            break
                        # Não pode sobrepor símbolo já colocado
                        if not isinstance(self.grid[r][c], int):
                            fits = False
                            break
                        cells_to_fill.append((r, c))
                if not fits:
                    break
            if not fits:
                continue

            # Verificar se conecta com outra peça do mesmo símbolo
            connects_same = False
            for (r, c) in cells_to_fill:
                for (nr, nc) in self.adjacent_positions(r, c):
                    if (nr, nc) not in cells_to_fill:
                        if self.grid[nr][nc] == symbol:
                            connects_same = True
                            break
                if connects_same:
                    break
            if connects_same:
                continue

            # Verificar se cria bloco 2x2 com letras (em qualquer posição da peça)
            creates_2x2 = False
            new_grid = [row[:] for row in self.grid]
            for (r, c) in cells_to_fill:
                new_grid[r][c] = symbol
            for (r, c) in cells_to_fill:
                for dr in [0, -1]:
                    for dc in [0, -1]:
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < len(new_grid)-1 and 0 <= cc < len(new_grid[0])-1:
                            block = [new_grid[rr][cc], new_grid[rr+1][cc], new_grid[rr][cc+1], new_grid[rr+1][cc+1]]
                            if all(isinstance(x, str) for x in block):
                                creates_2x2 = True
                                break
                    if creates_2x2:
                        break
                if creates_2x2:
                    break
            if creates_2x2:
                continue

            # Se passou todos os testes, retorna novo Board
            return Board(new_grid, self.regions)
        # Se não couber, retorna None
        return None
#-------------------------------------------------------------------------------------------------------------
class Nuruomino(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.initial = NuruominoState(board)
        self.board = board

    pieces = [('L', [[1, 1],[1, 0],[1, 0]]),
                  ('L', [[1, 1],[0, 1],[0, 1]]),
                  ('L', [[1, 0],[1, 0],[1, 1]]),
                  ('L', [[0, 1],[0, 1],[1, 1]]),
                  ('L', [[1, 1, 1],[1, 0, 0]]),
                  ('L', [[1, 1, 1],[0, 0, 1]]),
                  ('L', [[1, 0, 0],[1, 1, 1]]),
                  ('L', [[0, 0, 1],[1, 1, 1]]),
                  ('S', [[1, 0], [1, 1],[0, 1]]),
                  ('S', [[0, 1], [1, 1],[1, 0]]),
                  ('S', [[1, 1, 0], [0, 1, 1]]),
                  ('S', [[0, 1, 1], [1, 1, 0]]),
                  ('T', [[1, 0], [1, 1],[1, 0]]),
                  ('T', [[0, 1], [1, 1],[0, 1]]),
                  ('T', [[1, 1, 1], [0, 1, 0]]),
                  ('T', [[0, 1, 0], [1, 1, 1]]),
                  ('I', [[1],[1],[1],[1]]),
                  ('I', [[1, 1, 1, 1]]),]

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        actions = []

        for region_id, cells in state.board.regions.items():
            # Só tenta regiões que ainda têm células livres (assumindo int como livre)
            region_free = any(isinstance(state.board.get_value(r, c), int) for (r, c) in cells)
            if not region_free:
                continue
            for symbol, shape in self.pieces:
                # Só adiciona a ação se for possível colocar a peça nesta região
                if state.board.place_piece(region_id, symbol, shape) is not None:
                    actions.append((region_id, symbol, shape))
        return actions


    def result(self, state: NuruominoState, action):
        """
        Executa a ação sobre o estado e retorna um novo estado resultante.
        action: (region_id, symbol, shape)
        """
        region_id, symbol, shape = action
        new_board = state.board.place_piece(region_id, symbol, shape)
        if new_board is None:
            # Se não for possível colocar a peça, retorna o estado original (ou pode lançar exceção)
            return state
        return NuruominoState(new_board)

    def goal_test(self, state: NuruominoState):
        """
        Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Cada região deve ter 4 letras (uma peça) e
        cada tetromino deve estar ortogonalmente conectado a pelo menos
        um tetromino de outra região (não pode haver tetrominos isolados).
        """
        board = state.board
        # Primeiro, verifica se todas as regiões têm exatamente 4 letras
        for region_id, cells in board.regions.items():
            region_letters = [(r, c) for (r, c) in cells if isinstance(board.get_value(r, c), str)]
            if len(region_letters) != 4:
                return False

        # Agora, verifica se cada tetromino está conectado a pelo menos um de outra região
        for region_id, cells in board.regions.items():
            region_letters = [(r, c) for (r, c) in cells if isinstance(board.get_value(r, c), str)]
            if not region_letters:
                continue
            connected_to_other = False
            for (r, c) in region_letters:
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < len(board.grid) and 0 <= nc < len(board.grid[0]):
                        neighbor_val = board.get_value(nr, nc)
                        # Se for letra e não for da mesma região, está conectado a outro tetromino
                        if isinstance(neighbor_val, str) and (nr, nc) not in region_letters:
                            # Descobre a que região pertence o vizinho
                            for other_region_id, other_cells in board.regions.items():
                                if other_region_id != region_id and (nr, nc) in other_cells:
                                    connected_to_other = True
                                    break
                        if connected_to_other:
                            break
                if connected_to_other:
                    break
            if not connected_to_other:
                return False
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass







#PRINTS PARA DEBUG
if __name__ == "__main__":
    # Ler grelha do figura 1a:
    board = Board.parse_instance()
    # Criar uma instância de Nuruomino:
    problem = Nuruomino(board)
    
        # Criar um estado com a configuração inicial:
    s0 = NuruominoState(board)
    # Aplicar as ações que resolvem a instância
    s1 = problem.result(s0, (1, 'L', [[1, 1],[1, 0],[1, 0]]))
    s2 = problem.result(s1, (2, 'S', [[1, 0], [1, 1],[0, 1]]))
    s3 = problem.result(s2, (3, 'T', [[1, 0],[1, 1],[1, 0]]))
    s4 = problem.result(s3, (4, 'L', [[1, 1, 1],[1, 0, 0]]))
    s5 = problem.result(s4, (5, 'I', [[1],[1],[1],[1]]))

    print("Is goal?", problem.goal_test(s2))
    print("Is goal?", problem.goal_test(s5))
    print("Solution:\n", s5.board.print(), sep="")
    
