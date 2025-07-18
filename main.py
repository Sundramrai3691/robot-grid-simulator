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
    start = None
    targets = []
    robot = None
    run = True
    clock = pygame.time.Clock()
    sim_running = False
    
    # Enhanced control variables
    target_mode = False
    target_priority = 1
    robot_params = {
        'battery': DEFAULT_BATTERY,
        'sensor_range': DEFAULT_SENSOR_RANGE,
        'speed': DEFAULT_ROBOT_SPEED,
        'drain_rate': BATTERY_DRAIN_RATE
    }

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
                if not robot.step():
                    if robot.battery <= 0:
                        print("Robot battery depleted!")
                        sim_running = False
            else:
                print("All targets reached!")
                sim_running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                from core.grid import get_clicked_pos
                pos = pygame.mouse.get_pos()
                if pos[0] < width:  # Only process clicks on the grid area
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        spot = grid[row][col]
                        
                        if target_mode:
                            # Set target with current priority
                            if not spot.is_start() and not spot.is_barrier():
                                spot.make_target(target_priority)
                                targets.append(spot)
                        elif traffic_light_tool:
                            spot.make_traffic_light()
                        elif not start and not spot.is_barrier():
                            start = spot
                            start.make_start()
                        elif spot != start:
                            spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                from core.grid import get_clicked_pos
                pos = pygame.mouse.get_pos()
                if pos[0] < width:  # Only process clicks on the grid area
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        spot = grid[row][col]
                        if spot == start:
                            start = None
                        elif spot in targets:
                            targets.remove(spot)
                        spot.reset()
                        spot.is_traffic_stop = False
                        spot.is_target = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and targets:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    robot = Robot(start, targets, grid,
                                  lambda: draw(win, grid, ROWS, width, robot.trails, robot.get_center(), robot),
                                  **robot_params)
                    robot.plan_path()
                    sim_running = True
                    
                elif event.key == pygame.K_c:
                    grid = make_grid(ROWS, width)
                    start = None
                    targets = []
                    robot = None
                    sim_running = False
                    
                elif event.key == pygame.K_r:  # Reset simulation
                    if robot:
                        robot.current = start
                        robot.trails = []
                        robot.index = 0
                        robot.completed_targets = []
                        robot.current_target = None
                        robot.battery = robot.max_battery
                        robot.plan_path()
                        sim_running = True
                    
                elif event.key == pygame.K_o:  # Save obstacles
                    save_obstacles(grid)
                    
                elif event.key == pygame.K_p:  # Load obstacles
                    load_obstacles(grid)
                    
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    speed_index = event.key - pygame.K_1
                    sim_speed = SPEED_MULTIPLIERS[speed_index]
                    robot_params['speed'] = sim_speed
                    if robot:
                        robot.speed_multiplier = sim_speed

                elif event.key == pygame.K_t:  # Toggle traffic light tool
                    traffic_light_tool = not traffic_light_tool
                    target_mode = False

                elif event.key == pygame.K_m:  # Toggle target mode
                    target_mode = not target_mode
                    traffic_light_tool = False

                elif event.key == pygame.K_s:  # Save current map layout
                    map_name = get_text_input("Enter a name for this map:", "Save Map")
                    if map_name:
                        save_map(grid, start, targets, map_name)

                elif event.key == pygame.K_l:  # Load a named map
                    map_name = get_text_input("Enter the name of the map to load:", "Load Map")
                    if map_name:
                        result = load_map(grid, map_name)
                        if result:
                            grid, start, loaded_targets = result
                            targets = loaded_targets

                # Priority selection in target mode
                elif target_mode and event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    target_priority = event.key - pygame.K_0

                # Parameter adjustments
                elif event.key == pygame.K_b:  # Increase battery
                    robot_params['battery'] = min(200, robot_params['battery'] + 10)
                    if robot:
                        robot.max_battery = robot_params['battery']

                elif event.key == pygame.K_v:  # Decrease battery
                    robot_params['battery'] = max(50, robot_params['battery'] - 10)
                    if robot:
                        robot.max_battery = robot_params['battery']

                elif event.key == pygame.K_n:  # Increase sensor range
                    robot_params['sensor_range'] = min(10, robot_params['sensor_range'] + 1)
                    if robot:
                        robot.sensor_range = robot_params['sensor_range']

                elif event.key == pygame.K_j:  # Decrease sensor range
                    robot_params['sensor_range'] = max(1, robot_params['sensor_range'] - 1)
                    if robot:
                        robot.sensor_range = robot_params['sensor_range']

                elif event.key == pygame.K_q:  # Quit
                    run = False

    pygame.quit()

if __name__ == '__main__':
    # Initialize pygame
    pygame.init()
    
    # Create window
    WIN = pygame.display.set_mode((WIDTH + SIDEBAR_WIDTH, WIDTH))
    pygame.display.set_caption("A* Navigation Simulator - Ultimate Edition")
    
    # Initialize global variables
    sim_speed = DEFAULT_SPEED
    traffic_light_tool = False
    
    # Start main loop
    main(WIN, WIDTH)