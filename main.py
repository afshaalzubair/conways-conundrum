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
    WIDTH, HEIGHT = 1000, 1000
    TILE_SIZE = 2
    FPS = 60 
    UPDATE_FREQ = 1
    MAX_AGE = 10
    SURVIVAL_CELL_AMOUNT = [4,5,6,7,8]
    REPRODUCTION_CELL_AMOUNT = [3, 4]
    AGE_DEATH = True
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
    AGE_DEATH = DEF_PARAMS["AGE_DEATH"]
    ##### ##### ##### ##### ##### #####

# CONTROL PARAMETERS
LINE_COLOR = tuple(COLORS["LINE_COLOR"])
BG_COLOR = tuple(COLORS["BLACK"])
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE
TOTAL_CELLS = GRID_WIDTH * GRID_HEIGHT
GENERATION_RANDOMNESS = random.randrange(int(TOTAL_CELLS * 0.2), int(TOTAL_CELLS * 0.3))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def get_color(age):
    rainbow = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))

    young_color = tuple(COLORS["BLACK"])
    old_color = tuple(COLORS["CHOCOLATE"])

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

        # Skip cells that have reached max age, (they die)
        if (AGE_DEATH and age >= MAX_AGE):
            continue

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
    total_age = sum(min(age, MAX_AGE) for age in positions.values())
    average_age = total_age / num_live_cells if num_live_cells > 0 else 0
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

    # Title Box
    tbox_x = 60
    tbox_y = 10
    tbox_width = (WIDTH * 0.15)
    tbox_height = (HEIGHT * 0.04)
    tbox_position = (tbox_x, tbox_y, tbox_width, tbox_height)
    pygame.draw.rect(screen, tuple(COLORS["LAVENDER"]), tbox_position)

    # Title Border
    tborder_thickness = 5
    tborder_position = (
        tbox_x - tborder_thickness,
        tbox_y - tborder_thickness,
        tbox_width + tborder_thickness,
        tbox_height + tborder_thickness
    )
    pygame.draw.rect(screen, tuple(COLORS["REBECCAPURPLE"]), tborder_position, tborder_thickness)

    # Title Text
    font_size = 25
    font = pygame.font.Font("fonts/Minecraft.ttf", font_size)
    title = font.render("Statistics", True, tuple(COLORS["BLACK"]))
    screen.blit(title, (tbox_x + 17, tbox_y + 10))

    # Stats Box
    box_x = 15
    box_y = 65
    box_width = (WIDTH * 0.25)
    box_height = (HEIGHT * 0.12)
    box_position = (box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, tuple(COLORS["LAVENDER"]), box_position)

    # Stats Border
    border_thickness = 10
    border_position = (
        box_x - border_thickness,
        box_y - border_thickness,
        box_width + border_thickness,
        box_height + border_thickness
    )
    pygame.draw.rect(screen, tuple(COLORS["REBECCAPURPLE"]), border_position, border_thickness)

    # Stats Text
    font_size = 14
    font = pygame.font.Font("fonts/Minecraft.ttf", font_size)
    x_offset = box_x + 10
    y_offset = box_y + 10
    for name, value in statistics.items():
        text = font.render(f"{name}: {value}", True, tuple(COLORS["BLACK"]))
        screen.blit(text, (x_offset, y_offset))
        y_offset += 20

def draw_controls():
    controls = {
        "Toggle Controls:": "       T",
        "Pause/Play:": "         Space",
        "Generate:": "                G",
        "Clear Board:": "            C",
        "Toggle Grid:": "             H",
        "Toggle Stats:": "            S",
        "Toggle Intro:": "            E"
    }

    # Title Box
    tbox_x = (WIDTH / 3 + 80)
    tbox_y = (HEIGHT / 3 - 70)
    tbox_width = (WIDTH * 0.166)
    tbox_height = (HEIGHT * 0.05)
    tbox_position = (tbox_x, tbox_y, tbox_width, tbox_height)
    pygame.draw.rect(screen, tuple(COLORS["LAVENDER"]), tbox_position)

    # Title Border
    tborder_thickness = 5
    tborder_position = (
        tbox_x - tborder_thickness,
        tbox_y - tborder_thickness,
        tbox_width + tborder_thickness,
        tbox_height + tborder_thickness
    )
    pygame.draw.rect(screen, tuple(COLORS["REBECCAPURPLE"]), tborder_position, tborder_thickness)

    # Title Text
    font_size = 30
    font = pygame.font.Font("fonts/Minecraft.ttf", font_size)
    title = font.render("Controls", True, tuple(COLORS["BLACK"]))
    screen.blit(title, (tbox_x + 20, tbox_y + 10))

    # Main Box
    box_x = (WIDTH / 3)
    box_y = (HEIGHT / 3)
    box_width = (WIDTH * 0.33)
    box_height = (HEIGHT * 0.23)
    box_position = (box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, tuple(COLORS["LAVENDER"]), box_position)

    # Main Border
    border_thickness = 10
    border_position = (
        box_x - border_thickness,
        box_y - border_thickness,
        box_width + border_thickness,
        box_height + border_thickness
    )
    pygame.draw.rect(screen, tuple(COLORS["REBECCAPURPLE"]), border_position, border_thickness)
    
    # Main Text
    font_size = 25
    font = pygame.font.Font("fonts/Minecraft.ttf", font_size)
    x_offset = box_x + 10
    y_offset = box_y + 10
    for control, value in controls.items():
        text = font.render(f"{control} {value}", True, tuple(COLORS["BLACK"]))
        screen.blit(text, (x_offset, y_offset))
        y_offset += 30

def draw_introduction():
    # Title Box
    tbox_x = (WIDTH / 4)
    tbox_y = (HEIGHT / 4)
    tbox_width = (WIDTH * 0.5)
    tbox_height = (HEIGHT * 0.2)
    tbox_position = (tbox_x, tbox_y, tbox_width, tbox_height)
    pygame.draw.rect(screen, tuple(COLORS["LAVENDER"]), tbox_position)

    # Title Border
    tborder_thickness = 10
    tborder_position = (
        tbox_x - tborder_thickness,
        tbox_y - tborder_thickness,
        tbox_width + tborder_thickness,
        tbox_height + tborder_thickness
    )
    pygame.draw.rect(screen, tuple(COLORS["REBECCAPURPLE"]), tborder_position, tborder_thickness)

    # Title Text
    text = (
        "           Welcome to:", 
        "Conway's Conundrum!", 
        "                     A twist on the famous", 
        " Conway's Game of Life",
        "E to Close, T for Controls"
    )

    x_offset = tbox_x + 65
    y_offset = tbox_y + 35

    for i, item in enumerate(text):
        color = tuple(COLORS["VIOLET"]) if i == 1 else tuple(COLORS["BLACK"])   

        if (i == 1):
            font_size = 35
        elif (i == 2):
            font_size = 15
        elif (i == 4):
            font_size = 10
            x_offset -= 55
        else:
            font_size = 30
            y_offset -= 10

        font = pygame.font.Font("fonts/Minecraft.ttf", font_size)
        print = font.render(f"{item}", True, color)
        screen.blit(print, (x_offset, y_offset))
        y_offset += 40
    

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

        pygame.display.set_caption("Conway's Game of Life - Playing" if playing else "Conways Game of Life - Paused")

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
                    positions = generate(GENERATION_RANDOMNESS)
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