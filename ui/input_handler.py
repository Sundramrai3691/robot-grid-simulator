"""
Input handling utilities
"""

import pygame
import sys

def get_text_input(prompt, title="Input"):
    """Get text input from user using a simple input dialog"""
    pygame.init()
    
    # Create a simple input window
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption(title)
    
    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    
    input_text = ""
    input_active = True
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                input_active = False
                input_text = ""
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_ESCAPE:
                    input_active = False
                    input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
        
        # Draw the input dialog
        screen.fill((240, 240, 240))
        
        # Draw prompt
        prompt_surface = font.render(prompt, True, (0, 0, 0))
        screen.blit(prompt_surface, (20, 30))
        
        # Draw input box
        input_box = pygame.Rect(20, 80, 360, 32)
        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, (0, 0, 0), input_box, 2)
        
        # Draw input text
        text_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        
        # Draw instructions
        instr_surface = font.render("Press Enter to confirm, Escape to cancel", True, (100, 100, 100))
        screen.blit(instr_surface, (20, 140))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.display.quit()
    return input_text.strip() if input_text else None