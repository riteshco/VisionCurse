def create_light_aura(radius):
    """
    Creates a square Surface with a radial gradient.
    The center is bright (255, 255, 255) and fades to black (0, 0, 0) at the radius.
    """
    surface = pygame.Surface((radius * 2, radius * 2))
    surface.fill(BLACK) # Start with black
    
    # Draw concentric circles, getting dimmer from center
    for r in range(radius, 0, -1):
        brightness = int(255 * (1.0 - (r / radius)))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (radius, radius), r)
        
    # Set black to be transparent (colorkey)
    surface.set_colorkey(BLACK)
    return surface