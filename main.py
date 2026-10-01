import pygame
from game.game_engine import GameEngine


# Initialize pygame
pygame.init()


# Screen dimensions
WIDTH = 600
HEIGHT = 500

SCREEN = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Marble Tilt Maze - Pygame Version"
)


# Clock
clock = pygame.time.Clock()
FPS = 60


def show_menu():
    """
    Display the difficulty selection menu.
    Returns the selected difficulty or None to exit.
    """

    font = pygame.font.SysFont(
        "Arial",
        28
    )

    title_font = pygame.font.SysFont(
        "Arial",
        36
    )

    while True:

        SCREEN.fill((40, 40, 50))

        title = title_font.render(
            "MARBLE TILT MAZE",
            True,
            (255, 255, 255)
        )

        subtitle = font.render(
            "Choose Difficulty",
            True,
            (255, 255, 255)
        )

        easy = font.render(
            "1 - EASY   (60 seconds)",
            True,
            (255, 255, 255)
        )

        medium = font.render(
            "2 - MEDIUM (45 seconds)",
            True,
            (255, 255, 255)
        )

        hard = font.render(
            "3 - HARD   (30 seconds)",
            True,
            (255, 255, 255)
        )

        exit_text = font.render(
            "4 - EXIT",
            True,
            (255, 255, 255)
        )

        SCREEN.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 80)
            )
        )

        SCREEN.blit(
            subtitle,
            subtitle.get_rect(
                center=(WIDTH // 2, 140)
            )
        )

        SCREEN.blit(
            easy,
            easy.get_rect(
                center=(WIDTH // 2, 210)
            )
        )

        SCREEN.blit(
            medium,
            medium.get_rect(
                center=(WIDTH // 2, 260)
            )
        )

        SCREEN.blit(
            hard,
            hard.get_rect(
                center=(WIDTH // 2, 310)
            )
        )

        SCREEN.blit(
            exit_text,
            exit_text.get_rect(
                center=(WIDTH // 2, 360)
            )
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    return "easy"

                elif event.key == pygame.K_2:
                    return "medium"

                elif event.key == pygame.K_3:
                    return "hard"

                elif event.key == pygame.K_4:
                    return None

        clock.tick(FPS)


def play_game(difficulty):
    """
    Run one game using the selected difficulty.

    Returns:
        "replay" when player wants another game
        "exit" when player wants to quit
    """

    engine = GameEngine(
        WIDTH,
        HEIGHT,
        difficulty
    )

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "exit"

            key_pressed = engine.handle_event(event)

            if key_pressed is not None:

                # Game is over.
                # Return to difficulty menu.
                return "replay"

        engine.handle_input()

        engine.update()

        engine.render(SCREEN)

        pygame.display.flip()

        clock.tick(FPS)

    return "exit"


def main():

    running = True

    # First show difficulty menu
    difficulty = show_menu()

    if difficulty is None:
        running = False

    while running:

        result = play_game(difficulty)

        if result == "exit":
            running = False

        elif result == "replay":

            # Show difficulty menu again
            difficulty = show_menu()

            if difficulty is None:
                running = False

    pygame.quit()


if __name__ == "__main__":
    main()