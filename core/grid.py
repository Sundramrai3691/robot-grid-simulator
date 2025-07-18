"""
Grid creation and management functions
"""

import pygame
from .spot import Spot
from config.constants import *

def make_grid(rows, width):
    """Create a grid of spots"""
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def draw_grid(win, rows, width):
    """Draw grid lines"""
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def get_clicked_pos(pos, rows, width):
    """Get grid position from mouse click"""
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col