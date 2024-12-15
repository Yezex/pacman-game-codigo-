import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800

#Initializing musics, ba dum ts
pygame.mixer.music.load("pacman_beginning.wav")  # Ensure you have an mp3 file for background music
pygame.mixer.music.set_volume(0.1)  # Set volume level
pygame.mixer.music.play(-1, 0.0)  # Play the music looped

# Load sound effects (make sure you have sound files like these)
pellet_sound = pygame.mixer.Sound("pacman_chomp.wav")  # When collecting pellets
ghost_collision_sound = pygame.mixer.Sound("pacman_death.wav")  # When Pac-Man touches a ghost

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Cell size for grid
CELL_SIZE = 40


FPS = 30
PACMAN_SPEED = 4  # Number of pixels Pacman moves per frame
GHOST_SPEED = 3    # Slightly increased speed for ghosts
def resource_path(relative_path):
    """Obtén la ruta absoluta a un recurso empaquetado con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Cuando el programa se ejecuta desde un ejecutable, usa _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(""), relative_path)
# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman EDO")

# Fonts
font = pygame.font.Font(None, 36)

# Load images (replace with your PNG paths)
pacman_image = pygame.image.load(resource_path("Pacman.png"))  # Add the correct path to your Pacman PNG
pacman_image = pygame.transform.scale(pacman_image, (CELL_SIZE, CELL_SIZE))

ghost_image = pygame.image.load(resource_path("fantasma.png"))  # Add the correct path to your Ghost PNG
ghost_image = pygame.transform.scale(ghost_image, (CELL_SIZE, CELL_SIZE))

# Game objects
class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0

    def move(self, walls):
        # Predict next position
        next_x = self.x + self.dx
        next_y = self.y + self.dy

        # Define Pac-Man's bounding box
        pacman_box = pygame.Rect(next_x, next_y, CELL_SIZE, CELL_SIZE)

        # Check collision with walls
        collision = False
        for wall in walls:
            wall_box = pygame.Rect(wall[0], wall[1], CELL_SIZE, CELL_SIZE)
            if pacman_box.colliderect(wall_box):
                collision = True
                break

        # Apply movement only if no collision
        if not collision:
            self.x = next_x
            self.y = next_y
        else:
            self.dx = 0
            self.dy = 0

    def draw(self):
        screen.blit(pacman_image, (self.x, self.y))

class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_move = (0, 0)  # Last successful move direction
        self.mode = "random"  # Start in random mode
        self.mode_timer = random.randint(90, 150)  # Timer for mode switching
        self.stuck_timer = 0  # Track how long a ghost has been stuck

    def move(self, target_x, target_y, walls):
        # Mode timer logic
        if self.mode_timer <= 0:
            self.mode = "target" if self.mode == "random" else "random"
            self.mode_timer = random.randint(90, 150)  # Reset mode timer
        else:
            self.mode_timer -= 1

        # Define possible directions (up, down, left, right)
        directions = [
            (0, -GHOST_SPEED),  # Up
            (0, GHOST_SPEED),   # Down
            (-GHOST_SPEED, 0),  # Left
            (GHOST_SPEED, 0)    # Right
        ]
        random.shuffle(directions)  # Add randomness to movement evaluation

        # Shrink wall boxes for smoother navigation
        wall_margin = 2
        valid_moves = []
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            new_box = pygame.Rect(new_x, new_y, CELL_SIZE, CELL_SIZE)

            # Check for collisions with walls
            collision = any(
                new_box.colliderect(
                    pygame.Rect(w[0] + wall_margin, w[1] + wall_margin, CELL_SIZE - 2 * wall_margin, CELL_SIZE - 2 * wall_margin)
                )
                for w in walls
            )

            if not collision:
                valid_moves.append((new_x, new_y, dx, dy))

        # Handle movement based on mode
        if valid_moves:
            self.stuck_timer = 0  # Reset stuck timer if movement is possible

            if self.mode == "random":
                # Continue in the same direction if possible
                preferred_move = None
                for move in valid_moves:
                    if (move[2], move[3]) == self.last_move:
                        preferred_move = move
                        break

                # Choose preferred or random move
                chosen_move = preferred_move or random.choice(valid_moves)
            else:
                # Move closer to target (Pac-Man)
                chosen_move = min(
                    valid_moves,
                    key=lambda move: abs(move[0] - target_x) + abs(move[1] - target_y)  # Manhattan distance
                )

            # Apply chosen move
            self.x, self.y = chosen_move[0], chosen_move[1]
            self.last_move = (chosen_move[2], chosen_move[3])
        else:
            # If stuck, increment timer and force movement after a threshold
            self.stuck_timer += 1
            if self.stuck_timer >= 10:  # If stuck for too long, move randomly
                random_direction = random.choice(directions)
                self.x += random_direction[0]
                self.y += random_direction[1]
                self.stuck_timer = 0  # Reset stuck timer

    def draw(self):
        screen.blit(ghost_image, (self.x, self.y))


class Pellet:
    def __init__(self, x, y, is_special=False):
        self.x = x
        self.y = y
        self.is_special = is_special

    def draw(self):
        color = RED if self.is_special else WHITE
        radius = 10 if self.is_special else 5
        pygame.draw.circle(screen, color, (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2), radius)

class Door:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, CELL_SIZE, CELL_SIZE))

# Generate walls for the maze
def generate_maze():
    walls = []

    # Borders (including bottom border for full enclosure)
    for i in range(0, WIDTH, CELL_SIZE):
        walls.append(pygame.Rect(i, 0, CELL_SIZE, CELL_SIZE))  # Top border
        walls.append(pygame.Rect(i, HEIGHT - CELL_SIZE, CELL_SIZE, CELL_SIZE))  # Bottom border
    for i in range(0, HEIGHT, CELL_SIZE):
        walls.append(pygame.Rect(0, i, CELL_SIZE, CELL_SIZE))  # Left border
        walls.append(pygame.Rect(WIDTH - CELL_SIZE, i, CELL_SIZE, CELL_SIZE))  # Right border

    # Inner maze structure
    maze_structure = [
        "####################",
        "#........#.........#",
        "#.####.#.#.#######.#",
        "#.#....#.#........#",
        "#.#######.#######.#",
        "#..................#",
        "#.####.#####.#####.#",
        "#......#.....#.....#",
        "######.#.#########..",
        "#......#...........#",
        "..........#####.....",
        ".########......#######",
        "#........#.........#",
        "#.####.#.#.#######.#",
        "#.#....#.#........#",
        "#.#######.#######.#",
        "#..................#",
        "#.####.#####.#####.#",
        "#......#.....#.....#",
        "######.#.#########..",
    ]

    for row_idx, row in enumerate(maze_structure):
        for col_idx, cell in enumerate(row):
            if cell == "#":
                walls.append(pygame.Rect(col_idx * CELL_SIZE, row_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    return walls


# Generate pellets
def generate_pellets(walls):
    pellets = []
    for x in range(0, WIDTH, CELL_SIZE):
        for y in range(0, HEIGHT, CELL_SIZE):
            if (x, y) not in walls:
                if x == WIDTH // 2 - CELL_SIZE // 2 and y == HEIGHT // 2 - CELL_SIZE // 2:
                    pellets.append(Pellet(x, y, is_special=True))
                else:
                    pellets.append(Pellet(x, y))
    return pellets

# Menu to restart game
def restart_menu(win=False):
    global pacman_image
    while True:
        screen.fill(BLACK)
        if win:
            menu_text = font.render("You Win! Press R to Restart or Q to Quit", True, WHITE)
        else:
            menu_text = font.render("Game Over! Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pacman_image = pygame.image.load(resource_path("Pacman.png"))  # Add the correct path to your Pacman PNG
                    pacman_image = pygame.transform.scale(pacman_image, (CELL_SIZE, CELL_SIZE))
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

#Image rotation stuff yay
def rotate_img(original_image, current_dir, rotate_dir):
    """
    Rotates and flips Pacman's image to align with the desired direction.

    Args:
        original_image (pygame.Surface): The untransformed Pacman image.
        current_dir (str): The current direction of Pacman (e.g., "Up", "Down", "Left", "Right").
        rotate_dir (str): The desired direction to rotate Pacman to.

    Returns:
        pygame.Surface: The rotated and/or flipped image of Pacman.
    """
    # Direction to rotation angles relative to the "Right" orientation
    direction_to_angle = {
        "Right": 0,
        "Up": 90,
        "Left": 180,
        "Down": -90
    }

    # Default direction if current_dir is None
    if current_dir is None:
        current_dir = "Right"

    # If no change in direction, return the original image
    if current_dir == rotate_dir:
        return original_image

    # Start with the original image for transformation
    transformed_image = original_image

    # Handle flipping for Left and Right transitions
    if (current_dir == "Right" and rotate_dir == "Left") or \
            (current_dir == "Left" and rotate_dir == "Right"):
        transformed_image = pygame.transform.flip(original_image, flip_x=True, flip_y=False)
        return transformed_image

    # Determine the required rotation angle
    current_angle = direction_to_angle[current_dir]
    target_angle = direction_to_angle[rotate_dir]
    rotation_angle = target_angle - current_angle

    # Apply rotation for all other direction changes
    transformed_image = pygame.transform.rotate(original_image, rotation_angle)
    return transformed_image

def is_touching(pacman, pellet):
    return (
        pacman.x // CELL_SIZE * CELL_SIZE == pellet.x and
        pacman.y // CELL_SIZE * CELL_SIZE == pellet.y
    )



# Game logic
def main_game():
    global pacman_image
    clock = pygame.time.Clock()
    pacman = Pacman(CELL_SIZE, CELL_SIZE)

    # Initialize ghosts for the first level
    ghosts = [
        Ghost(WIDTH - CELL_SIZE * 2, CELL_SIZE),
        Ghost(WIDTH - CELL_SIZE * 2, HEIGHT - CELL_SIZE * 2),
        Ghost(CELL_SIZE, HEIGHT - CELL_SIZE * 2),
    ]

    # Maze generation and pellet setup
    walls = generate_maze()
    pellets = generate_pellets(walls)
    door = Door(WIDTH - CELL_SIZE * 2, HEIGHT // 2)
    current_direction = None

    score = 0
    level = 1  # Starting level
    running = True
    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    rotate_to = "Up"
                    pacman.dx, pacman.dy = 0, -PACMAN_SPEED
                    pacman_image = rotate_img(pacman_image, current_direction, rotate_to)
                    current_direction = "Up"
                elif event.key == pygame.K_DOWN:
                    rotate_to = "Down"
                    pacman.dx, pacman.dy = 0, PACMAN_SPEED
                    pacman_image = rotate_img(pacman_image, current_direction, rotate_to)
                    current_direction = "Down"
                elif event.key == pygame.K_LEFT:
                    rotate_to = "Left"
                    pacman.dx, pacman.dy = -PACMAN_SPEED, 0
                    pacman_image = rotate_img(pacman_image, current_direction, rotate_to)
                    current_direction = "Left"
                elif event.key == pygame.K_RIGHT:
                    rotate_to = "Right"
                    pacman.dx, pacman.dy = PACMAN_SPEED, 0
                    pacman_image = rotate_img(pacman_image, current_direction, rotate_to)
                    current_direction = "Right"

        # Update game state
        pacman.move(walls)

        for ghost in ghosts:
            ghost.move(pacman.x, pacman.y, walls)

        # Check for pellet collision
        pellets = [
            pellet
            for pellet in pellets
            if not is_touching(pacman, pellet) or not (score := score + (50 if pellet.is_special else 10))
        ]

        # Check for ghost collision
        for ghost in ghosts:
            if abs(pacman.x - ghost.x) < CELL_SIZE * 1.5 and abs(pacman.y - ghost.y) < CELL_SIZE * 1.5:
                ghost_collision_sound.play()  # Play the sound when colliding with a ghost
                running = False

        # Check if Pacman reaches the door and has enough points
        required_points = 300 + (level - 1) * 100  # Points required for the current level
        if abs(pacman.x - door.x) < CELL_SIZE and abs(pacman.y - door.y) < CELL_SIZE:
            if score >= required_points:  # Check if the player has enough points
                if edo_choice_and_question(level):
                    level += 1  # Level up, add more ghosts and increase point requirement
                    # Add an extra ghost for the next level
                    ghosts.append(Ghost(WIDTH - CELL_SIZE * 2, HEIGHT - CELL_SIZE * 2))
                else:
                    running = False
            else:
                # Display message informing the player they need more points
                points_needed = required_points - score
                message = f"You need {points_needed} more points to enter!"
                message_text = font.render(message, True, WHITE)

                # Draw a semi-transparent background for the message
                message_bg_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 - 20, WIDTH // 2, 40)
                pygame.draw.rect(screen, (0, 0, 0, 128), message_bg_rect)  # Semi-transparent black background
                screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2 - 20))

        # Draw game objects: walls, pacman, ghosts, pellets, etc.
        pacman.draw()
        for ghost in ghosts:
            ghost.draw()
        for pellet in pellets:
            pellet.draw()
        door.draw()
        for wall in walls:
            pygame.draw.rect(screen, BLUE, (wall[0], wall[1], CELL_SIZE, CELL_SIZE))

        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(level_text, (200, 13))
        screen.blit(score_text, (10, 13))

        # Display message only after all game objects
        if score < required_points and abs(pacman.x - door.x) < CELL_SIZE and abs(pacman.y - door.y) < CELL_SIZE:
            points_needed = required_points - score
            message = f"You need {points_needed} more points to enter!"
            message_text = font.render(message, True, WHITE)
            message_bg_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 - 20, WIDTH // 2, 40)
            pygame.draw.rect(screen, (0, 0, 0, 128), message_bg_rect)  # Semi-transparent black background
            screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2 - 20))

        pygame.display.flip()
        clock.tick(FPS)

    return restart_menu()



def edo_question(selected_question):
    question, answer = selected_question
    input_text = ""
    running = True
    while running:
        screen.fill(BLACK)

        # Display question
        question_text = font.render(question, True, WHITE)
        screen.blit(question_text, (20, HEIGHT // 3))

        # Display input
        input_surface = font.render(input_text, True, WHITE)
        screen.blit(input_surface, (20, HEIGHT // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text == answer:
                        return True
                    else:
                        input_text = "Incorrect! Try again."
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        pygame.display.flip()

# Function to choose EDO type and question for the user
def edo_choice_and_question(level):
    if level == 1:
        edo_options = [
            # Separation of Variables
            ("Solve: dy/dx = y/x, y(1) = 2", "2 * x"),
            # Homogeneous Equation
            ("Solve: dy/dx = (x + y) / (x - y), y(1) = 1", "(x + sqrt(3)) / (1 + sqrt(3))"),
            # Exact Equation
            ("Solve: (2x + y)dx + (x + y)dy = 0", "-x^2 - xy - y^2 = C"),
        ]
    elif level == 2:
        edo_options = [
            ("Solve: dy/dx = x^2 - y^2, y(0) = 1", "tan(x)"),
            ("Solve: dy/dx = e^(x+y), y(0) = 0", "ln(e^x - 1)"),
            ("Solve: x dy/dx + y = e^x, y(1) = e", "e^x / x"),
        ]
    elif level == 3:
        edo_options = [
            ("Solve: x^2 dy/dx + 2xy = x, y(1) = 0", "ln(x) - 1/x"),
            ("Solve: dy/dx = sin(x)cos(y), y(0) = pi/2", "pi/2 - sin(x)"),
            ("Solve: dy/dx = (x^2 + y^2)/(2xy), y(1) = 1", "sqrt(2x - x^2)"),
        ]

    running = True
    selected_question = None

    while running:
        screen.fill(BLACK)

        # Display level and instructions
        instructions = font.render(f"Choose EDO for Level {level}", True, WHITE)
        screen.blit(instructions, (20, HEIGHT // 4))

        # Display options
        for i, (question, _) in enumerate(edo_options):
            option_text = font.render(f"{i + 1}. {question}", True, WHITE)
            screen.blit(option_text, (20, HEIGHT // 2 + i * 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    selected_question = edo_options[int(event.unicode) - 1]
                    running = False

        pygame.display.flip()

    # Answering the selected EDO
    return edo_question(selected_question)

# Main loop
def main():
    while True:
        if not main_game():
            break

if __name__ == "__main__":
    main()
