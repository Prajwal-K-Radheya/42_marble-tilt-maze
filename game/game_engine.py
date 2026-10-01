import pygame
from .marble import Marble
from .wall import Wall

# Game Engine

WHITE = (255, 255, 255)
DARK = (40, 40, 50)
WALL_COLOR = (90, 90, 110)
GOAL_COLOR = (60, 200, 120)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.marble = Marble(50, 50)
        self.tilt_strength = 0.6
        self.friction = 0.02
        self.max_speed = 9

        self.walls = self._build_maze()
        self.goal_x = width - 60
        self.goal_y = height - 60
        self.goal_radius = 22

        self.time_limit_ms = 45000
        self.start_ticks = pygame.time.get_ticks()

        self.font = pygame.font.SysFont("Arial", 26)

        self.game_over = False
        self.result = None  # "solved" or "timeout"
        self.finish_time_ms = None

    def _build_maze(self):
        walls = []
        t = 16  # wall thickness

        # Outer boundary
        walls.append(Wall(0, 0, self.width, t))
        walls.append(Wall(0, self.height - t, self.width, t))
        walls.append(Wall(0, 0, t, self.height))
        walls.append(Wall(self.width - t, 0, t, self.height))

        # Internal walls
        walls.append(Wall(0, 140, self.width - 140, t))
        walls.append(Wall(140, 260, self.width - 140, t))
        walls.append(Wall(0, 380, self.width - 140, t))

        return walls

    def handle_event(self, event):
        # If the game is over, pressing any key exits the game.
        if self.game_over and event.type == pygame.KEYDOWN:
            return True

        return False

    def handle_input(self):
        if self.game_over:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()

        dx = mouse_x - self.width // 2
        dy = mouse_y - self.height // 2

        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)

        ax = (dx / dist) * self.tilt_strength
        ay = (dy / dist) * self.tilt_strength

        self.marble.vx += ax
        self.marble.vy += ay

    def update(self):
        if self.game_over:
            return

        elapsed = pygame.time.get_ticks() - self.start_ticks

        # Check timeout
        if elapsed >= self.time_limit_ms:
            self.game_over = True
            self.result = "timeout"
            return

        # Apply friction
        self.marble.vx *= (1 - self.friction)
        self.marble.vy *= (1 - self.friction)

        # Limit maximum speed
        speed = (self.marble.vx ** 2 + self.marble.vy ** 2) ** 0.5

        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.marble.vx *= scale
            self.marble.vy *= scale

        # Move marble
        self.marble.x += self.marble.vx
        self.marble.y += self.marble.vy

        # Resolve collisions
        self._resolve_wall_collisions()

        # Check goal
        gx = self.goal_x - self.marble.x
        gy = self.goal_y - self.marble.y

        if (gx ** 2 + gy ** 2) ** 0.5 <= self.goal_radius:
            self.game_over = True
            self.result = "solved"
            self.finish_time_ms = elapsed

    def _resolve_wall_collisions(self):
        """
        Resolve collisions between the circular marble
        and rectangular walls.
        """

        for wall in self.walls:
            wall_rect = wall.rect()

            # Find the closest point on the rectangle
            # to the center of the marble.
            closest_x = max(
                wall_rect.left,
                min(self.marble.x, wall_rect.right)
            )

            closest_y = max(
                wall_rect.top,
                min(self.marble.y, wall_rect.bottom)
            )

            dx = self.marble.x - closest_x
            dy = self.marble.y - closest_y

            distance_sq = dx * dx + dy * dy
            radius = self.marble.radius

            # Normal case:
            # marble is outside the wall but touching it.
            if 0 < distance_sq < radius * radius:
                distance = distance_sq ** 0.5

                nx = dx / distance
                ny = dy / distance

                # Push marble outside the wall.
                penetration = radius - distance

                self.marble.x += nx * penetration
                self.marble.y += ny * penetration

                # Calculate velocity toward the wall.
                velocity_into_wall = (
                    self.marble.vx * nx
                    + self.marble.vy * ny
                )

                # Bounce only when moving into the wall.
                if velocity_into_wall < 0:
                    restitution = 0.3

                    self.marble.vx -= (
                        (1 + restitution)
                        * velocity_into_wall
                        * nx
                    )

                    self.marble.vy -= (
                        (1 + restitution)
                        * velocity_into_wall
                        * ny
                    )

            # Special case:
            # marble center is inside the wall.
            elif distance_sq == 0 and wall_rect.collidepoint(
                self.marble.x,
                self.marble.y
            ):
                distances = {
                    "left": self.marble.x - wall_rect.left,
                    "right": wall_rect.right - self.marble.x,
                    "top": self.marble.y - wall_rect.top,
                    "bottom": wall_rect.bottom - self.marble.y,
                }

                side = min(distances, key=distances.get)

                if side == "left":
                    nx, ny = -1, 0
                    penetration = radius + distances["left"]

                elif side == "right":
                    nx, ny = 1, 0
                    penetration = radius + distances["right"]

                elif side == "top":
                    nx, ny = 0, -1
                    penetration = radius + distances["top"]

                else:
                    nx, ny = 0, 1
                    penetration = radius + distances["bottom"]

                # Push marble outside the wall.
                self.marble.x += nx * penetration
                self.marble.y += ny * penetration

                # Calculate velocity toward the wall.
                velocity_into_wall = (
                    self.marble.vx * nx
                    + self.marble.vy * ny
                )

                # Bounce only when moving into the wall.
                if velocity_into_wall < 0:
                    restitution = 0.3

                    self.marble.vx -= (
                        (1 + restitution)
                        * velocity_into_wall
                        * nx
                    )

                    self.marble.vy -= (
                        (1 + restitution)
                        * velocity_into_wall
                        * ny
                    )

    def render(self, screen):
        screen.fill(DARK)

        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(
                screen,
                WALL_COLOR,
                wall.rect()
            )

        # Draw goal
        pygame.draw.circle(
            screen,
            GOAL_COLOR,
            (self.goal_x, self.goal_y),
            self.goal_radius
        )

        # Draw marble
        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.marble.x),
                int(self.marble.y)
            ),
            self.marble.radius
        )

        # Draw timer
        elapsed = pygame.time.get_ticks() - self.start_ticks

        seconds_left = max(
            0,
            (self.time_limit_ms - elapsed) // 1000
        )

        timer_text = self.font.render(
            f"Time: {seconds_left}s",
            True,
            WHITE
        )

        screen.blit(timer_text, (10, 10))

        # Game Over screen
        if self.game_over:

            # Dark transparent overlay
            overlay = pygame.Surface(
                (self.width, self.height)
            )

            overlay.set_alpha(210)
            overlay.fill((0, 0, 0))

            screen.blit(
                overlay,
                (0, 0)
            )

            # Determine result
            if self.result == "solved":
                title_text = "MAZE SOLVED!"

                time_text = (
                    f"Finish Time: "
                    f"{self.finish_time_ms / 1000:.1f}s"
                )

            else:
                title_text = "TIME'S UP!"

                time_text = (
                    "The maze was not solved."
                )

            # Create text surfaces
            title_surface = self.font.render(
                title_text,
                True,
                WHITE
            )

            time_surface = self.font.render(
                time_text,
                True,
                WHITE
            )

            instruction_surface = self.font.render(
                "Press any key to exit",
                True,
                WHITE
            )

            # Draw title
            screen.blit(
                title_surface,
                title_surface.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 - 60
                    )
                )
            )

            # Draw result/time
            screen.blit(
                time_surface,
                time_surface.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2
                    )
                )
            )

            # Draw instruction
            screen.blit(
                instruction_surface,
                instruction_surface.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 + 60
                    )
                )
            )