#!/usr/bin/env python3
"""
A* Navigation Simulator - Ultimate Edition
Main entry point for the application
"""

import pygame
import os
from config.settings import *
from config.constants import *
from core.grid import make_grid
from core.robot import Robot
from ui.renderer import draw
from ui.input_handler import get_text_input
from utils.file_manager import save_map, load_map, save_obstacles, load_obstacles

def main(win, width):
    global sim_speed, traffic_light_tool
    
    # Create maps directory if it doesn't exist
    if not os.path.exists("maps"):
        os.makedirs("maps")
    
    pygame.font.init()
    grid = make_grid(ROWS, width)
    start = end = robot = None
    run = True
    clock = pygame.time.Clock()
    sim_running = False

    while run:
        clock.tick(30)

        # Update traffic lights
        for row in grid:
            for spot in row:
                if spot.is_traffic_stop:
                    spot.update_traffic_light()

        draw(win, grid, ROWS, width,
             robot.trails if robot else [],
             robot.get_center() if robot else None, robot)

        if sim_running and robot:
            if not robot.reached_goal():
                robot.step()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                from core.grid import get_clicked_pos
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                if 0 <= row < ROWS and 0 <= col < ROWS:
                    spot = grid[row][col]
                    if not start and spot != end:
                        start = spot
                        start.make_start()
                    elif not end and spot != start:
                        end = spot
                        end.make_end()
                    elif traffic_light_tool:
                        spot.make_traffic_light()
                    elif spot != start and spot != end:
                        spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                from core.grid import get_clicked_pos
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                if 0 <= row < ROWS and 0 <= col < ROWS:
                    spot = grid[row][col]
                    if spot == start:
                        start = None
                    elif spot == end:
                        end = None
                    spot.reset()
                    spot.is_traffic_stop = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    robot = Robot(start, end, grid,
                                  lambda: draw(win, grid, ROWS, width, robot.trails, robot.get_center(), robot))
                    robot.plan_path()
                    sim_running = True
                    
                if event.key == pygame.K_c:
                    grid = make_grid(ROWS, width)
                    start = end = robot = None
                    sim_running = False
                    
                if event.key == pygame.K_r:  # Reset simulation
                    grid = make_grid(ROWS, width)
                    start = end = robot = None
                    sim_running = False
                    
                if event.key == pygame.K_o:  # Save obstacles
                    save_obstacles(grid)
                    
                if event.key == pygame.K_p:  # Load obstacles
                    load_obstacles(grid)
                    
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    sim_speed = [0.1, 0.3, 0.5, 1.0][event.key - pygame.K_1]

                if event.key == pygame.K_t:  # Toggle traffic light tool
                    traffic_light_tool = not traffic_light_tool

                if event.key == pygame.K_s:  # Save current map layout
                    map_name = get_text_input("Enter a name for this map:", "Save Map")
                    if map_name:
                        save_map(grid, start, end, map_name)

                if event.key == pygame.K_l:  # Load a named map
                    map_name = get_text_input("Enter the name of the map to load:", "Load Map")
                    if map_name:
                        result = load_map(grid, map_name)
                        if result:
                            grid, start, end = result

    pygame.quit()

if __name__ == '__main__':
    # Initialize pygame and create window
    pygame.init()
    WIN = pygame.display.set_mode((WINDOW_WIDTH, WIDTH))
    pygame.display.set_caption("A* Navigation Simulator - Ultimate Edition")
    
    main(WIN, WIDTH)