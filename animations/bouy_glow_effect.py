import pygame

def bouy_glow_effect(surface, x, y, width, height, alpha=255, blink_direction=-5):
    """
    Creates a glowing effect for the buoy.
    
    :param surface: The surface to draw on.
    :param x: The x-coordinate of the buoy.
    :param y: The y-coordinate of the buoy.
    :param width: The width of the buoy.
    :param height: The height of the buoy.
    :param alpha: The initial alpha value (brightness).
    :param blink_direction: The direction to change the alpha value (-1 for fade out, 1 for fade in).
    """
    # Create a new surface with an alpha channel
    glow_surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
    
    # Draw a circle with a gradient effect
    for i in range(0, 256, 5):
        color = (255, 255, 0, int(alpha * (i / 255)))  # Yellow color with varying alpha
        pygame.draw.circle(glow_surface, color, (width // 2, height // 2), i // 2)
    
    # Blit the glow surface onto the main surface
    surface.blit(glow_surface, (x - width // 2, y - height // 2))
    
    # Update the alpha value for the next frame
    alpha += blink_direction
    if alpha <= 0 or alpha >= 255:
        blink_direction *= -1
    
    return alpha, blink_direction