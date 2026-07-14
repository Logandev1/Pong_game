import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Game settings
BALL_SIZE = 15
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 6
BALL_SPEED = 5
MAX_BALL_SPEED = 10

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0

    def update(self):
        # Move paddle
        self.rect.y += self.speed
        
        # Keep paddle in bounds
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)

    def move_up(self):
        self.speed = -PADDLE_SPEED

    def move_down(self):
        self.speed = PADDLE_SPEED

    def stop(self):
        self.speed = 0


class Ball:
    def __init__(self):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - BALL_SIZE // 2,
            SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
            BALL_SIZE,
            BALL_SIZE
        )
        self.vx = BALL_SPEED
        self.vy = BALL_SPEED
        self.reset()

    def reset(self):
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT // 2
        self.vx = BALL_SPEED
        self.vy = BALL_SPEED

    def update(self):
        # Move ball
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Bounce off top and bottom
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy = -self.vy
            # Keep ball in bounds
            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

    def draw(self, screen):
        pygame.draw.ellipse(screen, WHITE, self.rect)

    def check_paddle_collision(self, paddle):
        if self.rect.colliderect(paddle.rect):
            self.vx = -self.vx
            
            # Add spin based on where ball hit paddle
            if paddle.rect.centery < self.rect.centery:
                self.vy += PADDLE_SPEED * 0.5
            elif paddle.rect.centery > self.rect.centery:
                self.vy -= PADDLE_SPEED * 0.5
            
            # Cap ball speed
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed > MAX_BALL_SPEED:
                self.vx = (self.vx / speed) * MAX_BALL_SPEED
                self.vy = (self.vy / speed) * MAX_BALL_SPEED
            
            # Push ball away from paddle
            if self.vx < 0:
                self.rect.left = paddle.rect.right
            else:
                self.rect.right = paddle.rect.left

    def is_out_of_bounds(self):
        return self.rect.left < 0 or self.rect.right > SCREEN_WIDTH


class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Pong Game")
        self.clock = pygame.time.Clock()
        
        # Create paddles
        self.player1 = Paddle(20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.player2 = Paddle(SCREEN_WIDTH - 20 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        
        # Create ball
        self.ball = Ball()
        
        # Score
        self.score1 = 0
        self.score2 = 0
        
        # Font
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        
        # Touch controls
        self.touch_active = False
        self.touch_y = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.player1.move_up()
                if event.key == pygame.K_s:
                    self.player1.move_down()
                if event.key == pygame.K_UP:
                    self.player2.move_up()
                if event.key == pygame.K_DOWN:
                    self.player2.move_down()
            
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s):
                    self.player1.stop()
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.player2.stop()
            
            # Touch controls
            if event.type == pygame.FINGERDOWN:
                self.touch_active = True
                self.touch_y = event.y * SCREEN_HEIGHT
            
            if event.type == pygame.FINGERMOTION and self.touch_active:
                self.touch_y = event.y * SCREEN_HEIGHT
            
            if event.type == pygame.FINGERUP:
                self.touch_active = False
                self.player1.stop()
        
        return True

    def update_touch_controls(self):
        if self.touch_active:
            # Left side controls player 1
            self.player1.rect.centery = self.touch_y
            # Keep paddle in bounds
            if self.player1.rect.top < 0:
                self.player1.rect.top = 0
            if self.player1.rect.bottom > SCREEN_HEIGHT:
                self.player1.rect.bottom = SCREEN_HEIGHT

    def update(self):
        self.player1.update()
        self.player2.update()
        self.ball.update()
        
        # Ball collision with paddles
        self.ball.check_paddle_collision(self.player1)
        self.ball.check_paddle_collision(self.player2)
        
        # Simple AI for player 2
        if self.ball.rect.centery < self.player2.rect.centery - 35:
            self.player2.move_up()
        elif self.ball.rect.centery > self.player2.rect.centery + 35:
            self.player2.move_down()
        else:
            self.player2.stop()
        
        # Ball out of bounds
        if self.ball.is_out_of_bounds():
            if self.ball.rect.left < 0:
                self.score2 += 1
            else:
                self.score1 += 1
            self.ball.reset()

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw center line
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.line(self.screen, GRAY, (SCREEN_WIDTH // 2, y), (SCREEN_WIDTH // 2, y + 10), 2)
        
        # Draw paddles and ball
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        self.ball.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"{self.score1}  {self.score2}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))
        
        # Draw controls info
        controls_text = self.small_font.render("W/S or UP/DOWN to move | Touch to control", True, GRAY)
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update_touch_controls()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = PongGame()
    game.run()
