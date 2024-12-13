import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800

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
        new_x = self.x + self.dx
        new_y = self.y + self.dy
        if (new_x // CELL_SIZE * CELL_SIZE, new_y // CELL_SIZE * CELL_SIZE) not in walls and 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT:
            self.x = new_x
            self.y = new_y

    def draw(self):
        # Draw Pacman using the image
        screen.blit(pacman_image, (self.x, self.y))

class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move_towards(self, target_x, target_y, walls):
        directions = [(0, -GHOST_SPEED), (0, GHOST_SPEED), (-GHOST_SPEED, 0), (GHOST_SPEED, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            if (new_x // CELL_SIZE * CELL_SIZE, new_y // CELL_SIZE * CELL_SIZE) not in walls and 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT:
                if abs(new_x - target_x) + abs(new_y - target_y) < abs(self.x - target_x) + abs(self.y - target_y):
                    self.x = new_x
                    self.y = new_y
                    break

    def draw(self):
        # Draw Ghost using the image
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
    walls = set()

    # Borders (excluding bottom border for free movement)
    for i in range(0, WIDTH, CELL_SIZE):
        walls.add((i, 0))
    for i in range(0, HEIGHT, CELL_SIZE):
        walls.add((0, i))
        walls.add((WIDTH - CELL_SIZE, i))

    # Inner maze structure (similar to Pac-Man)
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
                walls.add((col_idx * CELL_SIZE, row_idx * CELL_SIZE))

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
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Game logic
def main_game():
    clock = pygame.time.Clock()
    pacman = Pacman(CELL_SIZE, CELL_SIZE)
    ghosts = [Ghost(WIDTH - CELL_SIZE * 2, CELL_SIZE), Ghost(WIDTH - CELL_SIZE * 2, HEIGHT - CELL_SIZE * 2), Ghost(CELL_SIZE, HEIGHT - CELL_SIZE * 2)]
    walls = generate_maze()
    pellets = generate_pellets(walls)
    door = Door(WIDTH - CELL_SIZE * 2, HEIGHT // 2)

    score = 0
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
                    pacman.dx, pacman.dy = 0, -PACMAN_SPEED
                elif event.key == pygame.K_DOWN:
                    pacman.dx, pacman.dy = 0, PACMAN_SPEED
                elif event.key == pygame.K_LEFT:
                    pacman.dx, pacman.dy = -PACMAN_SPEED, 0
                elif event.key == pygame.K_RIGHT:
                    pacman.dx, pacman.dy = PACMAN_SPEED, 0

        # Update game state
        pacman.move(walls)

        for ghost in ghosts:
            ghost.move_towards(pacman.x, pacman.y, walls)

        # Check for pellet collision
        new_pellets = []
        for pellet in pellets:
            if pacman.x // CELL_SIZE * CELL_SIZE == pellet.x and pacman.y // CELL_SIZE * CELL_SIZE == pellet.y:
                score += 50 if pellet.is_special else 10
                if pellet.is_special:
                    pellets.remove(pellet)
                else:
                    new_pellets.append(pellet)
            else:
                new_pellets.append(pellet)
        pellets = new_pellets

        # Check for ghost collision
        for ghost in ghosts:
            if abs(pacman.x - ghost.x) < CELL_SIZE and abs(pacman.y - ghost.y) < CELL_SIZE:
                running = False

        # Check if Pacman reaches the door
        if abs(pacman.x - door.x) < CELL_SIZE and abs(pacman.y - door.y) < CELL_SIZE:
            if edo_question():
                return restart_menu(win=True)
            else:
                running = False

        # Draw objects
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
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    return restart_menu()

# Question prompt for EDO
questions = [
    ("Solve: dy/dx = 2x, y(0) = 1", "x**2 + 1"),
    ("Solve: dy/dx = -3y, y(0) = 4", "4 * exp(-3*x)"),
]

def edo_question():
    question, answer = random.choice(questions)

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

# Main loop
def main():
    while True:
        if not main_game():
            break

if __name__ == "__main__":
    main()
