import pygame
import math
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the window
window_width, window_height = 800, 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Rotating Cube with Rainbow Animation")

# Define the cube vertices
cube_size = 200
vertices = np.array([
    [-cube_size/2, -cube_size/2, -cube_size/2],
    [-cube_size/2, -cube_size/2, cube_size/2],
    [-cube_size/2, cube_size/2, -cube_size/2],
    [-cube_size/2, cube_size/2, cube_size/2],
    [cube_size/2, -cube_size/2, -cube_size/2],
    [cube_size/2, -cube_size/2, cube_size/2],
    [cube_size/2, cube_size/2, -cube_size/2],
    [cube_size/2, cube_size/2, cube_size/2]
])

# Define the cube faces
faces = [
    [0, 1, 3, 2],
    [2, 3, 7, 6],
    [6, 7, 5, 4],
    [4, 5, 1, 0],
    [1, 5, 7, 3],
    [4, 0, 2, 6]
]

# Set up the projection matrix
fov = 60
aspect_ratio = window_width / window_height
near_plane = 0.1
far_plane = 1000.0
projection_matrix = np.array([
    [1 / (aspect_ratio * math.tan(math.radians(fov / 2))), 0, 0, 0],
    [0, 1 / math.tan(math.radians(fov / 2)), 0, 0],
    [0, 0, -(far_plane + near_plane) / (far_plane - near_plane), -1],
    [0, 0, -(2 * far_plane * near_plane) / (far_plane - near_plane), 0]
])

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    window.fill((0, 0, 0))

    # Rotate the cube
    t = pygame.time.get_ticks() * 0.001
    rotation_x = (math.sin(t * 5) + 2) * math.pi / 180
    rotation_y = (math.sin(t * 5) + 2) * math.pi / 180
    rotation_z = (math.sin(t * 5) + 2) * math.pi / 180

    # Create the rotation matrices
    rotation_matrix_x = np.array([
        [1, 0, 0],
        [0, math.cos(rotation_x), -math.sin(rotation_x)],
        [0, math.sin(rotation_x), math.cos(rotation_x)]
    ])

    rotation_matrix_y = np.array([
        [math.cos(rotation_y), 0, math.sin(rotation_y)],
        [0, 1, 0],
        [-math.sin(rotation_y), 0, math.cos(rotation_y)]
    ])

    rotation_matrix_z = np.array([
        [math.cos(rotation_z), -math.sin(rotation_z), 0],
        [math.sin(rotation_z), math.cos(rotation_z), 0],
        [0, 0, 1]
    ])

    # Apply the rotation to the cube vertices
    rotated_vertices = np.dot(vertices, rotation_matrix_x)
    rotated_vertices = np.dot(rotated_vertices, rotation_matrix_y)
    rotated_vertices = np.dot(rotated_vertices, rotation_matrix_z)

    # Project the 3D vertices to 2D
    projected_vertices = np.dot(rotated_vertices, projection_matrix.T)
    projected_vertices[:, 0] += window_width / 2
    projected_vertices[:, 1] += window_height / 2

    # Draw the cube faces with rainbow colors
    for i, face in enumerate(faces):
        vertices_2d = projected_vertices[face]
        color = tuple(int(255 * ((math.sin(t * 5 + i / 6 * 2 * math.pi) + 1) / 2)) for _ in range(3))
        pygame.draw.polygon(window, color, vertices_2d)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()