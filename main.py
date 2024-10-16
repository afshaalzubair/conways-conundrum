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

with open("data/colors.json", "r") as color_file, open("data/defaultparameters.json", "r") as param_file:
    COLORS = json.load(color_file)
    DEF_PARAMS = json.load(param_file)

use_default_parameters = False

if not (use_default_parameters):
    ##### EXPERIMENTAL PARAMETERS #####
    WIDTH, HEIGHT = 1002, 1002
    TILE_SIZE = 3
    FPS = 60 
    UPDATE_FREQ = 1
    MAX_AGE = 3
    SURVIVAL_CELL_AMOUNT = [2, 3, 4]
    REPRODUCTION_CELL_AMOUNT = [3]
    ##### ##### ##### ##### ##### #####
else:
    #####    DEFAULT PARAMETERS   #####
    WIDTH = DEF_PARAMS["WIDTH"]
    HEIGHT = DEF_PARAMS["HEIGHT"]
    TILE_SIZE = DEF_PARAMS["TILE_SIZE"]
    FPS = DEF_PARAMS["FPS"]
    UPDATE_FREQ = DEF_PARAMS["UPDATE_FREQ"]
    MAX_AGE = DEF_PARAMS["MAX_AGE"]
    SURVIVAL_CELL_AMOUNT = tuple(DEF_PARAMS["SURVIVAL_CELL_AMOUNT"])
    REPRODUCTION_CELL_AMOUNT = tuple(DEF_PARAMS["REPRODUCTION_CELL_AMOUNT"])
    ##### ##### ##### ##### ##### #####

# CONTROL PARAMETERS
LINE_COLOR = tuple(COLORS["LINE_COLOR"])
BG_COLOR = tuple(COLORS["BLACK"])
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE
GENERATION_RANDOMNESS = random.randrange(int((0.1 * ((WIDTH + HEIGHT) / 2))), int((0.2 * ((WIDTH + HEIGHT) / 2))))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def get_color(age):
    rainbow = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))

    young_color = tuple(COLORS["BLACK"])
    old_color = tuple(COLORS["WHITE"])

    age = min(age, MAX_AGE)

    ratio = age / MAX_AGE
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
    # Stores positions of all neighbors of all live cells of the current cycle of positions
    all_neighbors = set()
    # Updated after adjust_grid, stores positions and age of the cells that need to be updated after cycle
    new_positions = {}

    # Loop through the position and age of all live cells
    for position, age in positions.items(): 
        # Get neighboring coordinates
        neighbors = get_neighbors(position)
        # Add set of coordinates to all_neighbors
        all_neighbors.update(neighbors)

        # Filter only for live cells
        live_neighbors = list(filter(lambda x: x in positions, neighbors))

        # If live cell amount is 2 or 3, (or experimental value) keep cell position; determined by the length (num) of coordinates in live_neighbors
        if len(live_neighbors) in SURVIVAL_CELL_AMOUNT: 
            new_positions[position] = age + 1

    # Loop through all neighbors of live cells
    for position in all_neighbors:
        neighbors = get_neighbors(position)
        # Check live neighbors of live neighbors
        live_neighbors = list(filter(lambda x: x in positions, neighbors))

        # If they have three live neighbors (or experimental number of neighbors), alive the adjacent cell
        if len(live_neighbors) in REPRODUCTION_CELL_AMOUNT and position not in new_positions:
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

def calculate_statistics(positions, generation_count, previous_live_cell_count):
    num_live_cells = len(positions)
    population_density = num_live_cells / (GRID_WIDTH * GRID_HEIGHT)
    average_age = sum(positions.values()) / num_live_cells if num_live_cells > 0 else 0
    survival_rate = (num_live_cells / previous_live_cell_count) * 100 if previous_live_cell_count > 0 else 0

    statistics = {
        "Generation": generation_count,
        "Live Cells": num_live_cells,
        "Population Density": f"{population_density:.2%}",
        "Average Age": f"{average_age:.2f} Gens",
        "Survival Rate": f"{survival_rate:.2f}%"
    }

    return statistics

