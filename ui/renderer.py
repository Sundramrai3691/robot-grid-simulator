"""
Rendering and drawing functions
"""

import pygame
import math
from config.constants import *
from config.settings import *
from core.grid import draw_grid

def draw(win, grid, rows, width, trails=[], robot_pos=None, robot=None):
    """Main drawing function"""
    win.fill(WHITE)

    # Draw perception area first (if robot exists)
    if robot and robot.perception_area:
        for spot in robot.perception_area:
            # Draw semi-transparent overlay for perception area
            s = pygame.Surface((spot.width, spot.width), pygame.SRCALPHA)
            pygame.draw.rect(s, (*BLUE, 30), (0, 0, spot.width, spot.width))
            win.blit(s, (spot.x, spot.y))

    # Draw unknown areas (darker) for limited perception
    if robot and hasattr(robot, 'known_map'):
        for row in grid:
            for spot in row:
                if spot.get_pos() not in robot.known_map:
                    s = pygame.Surface((spot.width, spot.width), pygame.SRCALPHA)
                    pygame.draw.rect(s, (*BLACK, 80), (0, 0, spot.width, spot.width))
                    win.blit(s, (spot.x, spot.y))

    # Draw all cells
    for row in grid:
        for spot in row:
            spot.draw(win)

    # Draw trails behind everything
    for trail in trails:
        trail.draw(win)

    # Draw robot with direction indicator
    if robot_pos:
        pos_x, pos_y = robot_pos
        radius = grid[0][0].width // 3
        pygame.draw.circle(win, ORANGE, (pos_x, pos_y), radius)

        # Draw direction arrow
        if len(trails) > 1:
            prev_pos = trails[-2].pos
            angle = math.atan2(pos_y - prev_pos[1], pos_x - prev_pos[0])
            arrow_length = radius * 1.5
            end_x = pos_x + arrow_length * math.cos(angle)
            end_y = pos_y + arrow_length * math.sin(angle)
            pygame.draw.line(win, BLACK, (pos_x, pos_y), (end_x, end_y), 2)

    # Draw sensor range circle
    if robot and robot_pos:
        sensor_radius = robot.sensor_range * (width // rows)
        pygame.draw.circle(win, (*GREEN, 50), robot_pos, sensor_radius, 2)

    draw_grid(win, rows, width)
    draw_ui(win, robot)
    pygame.display.update()

def draw_ui(win, robot=None):
    """Draw the enhanced user interface sidebar"""
    pygame.draw.rect(win, SIDEBAR_BG, (WIDTH, 0, SIDEBAR_WIDTH, WIDTH))  # Right sidebar

    font_title = pygame.font.SysFont('Arial', 24, bold=True)
    font = pygame.font.SysFont('Arial', 16)
    font_small = pygame.font.SysFont('Arial', 14)

    # Title
    title = font_title.render("A* SIMULATOR", True, BLACK)
    win.blit(title, (WIDTH + 20, 20))

    instructions = [
        "Controls:",
        "• Left Click: Set Start/Target/Barrier",
        "• Hold T: Add Traffic Light",
        "• Hold M: Target Mode (1-3 Priority)",
        "• Right Click: Remove Cell",
        "• Space: Start Simulation",
        "• C: Clear Grid, R: Reset",
        "• O: Save Obstacles, P: Load Obstacles",
        "• S: Save Map, L: Load Map",
        "• 1-4: Speed (Current: {}x)".format(sim_speed),
        "• T: Toggle Traffic Tool",
        "• M: Toggle Target Mode"
    ]

    # Render controls section
    for i, text in enumerate(instructions):
        label = font_small.render(text, True, BLACK)
        win.blit(label, (WIDTH + 20, 60 + i * 22))

    # Robot parameters and status
    if robot:
        y_offset = 320
        
        # Battery indicator
        battery_percent = (robot.battery / robot.max_battery) * 100
        battery_color = GREEN if battery_percent > 50 else (YELLOW if battery_percent > 20 else RED)
        battery_text = font.render(f"Battery: {battery_percent:.1f}%", True, battery_color)
        win.blit(battery_text, (WIDTH + 20, y_offset))
        
        # Draw battery bar
        bar_width = 200
        bar_height = 10
        bar_x = WIDTH + 20
        bar_y = y_offset + 25
        pygame.draw.rect(win, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        fill_width = int(bar_width * (battery_percent / 100))
        pygame.draw.rect(win, battery_color, (bar_x + 2, bar_y + 2, fill_width - 4, bar_height - 4))
        
        # Performance metrics
        metrics = [
            f"Speed: {robot.speed_multiplier}x",
            f"Sensor Range: {robot.sensor_range}",
            f"Distance: {robot.distance_traveled}",
            f"Steps: {robot.steps_taken}",
            f"Replans: {robot.replan_count}",
            f"Targets: {len(robot.completed_targets)}/{len(robot.targets)}"
        ]
        
        for i, metric in enumerate(metrics):
            metric_text = font_small.render(metric, True, BLACK)
            win.blit(metric_text, (WIDTH + 20, y_offset + 50 + i * 20))

        # Path Length
        if robot.path:
            length_text = font.render(f"Path Length: {len(robot.path)}", True, DARK_GREEN)
            win.blit(length_text, (WIDTH + 20, y_offset + 170))

        # Current target info
        if robot.current_target:
            target_text = font.render(f"Target Priority: {robot.current_target.target_priority}", True, PURPLE)
            win.blit(target_text, (WIDTH + 20, y_offset + 195))

    # Legend
    legend_y = 650
    legend_title = font.render("Legend:", True, BLACK)
    win.blit(legend_title, (WIDTH + 20, legend_y))
    
    legend_items = [
        ("Start/Robot", ORANGE),
        ("High Priority", TARGET_HIGH),
        ("Medium Priority", TARGET_MEDIUM),
        ("Low Priority", TARGET_LOW),
        ("Barrier", BLACK),
        ("Path", PURPLE),
        ("Perception", BLUE)
    ]
    
    for i, (label, color) in enumerate(legend_items):
        y_pos = legend_y + 25 + i * 20
        pygame.draw.rect(win, color, (WIDTH + 20, y_pos, 15, 15))
        label_text = font_small.render(label, True, BLACK)
        win.blit(label_text, (WIDTH + 45, y_pos))