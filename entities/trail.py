"""
Trail marker for robot path visualization
"""

import pygame
from config.constants import *

class TrailMarker:
    def __init__(self, pos, color, size):
        self.pos = pos
        self.color = color
        self.size = size
        self.lifetime = TRAIL_LENGTH
        self.max_lifetime = TRAIL_LENGTH
        
    def update(self):
        """Update trail marker (fade over time)"""
        self.lifetime -= 1
        # Fade the alpha based on remaining lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        self.color = (*self.color[:3], max(0, alpha))
        
    def draw(self, win):
        """Draw the trail marker"""
        if self.lifetime > 0:
            # Create a surface with alpha for transparency
            s = pygame.Surface((self.size // 4, self.size // 4), pygame.SRCALPHA)
            pygame.draw.circle(s, self.color, (self.size // 8, self.size // 8), self.size // 8)
            win.blit(s, (self.pos[0] - self.size // 8, self.pos[1] - self.size // 8))