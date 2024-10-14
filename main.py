import pygame
import random
import json

"""
Rules of Conway's Game of Life:

1. A live cell with less than two live neighbors dies (underpopulation).
2. A live cell with two or three live neighbors lives (survival).
3. A live cell with more than three live neighbors dies (overpopulation).
4. A dead cell with exactly three live neighbors becomes alive (reproduction).

"""

pygame.init()

with open("colors.json", "r") as file:
    COLORS = json.load(file)

LINE_COLOR = tuple(COLORS["LINE_COLOR"])
BG_COLOR = tuple(COLORS["BLACK"])

WIDTH, HEIGHT = 1002, 1002
TILE_SIZE = 2
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE
FPS = 60 # Experimental Parameter

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def get_color(age):
    rainbow = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))

    young_color = tuple(COLORS["YELLOW"])
    old_color = tuple(COLORS["BLACK"])

    max_age = 10 # Experimental Parameter
    age = min(age, max_age)

    ratio = age / max_age
    color = (
        int(young_color[0] * (1 - ratio) + old_color[0] * ratio),
        int(young_color[1] * (1 - ratio) + old_color[1] * ratio),
        int(young_color[2] * (1 - ratio) + old_color[2] * ratio)
    )

    return color

def generate(num):
    return {(random.randrange(0, GRID_WIDTH), random.randrange(0, GRID_HEIGHT)): 1 for i in range(num)}

def draw_grid(positions, show_grid):
    for position, age in positions.items():
        col, row = position
        top_left = (col * TILE_SIZE, row * TILE_SIZE)
        color = get_color(age)
        pygame.draw.rect(screen, color, (*top_left, TILE_SIZE, TILE_SIZE))

    if show_grid:
        for row in range(GRID_HEIGHT):
            pygame.draw.line(screen, LINE_COLOR, (0, row * TILE_SIZE), (WIDTH, row * TILE_SIZE))

        for col in range(GRID_WIDTH):
            pygame.draw.line(screen, LINE_COLOR, (col * TILE_SIZE, 0), (col * TILE_SIZE, HEIGHT))  

def adjust_grid(positions):

    # Stores all neighbors of all live cells of the current set of positions
    all_neighbors = set()
    # Updated after adjust_grid
    new_positions = {}

    # Going through live cells
    for position, age in positions.items(): 
        # Get neighboring coordinates
        neighbors = get_neighbors(position)
        # Update neighbors for later use
        all_neighbors.update(neighbors)

        # Filter only for live cells
        live_neighbors = list(filter(lambda x: x in positions, neighbors))

        # If live cell amount is 2 or 3, (or experimental value) keep cell position
        if len(live_neighbors) in [2, 3]: # Experimental Parameter
            new_positions[position] = age + 1

    # Loop through all neighbors of live cells
    for position in all_neighbors:
        neighbors = get_neighbors(position)
        # Check live neighbors of live neighbors
        live_neighbors = list(filter(lambda x: x in positions, neighbors))

        # If they have three live neighbors, alive the adjacent cell
        if len(live_neighbors) == 3 and position not in new_positions:
            new_positions[position] = 1

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
    show_grid = True
    count = 0
    update_freq = 1 # Experimental Parameter
    randomness = random.randrange(100, 200) # Experimental Parameter
    positions = {}

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
                    del positions[pos]
                else:
                    positions[pos] = 1

            if event.type == pygame.KEYDOWN:
                # Press space to pause/play
                if event.key == pygame.K_SPACE:
                    playing = not playing
                
                # Press c to clear board
                if event.key == pygame.K_c:
                    positions = {}
                    playing = False
                    count = 0

                # Press g to generate cells
                if event.key == pygame.K_g:
                    positions = generate(randomness * GRID_WIDTH)

                # Press h to toggle grid on/off
                if event.key == pygame.K_h:
                    show_grid = not show_grid


        screen.fill(BG_COLOR)
        draw_grid(positions, show_grid)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()