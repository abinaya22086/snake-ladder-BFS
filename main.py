# Snake and Ladder Solver using BFS
from collections import deque

N = 30
moves = {
    3: 22, 5: 8, 11: 26, 20: 29,   # ladders
    17: 4, 19: 7, 21: 9, 27: 1     # snakes
}

def min_dice_throws(moves, N):
    visited = [False] * (N + 1)
    q = deque()
    q.append((1, 0))
    visited[1] = True

    while q:
        cell, dice = q.popleft()
        if cell == N:
            return dice

        for step in range(1, 7):
            next_cell = cell + step
            if next_cell <= N and not visited[next_cell]:
                visited[next_cell] = True
                dest = moves.get(next_cell, next_cell)
                q.append((dest, dice + 1))
    return -1

def main():
    print("\n🎲 Snake and Ladder Solver using BFS 🎲")
    print("---------------------------------------")
    print("Snakes & Ladders (start → end):")
    for k, v in moves.items():
        print(f"  {k} → {v}")

    result = min_dice_throws(moves, N)
    print(f"\n✅ Minimum dice throws required to reach cell {N}: {result}")

if __name__ == "__main__":
    main()
