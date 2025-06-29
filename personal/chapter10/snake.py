import pygame
import random
import sys
from pygame.locals import *

# 初始化pygame
pygame.init()
pygame.font.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
DARK_GREEN = (0, 100, 0)

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 难度设置
DIFFICULTIES = {
    "简单": {"speed": 8, "color": GREEN, "obstacles": 5},
    "中等": {"speed": 12, "color": BLUE, "obstacles": 10},
    "困难": {"speed": 16, "color": RED, "obstacles": 15}
}

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.length = 1
        self.score = 0
        self.color = GREEN
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_position = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        # 检查是否撞到自己
        if new_position in self.positions[1:]:
            return False
            
        self.positions.insert(0, new_position)
        if len(self.positions) > self.length:
            self.positions.pop()
            
        return True
    
    def render(self, surface):
        for i, p in enumerate(self.positions):
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            # 蛇头用深色区分
            color = DARK_GREEN if i == 0 else self.color
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
        
    def randomize_position(self, snake_positions=None, obstacles=None):
        if snake_positions is None:
            snake_positions = []
        if obstacles is None:
            obstacles = []
            
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), 
                            random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_positions and self.position not in obstacles:
                break
    
    def render(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), 
                          (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

class Obstacle:
    def __init__(self, position):
        self.position = position
        self.color = BLUE
        
    def render(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), 
                          (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("贪吃蛇游戏")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('SimHei', 24)
        self.big_font = pygame.font.SysFont('SimHei', 48)
        self.snake = Snake()
        self.food = Food()
        self.obstacles = []
        self.difficulty = "中等"
        self.game_speed = DIFFICULTIES[self.difficulty]["speed"]
        self.snake.color = DIFFICULTIES[self.difficulty]["color"]
        self.game_state = "MENU"  # MENU, PLAYING, GAME_OVER, PAUSED
        self.generate_obstacles()
        
    def generate_obstacles(self):
        self.obstacles = []
        num_obstacles = DIFFICULTIES[self.difficulty]["obstacles"]
        for _ in range(num_obstacles):
            while True:
                pos = (random.randint(0, GRID_WIDTH - 1), 
                       random.randint(0, GRID_HEIGHT - 1))
                # 确保不生成在蛇头或食物位置
                if (pos != self.snake.get_head_position() and 
                    pos != self.food.position and 
                    pos not in [ob.position for ob in self.obstacles]):
                    self.obstacles.append(Obstacle(pos))
                    break
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if self.game_state == "PLAYING":
                    if event.key == K_UP and self.snake.direction != DOWN:
                        self.snake.direction = UP
                    elif event.key == K_DOWN and self.snake.direction != UP:
                        self.snake.direction = DOWN
                    elif event.key == K_LEFT and self.snake.direction != RIGHT:
                        self.snake.direction = LEFT
                    elif event.key == K_RIGHT and self.snake.direction != LEFT:
                        self.snake.direction = RIGHT
                    elif event.key == K_p:
                        self.game_state = "PAUSED"
                elif self.game_state == "PAUSED":
                    if event.key == K_p:
                        self.game_state = "PLAYING"
                elif self.game_state == "MENU":
                    if event.key == K_1:
                        self.difficulty = "简单"
                    elif event.key == K_2:
                        self.difficulty = "中等"
                    elif event.key == K_3:
                        self.difficulty = "困难"
                    elif event.key == K_RETURN:
                        self.start_game()
                elif self.game_state == "GAME_OVER":
                    if event.key == K_RETURN:
                        self.reset_game()
                        self.game_state = "MENU"
    
    def start_game(self):
        self.snake.reset()
        self.snake.color = DIFFICULTIES[self.difficulty]["color"]
        self.game_speed = DIFFICULTIES[self.difficulty]["speed"]
        self.generate_obstacles()
        self.food.randomize_position(self.snake.positions, 
                                    [ob.position for ob in self.obstacles])
        self.game_state = "PLAYING"
    
    def reset_game(self):
        self.snake.reset()
        self.generate_obstacles()
        self.food.randomize_position(self.snake.positions, 
                                    [ob.position for ob in self.obstacles])
    
    def update(self):
        if self.game_state != "PLAYING":
            return
            
        if not self.snake.update():
            self.game_state = "GAME_OVER"
            return
            
        # 检查是否撞到障碍物
        head = self.snake.get_head_position()
        for obstacle in self.obstacles:
            if head == obstacle.position:
                self.game_state = "GAME_OVER"
                return
            
        # 检查是否吃到食物
        if head == self.food.position:
            self.snake.length += 1
            self.snake.score += 10
            self.food.randomize_position(self.snake.positions, 
                                        [ob.position for ob in self.obstacles])
    
    def render(self):
        self.screen.fill(WHITE)
        
        if self.game_state == "MENU":
            self.render_menu()
        elif self.game_state == "PLAYING" or self.game_state == "PAUSED":
            self.render_game()
            if self.game_state == "PAUSED":
                self.render_pause()
        elif self.game_state == "GAME_OVER":
            self.render_game()
            self.render_game_over()
            
        pygame.display.flip()
    
    def render_menu(self):
        # 标题
        title = self.big_font.render("贪吃蛇游戏", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # 难度选择
        difficulty_text = self.font.render("请选择难度:", True, BLACK)
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(difficulty_text, difficulty_rect)
        
        easy_text = self.font.render("1. 简单", True, GREEN if self.difficulty == "简单" else BLACK)
        easy_rect = easy_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(easy_text, easy_rect)
        
        medium_text = self.font.render("2. 中等", True, BLUE if self.difficulty == "中等" else BLACK)
        medium_rect = medium_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(medium_text, medium_rect)
        
        hard_text = self.font.render("3. 困难", True, RED if self.difficulty == "困难" else BLACK)
        hard_rect = hard_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        self.screen.blit(hard_text, hard_rect)
        
        # 开始提示
        start_text = self.font.render("按回车键开始游戏", True, BLACK)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4))
        self.screen.blit(start_text, start_rect)
    
    def render_game(self):
        # 绘制网格
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))
        
        # 绘制游戏元素
        self.snake.render(self.screen)
        self.food.render(self.screen)
        for obstacle in self.obstacles:
            obstacle.render(self.screen)
        
        # 显示游戏信息
        score_text = self.font.render(f"得分: {self.snake.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        difficulty_text = self.font.render(f"难度: {self.difficulty}", True, BLACK)
        self.screen.blit(difficulty_text, (10, 40))
        
        controls_text = self.font.render("方向键: 移动 | P: 暂停", True, BLACK)
        self.screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 10, 10))
    
    def render_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.big_font.render("游戏暂停", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        self.screen.blit(pause_text, pause_rect)
        
        continue_text = self.font.render("按P键继续游戏", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
        self.screen.blit(continue_text, continue_rect)
    
    def render_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        game_over = self.big_font.render("游戏结束!", True, RED)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(game_over, game_over_rect)
        
        score = self.font.render(f"最终得分: {self.snake.score}", True, WHITE)
        score_rect = score.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score, score_rect)
        
        restart = self.font.render("按回车键返回主菜单", True, WHITE)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        self.screen.blit(restart, restart_rect)
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.game_speed)

if __name__ == "__main__":
    game = Game()
    game.run()