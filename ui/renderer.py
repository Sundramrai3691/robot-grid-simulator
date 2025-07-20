"""
Rendering and drawing functions
"""

import pygame
import math
from config.constants import *
from config.settings import *
from core.grid import draw_grid

def draw(win, grid, rows, width, trails, robot_center, robot, barrier_mode=False):
    win.fill(WHITE)

    # Draw grid spots
    for row in grid:
        for spot in row:
            spot.draw(win)
            if hasattr(spot, 'priority') and spot.priority:
                font = pygame.font.SysFont('Arial', 16, bold=True)
                text = font.render(str(spot.priority), True, BLACK)
                text_rect = text.get_rect(center=(spot.x + spot.width // 2, spot.y + spot.width // 2))
                win.blit(text, text_rect)



    # Draw trail path
    for trail in trails:
        pygame.draw.circle(win, PURPLE, trail.get_center(), 3)



    # Draw robot and direction
    # Draw robot and direction with a green ring around it
    # Draw robot and direction with a larger green ring
    # Draw robot and direction with a much larger green ring
    if robot_center:
        pos_x, pos_y = robot_center
        radius = grid[0][0].width // 3

        # Make the green ring significantly larger
        outer_radius = radius + 20   # Increased from +10 to +20
        ring_thickness = 6           # Thicker ring for visibility
        pygame.draw.circle(win, (0, 255, 0), (pos_x, pos_y), outer_radius, ring_thickness)

        # Draw robot body
        pygame.draw.circle(win, ORANGE, (pos_x, pos_y), radius)

        # Draw direction arrow
        if len(trails) > 1:
            prev_pos = trails[-2].get_center()
            angle = math.atan2(pos_y - prev_pos[1], pos_x - prev_pos[0])
            arrow_length = radius * 1.5
            end_x = pos_x + arrow_length * math.cos(angle)
            end_y = pos_y + arrow_length * math.sin(angle)
            pygame.draw.line(win, BLACK, (pos_x, pos_y), (end_x, end_y), 2)



    # Draw grid lines and UI
    draw_grid(win, rows, width)
    draw_ui(win, robot)

    pygame.display.update()


def draw_ui(win, robot=None):
    """Draw the user interface sidebar"""
    pygame.draw.rect(win, SIDEBAR_BG, (WIDTH, 0, SIDEBAR_WIDTH, WIDTH))  # Right sidebar

    font_title = pygame.font.SysFont('Arial', 24, bold=True)
    font = pygame.font.SysFont('Arial', 18)

    # Title
    title = font_title.render("A* SIMULATOR", True, BLACK)
    win.blit(title, (WIDTH + 20, 20))

    instructions = [
        "Controls:",
        "• Left Click: Set Start/Target",
        "• B: Add Barriers (Toggle)",
        "• Hold T: Add Traffic Light",
        "• Right Click: Remove Cell",
        "• Space: Start Simulation",
        "• C: Clear Grid, R: Reset",
        "• O: Save Obstacles, P: Load Obstacles",
        "• S: Save Map, L: Load Map",
        "• 1-4: Speed (Current: {}x)".format(sim_speed)
    ]

    for i, text in enumerate(instructions):
        label = font.render(text, True, BLACK)
        win.blit(label, (WIDTH + 20, 70 + i * 30))
    

import pygame

import pygame

def show_startup_popup(win):
    popup_width, popup_height = 700, 400
    win_width, win_height = win.get_size()
    popup_x = (win_width - popup_width) // 2
    popup_y = (win_height - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

    font = pygame.font.SysFont("arial", 20, bold=False)
    title_font = pygame.font.SysFont("arial", 26, bold=True)

    lines = [
        "This simulator demonstrates the A* pathfinding algorithm, widely used in AI",
        "for navigating intelligent agents. You place obstacles,simulate smart traffic, ",
        "and watch the robot compute the optimal path in real-time.",
        "",
        "Left Click to place the Start and End nodes",
        "Press 'B' to toggle Barrier placement mode",
        "Press 'T' to add Smart Traffic Lights",
        "Press 'R' to Reset the grid",
        "Press 'S' to Save your current map",
        "Press 'L' to Load a previously saved map",
        "",
        "Press any key or click to begin!"
    ]

    # Draw background popup
    pygame.draw.rect(win, (240, 240, 240), popup_rect)
    pygame.draw.rect(win, (0, 0, 0), popup_rect, 2)

    # Draw title
    title = title_font.render("Welcome to A* Pathfinding Simulator", True, (0, 0, 0))
    win.blit(title, (popup_x + 20, popup_y + 20))

    # Draw each instruction line
    y_offset = popup_y + 70
    for line in lines:
        rendered_line = font.render(line, True, (0, 0, 0))
        win.blit(rendered_line, (popup_x + 20, y_offset))
        y_offset += 30

    pygame.display.update()

    # Wait for user interaction
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False


