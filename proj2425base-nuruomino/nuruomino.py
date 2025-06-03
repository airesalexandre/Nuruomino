# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 50:
# 110421 Alexandre Aires
# 109416 Pedro Veríssimo

from search import Problem, Node, depth_first_tree_search, astar_search, greedy_search
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

    
    def find_piece_placements(self, region_id, symbol, shape):
        """
        Returns a list of all valid placements for a piece (shape) in the given region.
        Each placement is a tuple: (region_id, symbol, [(r, c), ...], shape)
        Allows placement anywhere in the region as long as all cells are in the region and unoccupied.
        """
        region_cells = set(self.regions[region_id])
        sh_rows, sh_cols = len(shape), len(shape[0])
        placements = []
        # Try every possible anchor (top-left) position in the region's bounding box
        min_r = min(r for r, c in region_cells)
        max_r = max(r for r, c in region_cells)
        min_c = min(c for r, c in region_cells)
        max_c = max(c for r, c in region_cells)
        for base_r in range(min_r, max_r - sh_rows + 2):
            for base_c in range(min_c, max_c - sh_cols + 2):
                fits = True
                cells_to_fill = []
                for dr in range(sh_rows):
                    for dc in range(sh_cols):
                        if shape[dr][dc]:
                            r, c = base_r + dr, base_c + dc
                            if (r, c) not in region_cells:
                                fits = False
                                break
                            if not isinstance(self.grid[r][c], int):
                                fits = False
                                break
                            cells_to_fill.append((r, c))
                    if not fits:
                        break
                if not fits:
                    continue
                # Check if connects with same symbol
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
                # Check for 2x2 block with letters
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
                placements.append((region_id, symbol, cells_to_fill, shape))
        return placements

    def add_piece(self, symbol, coords):
        """
        Returns a new Board with the piece (symbol, shape) placed at the given coordinates (list of (r, c)).
        Does not check validity, assumes coords is a valid placement.
        """
        new_grid = [row[:] for row in self.grid]
        for (r, c) in coords:
            new_grid[r][c] = symbol
        return Board(new_grid, self.regions)
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

    def dfs_backjumping(problem):
        regions = list(problem.board.regions.keys())
        assignment = {}
        conflict_sets = {region: set() for region in regions}

        def is_consistent(region, action, assignment):
            # Cria um tabuleiro temporário com as peças já colocadas
            board = problem.board
            for reg, act in assignment.items():
                board = board.add_piece(act[1], act[2])
            # Tenta adicionar a nova peça
            try:
                board = board.add_piece(action[1], action[2])
            except Exception:
                return False
            # Verifica restrições locais/globais (podes usar partes do goal_test)
            return not has_conflict(board, region, action)

        def has_conflict(board, region, action):
            # Exemplo: verifica se há tetrominos adjacentes iguais ou blocos 2x2
            # Podes adaptar com partes do teu goal_test
            return False  # Implementa conforme necessário

        def actions_for_region(region, assignment):
            # Gera todas as ações possíveis para a região, dado o assignment parcial
            board = problem.board
            for reg, act in assignment.items():
                board = board.add_piece(act[1], act[2])
            region_actions = []
            for symbol, shape in problem.pieces:
                placements = board.find_piece_placements(region, symbol, shape)
                for (region_id, symbol, coords, shape) in placements:
                    region_actions.append((region_id, symbol, coords, shape))
            return region_actions

        def backjump(region):
            if not conflict_sets[region]:
                return None
            return max(conflict_sets[region])

        def recursive(region_idx):
            if region_idx == len(regions):
                return assignment  # solução encontrada

            region = regions[region_idx]
            for action in actions_for_region(region, assignment):
                if is_consistent(region, action, assignment):
                    assignment[region] = action
                    result = recursive(region_idx + 1)
                    if result is not None:
                        return result
                    del assignment[region]
                else:
                    for prev_region in assignment:
                        conflict_sets[region].add(prev_region)
                    jump_to = backjump(region)
                    if jump_to is not None:
                        return None
            return None

        return recursive(0)

    def actions(self, state: NuruominoState):
        """
        Retorna uma lista de ações possíveis a partir do estado, com limitações e ordenação
        para acelerar procura em tabuleiros grandes.
        Cada ação inclui também as coordenadas onde a peça pode ser colocada.
        """
        MAX_ACTIONS_PER_REGION = 30  # Evita explosão combinatória

        region_order = sorted(state.board.regions.items(), key=lambda item: len(item[1]))  # Prioriza regiões menores
        actions = []

        for region_id, cells in region_order:
            region_free = any(isinstance(state.board.get_value(r, c), int) for (r, c) in cells)
            if not region_free:
                continue

            region_size = len(cells)
            if region_size < 4:
                continue  # Região impossível de preencher

            region_actions = []

            for symbol, shape in self.pieces:
                # Otimização: só tenta peças com <= número de células da região
                piece_cells = sum(cell for row in shape for cell in row)
                if piece_cells > region_size:
                    continue

                placements = state.board.find_piece_placements(region_id, symbol, shape)

                for (region_id, symbol, coords, shape) in placements:
                    # Avaliar qualidade da ação: menos conflitos, mais preenchimento
                    conflict_score = 0
                    for (r, c) in coords:
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < len(state.board.grid) and 0 <= nc < len(state.board.grid[0]):
                                neighbor = state.board.get_value(nr, nc)
                                if neighbor == symbol:
                                    conflict_score += 1  # tetromino igual adjacente

                    # Agora a ação inclui as coordenadas onde a peça pode ser colocada
                    region_actions.append(((region_id, symbol, coords, shape), -len(coords), conflict_score))

            # Ordenar: preferir peças que cobrem mais células e com menos conflitos
            region_actions.sort(key=lambda x: (x[1], x[2]))

            # Só considera as melhores N ações desta região
            top_actions = [x[0] for x in region_actions[:MAX_ACTIONS_PER_REGION]]
            if top_actions:
                return top_actions  # Só processa a primeira região com ações viáveis

        return actions



    def result(self, state: NuruominoState, action):
        """
        Executa a ação sobre o estado e retorna um novo estado resultante.
        action: (region_id, symbol, coords, shape)
        """
        _, symbol, coords, _ = action
        new_board = state.board.add_piece(symbol, coords)
        return NuruominoState(new_board)

    def goal_test(self, state: NuruominoState):
        """
        Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Cada região deve conter exatamente um grupo de 4 células conectadas ortogonalmente com o mesmo símbolo (tetromino),
        e todos os tetrominos devem estar ortogonalmente conectados (formar um único grupo).
        """
        board = state.board
        tetromino_cells = set()
        # Para cada região, encontrar grupos de 4 células conectadas ortogonalmente com o mesmo símbolo
        for region_id, cells in board.regions.items():
            region_letters = [(r, c) for (r, c) in cells if isinstance(board.get_value(r, c), str)]
            if len(region_letters) < 4:
                return False
            # Encontrar grupos de células conectadas ortogonalmente com o mesmo símbolo
            visited = set()
            found_tetromino = False
            for (r, c) in region_letters:
                if (r, c) in visited:
                    continue
                symbol = board.get_value(r, c)
                # BFS para grupo de mesmo símbolo
                group = set()
                queue = [(r, c)]
                while queue:
                    rr, cc = queue.pop()
                    if (rr, cc) in group:
                        continue
                    if board.get_value(rr, cc) != symbol:
                        continue
                    group.add((rr, cc))
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nr, nc = rr + dr, cc + dc
                        if (nr, nc) in region_letters and (nr, nc) not in group:
                            queue.append((nr, nc))
                if len(group) == 4:
                    if found_tetromino:
                        # Mais de um tetromino na região
                        return False
                    found_tetromino = True
                    tetromino_cells.update(group)
                    visited.update(group)
                elif len(group) > 0:
                    # Grupo inválido (não é tetromino)
                    visited.update(group)
            if not found_tetromino:
                return False
        # Verificar se todos os tetrominos estão ortogonalmente conectados
        if not tetromino_cells:
            return False
        visited = set()
        queue = [next(iter(tetromino_cells))]
        while queue:
            r, c = queue.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in tetromino_cells and (nr, nc) not in visited:
                    queue.append((nr, nc))
        return visited == tetromino_cells

    

    def h(self, node: Node):
        board = node.state.board
        hval = 0

        for _, cells in board.regions.items():
            letter_cells = [(r, c) for (r, c) in cells if isinstance(board.get_value(r, c), str)]
            empty_cells = [(r, c) for (r, c) in cells if isinstance(board.get_value(r, c), int)]

            #1. Penalizar regiões com menos de 4 células livres
            if len(letter_cells) == 0 and len(empty_cells) < 4:
                hval += 1000  # região impossível de preencher
                continue

            #2. Penalizar regiões fragmentadas com várias componentes
            visited = set()
            components = 0
            for (r, c) in letter_cells:
                if (r, c) in visited:
                    continue
                components += 1
                symbol = board.get_value(r, c)
                queue = [(r, c)]
                while queue:
                    rr, cc = queue.pop()
                    if (rr, cc) in visited or board.get_value(rr, cc) != symbol:
                        continue
                    visited.add((rr, cc))
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nr, nc = rr + dr, cc + dc
                        if (nr, nc) in letter_cells and (nr, nc) not in visited:
                            queue.append((nr, nc))
            if components > 1:
                hval += 5 * (components - 1)

            #3. Penalizar regiões que têm parte de tetrominos mas que não podem mais atingir 4 células
            if 0 < len(letter_cells) < 4 and len(letter_cells) + len(empty_cells) < 4:
                hval += 1000  # região já colocada parcialmente, mas sem espaço para completar

            #4. Penalizar tetrominos iguais ortogonalmente adjacentes (mesmo símbolo)
            for (r, c) in letter_cells:
                symbol = board.get_value(r, c)
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(board.grid) and 0 <= nc < len(board.grid[0]):
                        neighbor = board.get_value(nr, nc)
                        if neighbor == symbol and (nr, nc) not in cells:
                            hval += 10  # conflito de tetrominos adjacentes

            #5. Estimativa de peças necessárias ainda nesta região
            hval += (len(empty_cells) + 3) // 4

        #6. Penalizar blocos 2x2 de letras (nuricabe inválido)
        grid = board.grid
        for r in range(len(grid) - 1):
            for c in range(len(grid[0]) - 1):
                block = [grid[r][c], grid[r+1][c], grid[r][c+1], grid[r+1][c+1]]
                if all(isinstance(x, str) for x in block):
                    hval += 500  # grande penalização

        return hval








#PRINTS PARA DEBUG
if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Nuruomino(board)
    solution = Nuruomino.dfs_backjumping(problem)
    if solution:
        b = board
        for region in sorted(solution):
            _, symbol, coords, _ = solution[region]
            b = b.add_piece(symbol, coords)
        print("Solução encontrada:")
        print(b.print())
    else:
        print("Nenhuma solução encontrada.")