def draw_statistics(statistics):
    box_position = (15, 15, (WIDTH * 0.25), (HEIGHT * 0.12))
    pygame.draw.rect(screen, tuple(COLORS["LAVENDER"]), box_position)
    border_thickness = 10
    border_position = (5, 5, (WIDTH * 0.25 + border_thickness), (WIDTH * 0.12 + border_thickness))
    pygame.draw.rect(screen, tuple(COLORS["REBECCAPURPLE"]), border_position, border_thickness)
    font = pygame.font.Font("fonts/Minecraft.ttf", 14)
    y_offset = 25
    for name, value in statistics.items():
        text = font.render(f"{name}: {value}", True, tuple(COLORS["BLACK"]))
        screen.blit(text, (25, y_offset))
        y_offset += 20

def draw_controls():
    controls = {
        "Toggle Controls:": "       T",
        "Pause/Play:": "         Space",
        "Generate:": "                G",
        "Clear Board:": "            C",
        "Toggle Grid:": "             H",
        "Toggle Stats:": "            S"
        # add toggle intro menu
    }

    font = pygame.font.Font("fonts/Minecraft.ttf", 25)
    # Title Box
    tbox_position = ()
    pygame.draw.rect(screen, tuple(COLORS["LAVENDER"]), tbox_position)
    tborder_thickness = 5
    tborder_position = ()
    pygame.draw.rect(screen, tuple(COLORS["REBECCAPURPLE"]), tborder_position, tborder_thickness)
    title = font.render("Controls", True, tuple(COLORS["BLACK"]))
    screen.blit(title, ())

    # Main Box
    box_position = (WIDTH / 3, HEIGHT / 3, (WIDTH * 0.33), (HEIGHT * 0.2))
    pygame.draw.rect(screen, tuple(COLORS["LAVENDER"]), box_position)
    border_thickness = 10
    border_position = (WIDTH / 3 - border_thickness, HEIGHT / 3 - border_thickness, (WIDTH * 0.33 + border_thickness), (WIDTH * 0.2 + border_thickness))
    pygame.draw.rect(screen, tuple(COLORS["REBECCAPURPLE"]), border_position, border_thickness)
    font = pygame.font.Font("fonts/Minecraft.ttf", 25)
    y_offset = HEIGHT / 3 + 10
    for control, value in controls.items():
        text = font.render(f"{control} {value}", True, tuple(COLORS["BLACK"]))
        screen.blit(text, (WIDTH / 3 + 10, y_offset))
        y_offset += 30

def draw_introduction():
    pass
    

def main():
    running = True
    playing = False
    show_grid = True
    show_stats = False
    show_controls = False
    show_intro = True
    count = 0
    positions = {}

    generation = 0
    previous_live_cell_count = 0

    while running:
        clock.tick(FPS)

        if playing:
            count += 1

        if count >= UPDATE_FREQ:
            count = 0
            previous_live_cell_count = len(positions)
            positions = adjust_grid(positions)
            generation += 1

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
                    generation = 0

                # Press g to generate cells
                if event.key == pygame.K_g:
                    positions = generate(GENERATION_RANDOMNESS * GRID_WIDTH)
                    generation = 0

                # Press h to toggle grid on/off
                if event.key == pygame.K_h:
                    show_grid = not show_grid

                # Press s to toggle game statistics panel
                if event.key == pygame.K_s:
                    show_stats = not show_stats

                # Press t to toggle controls menu
                if event.key == pygame.K_t:
                    show_controls = not show_controls

                # Press e to toggle intro menu
                if event.key == pygame.K_e:
                    show_intro = not show_intro
        
        screen.fill(BG_COLOR)
        draw_grid(positions, show_grid)

        if show_stats:
            statistics = calculate_statistics(positions, generation, previous_live_cell_count)
            draw_statistics(statistics)

        if show_controls:
            draw_controls()

        if show_intro:
            draw_introduction()

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()