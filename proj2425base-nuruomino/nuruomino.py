# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 50:
# 110421 Alexandre Aires
# 109416 Pedro Veríssimo

import sys
from collections import defaultdict


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

if __name__ == "__main__":
    board = Board.parse_instance()
    init = NuruominoState(board)
    sol = depth_first_search(init, actions, result, goal_test)
    if sol:
        print(sol.board.print())
    else:
        print("Nenhuma solução encontrada.")
