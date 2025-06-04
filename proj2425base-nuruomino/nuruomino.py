# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 50:
# 110421 Alexandre Aires
# 109416 Pedro Veríssimo

import sys
from collections import defaultdict
import copy


def depth_first_search(initial_state, actions_fn, result_fn, goal_test_fn):
    """Simple DFS using native Python only."""
    stack = [initial_state]
    visited = set()

    while stack:
        state = stack.pop()
        sid = state.signature()
        if sid in visited:
            continue
        visited.add(sid)
        if goal_test_fn(state):
            return state
        for action in actions_fn(state):
            child = result_fn(state, action)
            stack.append(child)
    return None


class NuruominoState:
    def __init__(self, board):
        self.board = board

    def signature(self):
        # Unique signature based on board grid
        return repr(self.board.grid)


class Board:
    def __init__(self, grid, regions):
        self.grid = grid
        self.regions = regions

    @staticmethod
    def parse_instance():
        grid = []
        regions = defaultdict(list)
        for r, line in enumerate(sys.stdin):
            tokens = line.strip().split()
            if not tokens:
                continue
            row = []
            for c, tok in enumerate(tokens):
                region_id = int(tok)
                row.append(region_id)
                regions[region_id].append((r, c))
            grid.append(row)
        return Board(grid, dict(regions))

    def print(self):
        return "\n".join("\t".join(str(cell) for cell in row) for row in self.grid)

    def adjacent_positions(self, row, col):
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = row+dr, col+dc
            if 0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0]):
                yield (nr, nc)

    def get_value(self, row, col):
        return self.grid[row][col]

    def find_piece_placements(self, region_id, symbol, shape):
        cells = set(self.regions[region_id])
        sr, sc = len(shape), len(shape[0])
        placements = []
        rs = [r for r,_ in cells]; cs = [c for _,c in cells]
        for br in range(min(rs), max(rs)-sr+2):
            for bc in range(min(cs), max(cs)-sc+2):
                coords = []
                ok = True
                for dr in range(sr):
                    for dc in range(sc):
                        if shape[dr][dc]:
                            r, c = br+dr, bc+dc
                            if (r,c) not in cells or not isinstance(self.grid[r][c], int):
                                ok = False; break
                            coords.append((r,c))
                    if not ok: break
                if not ok: continue
                # same-symbol adjacency
                bad = False
                for r,c in coords:
                    for nr,nc in self.adjacent_positions(r,c):
                        if (nr,nc) not in coords and self.grid[nr][nc] == symbol:
                            bad = True; break
                    if bad: break
                if bad: continue
                # 2x2 check
                newg = [row[:] for row in self.grid]
                for r,c in coords: newg[r][c] = symbol
                H, W = len(newg), len(newg[0])
                two = False
                for r,c in coords:
                    for dr in (0,-1):
                        for dc in (0,-1):
                            rr,cc = r+dr, c+dc
                            if 0<=rr<H-1 and 0<=cc<W-1:
                                blk = [newg[rr][cc], newg[rr+1][cc], newg[rr][cc+1], newg[rr+1][cc+1]]
                                if all(isinstance(x,str) for x in blk):
                                    two = True; break
                        if two: break
                    if two: break
                if two: continue
                placements.append((region_id, symbol, coords, shape))
        return placements

    def add_piece(self, symbol, coords):
        newg = [row[:] for row in self.grid]
        for r,c in coords: newg[r][c] = symbol
        return Board(newg, self.regions)


def actions(state):
    # select first region with no letters placed
    for region, cells in state.board.regions.items():
        if all(isinstance(state.board.get_value(r,c), int) for r,c in cells):
            region_id = region
            break
    else:
        return []
    acts = []
    for sym, shape in Nuruomino.pieces:
        for act in state.board.find_piece_placements(region_id, sym, shape):
            acts.append(act)
    return acts


def result(state, action):
    _, sym, coords, _ = action
    return NuruominoState(state.board.add_piece(sym, coords))


def goal_test(state):
    b = state.board
    all_cells = []
    for region, cells in b.regions.items():
        letters = [(r,c) for r,c in cells if isinstance(b.get_value(r,c), str)]
        if len(letters) != 4:
            return False
        sym = b.get_value(*letters[0])
        vis = {letters[0]}
        stk = [letters[0]]
        while stk:
            r,c = stk.pop()
            for nr,nc in b.adjacent_positions(r,c):
                if (nr,nc) in letters and (nr,nc) not in vis and b.get_value(nr,nc)==sym:
                    vis.add((nr,nc)); stk.append((nr,nc))
        if len(vis) != 4:
            return False
        all_cells.extend(letters)
    if not all_cells:
        return False
    vis = {all_cells[0]}
    stk = [all_cells[0]]
    while stk:
        r,c = stk.pop()
        for nr,nc in b.adjacent_positions(r,c):
            if (nr,nc) in all_cells and (nr,nc) not in vis:
                vis.add((nr,nc)); stk.append((nr,nc))
    return len(vis) == len(all_cells)

