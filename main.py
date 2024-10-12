import pygame
import random

"""
Rules of Conway's Game of Life:

1. A live cell with less than two live neighbors dies (underpopulation).
2. A live cell with two or three live neighbors lives (survival).
3. A live cell with more than three live neighbors dies (overpopulation).
4. A dead cell with exactly three live neighbors becomes alive (reproduction).

"""

pygame.init()

LINE_COLOR = (0, 0, 0)
BG_COLOR = (128, 128, 128)
TILE_COLOR = (255, 255, 0)

WIDTH, HEIGHT = 800, 800
TILE_SIZE = 2
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE
FPS = 60 # Experimental Parameter

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def generate(num):
    return set([(random.randrange(0, GRID_HEIGHT), random.randrange(0, GRID_WIDTH)) for i in range(num)])

def draw_grid(positions):
    for position in positions:
        col, row = position
        top_left = (col * TILE_SIZE, row * TILE_SIZE)
        pygame.draw.rect(screen, TILE_COLOR, (*top_left, TILE_SIZE, TILE_SIZE))

    for row in range(GRID_HEIGHT):
        pygame.draw.line(screen, LINE_COLOR, (0, row * TILE_SIZE), (WIDTH, row * TILE_SIZE))

    for col in range(GRID_WIDTH):
        pygame.draw.line(screen, LINE_COLOR, (col * TILE_SIZE, 0), (col * TILE_SIZE, HEIGHT))    

def adjust_grid(positions):

    # Stores all neighbors of all live cells of the current set of positions
    all_neighbors = set()
    # What is updated after adjust_grid
    new_positions = set()

    # Going through live cells
    for position in positions: 
        # Get neighboring coordinates
        neighbors = get_neighbors(position)
        # Update neighbors for later use
        all_neighbors.update(neighbors)

        # Filter only for live cells
        neighbors = list(filter(lambda x: x in positions, neighbors))

        # If live cell amount is 2 or 3, keep cell position
        if len(neighbors) in [2, 3]:
            new_positions.add(position)

    # Loop through all neighbors of live cells
    for position in all_neighbors:
        neighbors = get_neighbors(position)
        # Check live neighbors of live neighbors
        neighbors = list(filter(lambda x: x in positions, neighbors))

        # If they have three live neighbors, alive the adjacent cell
        if len(neighbors) == 3:
            new_positions.add(position)

    return new_positions

def get_neighbors(pos):

    # 8 possible neighbors

    x, y = pos
    neighbors = []
    # Loop through nine possible positions using x/y displacement, if 0, 0, ignore
    for dx in [-1, 0, 1]:
        # Avoid off-screen position (x)
        if x + dx < 0 or x + dx > GRID_WIDTH:
            continue
        for dy in [-1, 0, 1]:
            # Avoid off-screen position (y)
            if y + dy < 0 or y + dy > GRID_HEIGHT:
                continue
            if dx == 0 and dy == 0:
                continue

            neighbors.append((x + dx, y + dy))

    return neighbors


def main():
    running = True
    playing = False
    count = 0
    update_freq = 5 # Experimental Parameter

    positions = set()

    while running:
        clock.tick(FPS)

        if playing:
            count += 1

        if count >= update_freq:
            count = 0
            positions = adjust_grid(positions)

        pygame.display.set_caption("Playing" if playing else "Paused")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // TILE_SIZE
                row = y // TILE_SIZE
                pos = (col, row)

                if pos in positions:
                    positions.remove(pos)
                else:
                    positions.add(pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    playing = not playing
                
                if event.key == pygame.K_c:
                    positions = set()
                    playing = False
                    count = 0

                if event.key == pygame.K_g:
                    positions = generate(random.randrange(200, 400) * GRID_WIDTH)

                


        screen.fill(BG_COLOR)
        draw_grid(positions)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()