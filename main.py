import pygame
import random
import sys
from enum import Enum

# Инициализация pygame
pygame.init()

# Константы
class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

class GameConfig:
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 600
    GRID_SIZE = 20
    GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
    GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
    FPS = 10

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Начальная позиция змейки
        self.positions = [(GameConfig.GRID_WIDTH // 2, GameConfig.GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.grow_pending = 3  # Начальная длина змейки
        self.score = 0
    
    def get_head_position(self):
        return self.positions[0]
    
    def move(self):
        head_x, head_y = self.get_head_position()
        
        # Движение в зависимости от направления
        if self.direction == Direction.UP:
            new_position = (head_x, head_y - 1)
        elif self.direction == Direction.DOWN:
            new_position = (head_x, head_y + 1)
        elif self.direction == Direction.LEFT:
            new_position = (head_x - 1, head_y)
        elif self.direction == Direction.RIGHT:
            new_position = (head_x + 1, head_y)
        
        # Добавляем новую голову
        self.positions.insert(0, new_position)
        
        # Удаляем хвост, если не нужно расти
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()
    
    def grow(self):
        self.grow_pending += 1
        self.score += 1
    
    def check_collision(self):
        head_x, head_y = self.get_head_position()
        
        # Проверка столкновения со стеной
        if (head_x < 0 or head_x >= GameConfig.GRID_WIDTH or
            head_y < 0 or head_y >= GameConfig.GRID_HEIGHT):
            return True
        
        # Проверка столкновения с собой
        if self.get_head_position() in self.positions[1:]:
            return True
        
        return False
    
    def change_direction(self, new_direction):
        # Предотвращаем движение в противоположном направлении
        if ((new_direction == Direction.UP and self.direction != Direction.DOWN) or
            (new_direction == Direction.DOWN and self.direction != Direction.UP) or
            (new_direction == Direction.LEFT and self.direction != Direction.RIGHT) or
            (new_direction == Direction.RIGHT and self.direction != Direction.LEFT)):
            self.direction = new_direction

class Food:
    def __init__(self, snake):
        self.position = self.generate_position(snake)
    
    def generate_position(self, snake):
        while True:
            position = (random.randint(0, GameConfig.GRID_WIDTH - 1),
                       random.randint(0, GameConfig.GRID_HEIGHT - 1))
            if position not in snake.positions:
                return position
    
    def respawn(self, snake):
        self.position = self.generate_position(snake)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        pygame.display.set_caption('Змейка - ООП')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        
        self.snake = Snake()
        self.food = Food(self.snake)
        self.game_over = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(Direction.RIGHT)
    
    def update(self):
        if not self.game_over:
            self.snake.move()
            
            # Проверка столкновения с едой
            if self.snake.get_head_position() == self.food.position:
                self.snake.grow()
                self.food.respawn(self.snake)
            
            # Проверка столкновений
            if self.snake.check_collision():
                self.game_over = True
    
    def draw(self):
        self.screen.fill(Colors.BLACK)
        
        # Рисуем сетку (опционально)
        for x in range(0, GameConfig.WINDOW_WIDTH, GameConfig.GRID_SIZE):
            pygame.draw.line(self.screen, Colors.BLUE, (x, 0), (x, GameConfig.WINDOW_HEIGHT))
        for y in range(0, GameConfig.WINDOW_HEIGHT, GameConfig.GRID_SIZE):
            pygame.draw.line(self.screen, Colors.BLUE, (0, y), (GameConfig.WINDOW_WIDTH, y))
        
        # Рисуем змейку
        for position in self.snake.positions:
            rect = pygame.Rect(position[0] * GameConfig.GRID_SIZE,
                             position[1] * GameConfig.GRID_SIZE,
                             GameConfig.GRID_SIZE, GameConfig.GRID_SIZE)
            pygame.draw.rect(self.screen, Colors.GREEN, rect)
            pygame.draw.rect(self.screen, Colors.BLACK, rect, 1)
        
        # Рисуем еду
        food_rect = pygame.Rect(self.food.position[0] * GameConfig.GRID_SIZE,
                              self.food.position[1] * GameConfig.GRID_SIZE,
                              GameConfig.GRID_SIZE, GameConfig.GRID_SIZE)
        pygame.draw.rect(self.screen, Colors.RED, food_rect)
        
        # Рисуем счет
        score_text = self.font.render(f'Счет: {self.snake.score}', True, Colors.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Рисуем сообщение о конце игры
        if self.game_over:
            game_over_text = self.font.render('Игра окончена! Нажмите R для перезапуска или Q для выхода', 
                                            True, Colors.WHITE)
            text_rect = game_over_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 
                                                      GameConfig.WINDOW_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
    
    def restart_game(self):
        self.snake.reset()
        self.food.respawn(self.snake)
        self.game_over = False
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(GameConfig.FPS)

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()