class Nuruomino:
    pieces = [
        ('L', [[1,1],[1,0],[1,0]]),('L', [[1,1],[0,1],[0,1]]),
        ('L', [[1,0],[1,0],[1,1]]),('L', [[0,1],[0,1],[1,1]]),
        ('L', [[1,1,1],[1,0,0]]),('L', [[1,1,1],[0,0,1]]),
        ('L', [[1,0,0],[1,1,1]]),('L', [[0,0,1],[1,1,1]]),
        ('S', [[1,0],[1,1],[0,1]]),('S', [[0,1],[1,1],[1,0]]),
        ('S', [[1,1,0],[0,1,1]]),('S', [[0,1,1],[1,1,0]]),
        ('T', [[1,0],[1,1],[1,0]]),('T', [[0,1],[1,1],[0,1]]),
        ('T', [[1,1,1],[0,1,0]]),('T', [[0,1,0],[1,1,1]]),
        ('I', [[1],[1],[1],[1]]),('I', [[1,1,1,1]]),
    ]

def smart_backtracking(board, pieces):
    regions = set(board.regions.keys())
    min_size = min(len(board.regions[r]) for r in regions)
    region_queue = [r for r in regions if len(board.regions[r]) == min_size]
    filled = set()
    remaining = set(regions)

    def get_adjacent_regions(board, filled, remaining):
        adj = set()
        for reg in filled:
            for r, c in board.regions[reg]:
                for nr, nc in board.adjacent_positions(r, c):
                    for other in remaining:
                        if (nr, nc) in board.regions[other]:
                            adj.add(other)
        return list(adj)

    def has_conflict(board, region, action):
        symbol, coords, shape = action[1], action[2], action[3]
        # 1. Tetrominos iguais ortogonalmente adjacentes de regiões diferentes
        for (r, c) in coords:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(board.grid) and 0 <= nc < len(board.grid[0]):
                    neighbor = board.get_value(nr, nc)
                    if neighbor == symbol:
                        reg1 = reg2 = None
                        for reg_id, cells in board.regions.items():
                            if (r, c) in cells: reg1 = reg_id
                            if (nr, nc) in cells: reg2 = reg_id
                        if reg1 is not None and reg2 is not None and reg1 != reg2:
                            return True
        # 2. Bloco 2x2 de letras
        for (r, c) in coords:
            for dr in [0, -1]:
                for dc in [0, -1]:
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < len(board.grid)-1 and 0 <= cc < len(board.grid[0])-1:
                        block = [board.get_value(rr, cc), board.get_value(rr+1, cc),
                                 board.get_value(rr, cc+1), board.get_value(rr+1, cc+1)]
                        if all(isinstance(x, str) for x in block):
                            return True
        return False

    def goal_test(board):
        # Usa o teu goal_test atual, ou adapta conforme necessário
        b = board
        all_cells = []
        for region, cells in b.regions.items():
            letters = [(r,c) for r,c in cells if isinstance(b.get_value(r,c), str)]
            if len(letters) != 4:
                return False
            sym = b.get_value(*letters[0])
            vis = {letters[0]}
            stk = [letters[0]]
            while stk:
                r,c = stk.pop()
                for nr,nc in b.adjacent_positions(r,c):
                    if (nr,nc) in letters and (nr,nc) not in vis and b.get_value(nr,nc)==sym:
                        vis.add((nr,nc)); stk.append((nr,nc))
            if len(vis) != 4:
                return False
            all_cells.extend(letters)
        if not all_cells:
            return False
        vis = {all_cells[0]}
        stk = [all_cells[0]]
        while stk:
            r,c = stk.pop()
            for nr,nc in b.adjacent_positions(r,c):
                if (nr,nc) in all_cells and (nr,nc) not in vis:
                    vis.add((nr,nc)); stk.append((nr,nc))
        return len(vis) == len(all_cells)

    def backtrack(board, region_queue, filled, remaining):
        if not remaining:
            if goal_test(board):
                return board
            return None
        if not region_queue:
            next_min = min(remaining, key=lambda r: len(board.regions[r]))
            region_queue = [next_min]
        region = select_next_region(board, region_queue, remaining, pieces)
        region_queue.remove(region)
        remaining = remaining - {region}
        for symbol, shape in pieces:
            for (region_id, symbol, coords, shape) in board.find_piece_placements(region, symbol, shape):
                new_board = board.add_piece(symbol, coords)
                #print(f"\n--- Peça '{symbol}' colocada na região {region} ---")
                #print(new_board.print())
                if not has_conflict(new_board, region, (region_id, symbol, coords, shape)):
                    new_filled = filled | {region}
                    new_adjacents = get_adjacent_regions(board, [region], remaining)
                    new_queue = region_queue + [r for r in new_adjacents if r not in region_queue]
                    if forward_check(new_board, new_queue, remaining, pieces):
                        result = backtrack(new_board, new_queue, new_filled, remaining)
                        if result is not None:
                            return result
        #print(f"❌ Nenhuma peça válida para a região {region}. A fazer backtrack...\n")
        return None


    return backtrack(board, region_queue, filled, remaining)

def select_next_region(board, region_queue, remaining, pieces):
    min_actions = float('inf')
    best_region = None
    for region in region_queue:
        actions = 0
        for symbol, shape in pieces:
            actions += len(board.find_piece_placements(region, symbol, shape))
        if actions < min_actions:
            min_actions = actions
            best_region = region
    return best_region

def forward_check(board, region_queue, remaining, pieces):
    for reg in region_queue:
        possible = False
        for symbol, shape in pieces:
            if board.find_piece_placements(reg, symbol, shape):
                possible = True
                break
        if not possible:
            return False
    return True

if __name__ == "__main__":
    board = Board.parse_instance()
    sol_board = smart_backtracking(board, Nuruomino.pieces)
    if sol_board:
        #print("\n\n\n")
        print(sol_board.print())
    else:
        print("Nenhuma solução encontrada.")
