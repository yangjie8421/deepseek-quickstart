import pygame
import random
import time
import os
import sys

# 初始化pygame
pygame.init()

# 游戏配置
class Config:
    # 颜色定义
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    
    # 方块颜色
    COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, MAGENTA, RED]
    
    # 游戏区域设置
    GRID_WIDTH = 10  # 游戏区域宽度(列数)
    GRID_HEIGHT = 20  # 游戏区域高度(行数)
    CELL_SIZE = 30  # 每个方块的大小(像素)
    GAME_AREA_LEFT = 50  # 游戏区域左侧位置
    GAME_AREA_TOP = 50  # 游戏区域顶部位置
    
    # 侧边栏设置
    SIDEBAR_WIDTH = 200  # 侧边栏宽度
    SCREEN_WIDTH = GAME_AREA_LEFT * 2 + GRID_WIDTH * CELL_SIZE + SIDEBAR_WIDTH  # 屏幕宽度
    SCREEN_HEIGHT = GAME_AREA_TOP * 2 + GRID_HEIGHT * CELL_SIZE  # 屏幕高度
    
    # 游戏速度设置(毫秒)
    INITIAL_SPEED = 800  # 初始下落速度
    SPEED_INCREMENT = 50  # 每升一级速度增加量
    
    # 分数设置
    SCORE_TABLE = [100, 300, 500, 800]  # 消除1-4行的得分
    LEVEL_UP_LINES = 10  # 每消除多少行升一级
    
    # 字体设置
    FONT_SIZE = 24
    FONT_NAME = "simhei"  # 使用黑体显示中文

# 方块形状定义
class BlockShapes:
    # 7种方块形状，每种形状有4种旋转状态
    SHAPES = [
        # I形
        [[1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
        
        # J形
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],
        
        # L形
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],
        
        # O形
        [[1, 1],
         [1, 1]],
        
        # S形
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],
        
        # T形
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
        
        # Z形
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]]
    ]
    
    @classmethod
    def get_shape(cls, shape_idx):
        """获取指定形状的方块"""
        return cls.SHAPES[shape_idx]

# 方块类
class Block:
    def __init__(self, shape_idx, x=0, y=0):
        """初始化方块"""
        self.shape_idx = shape_idx
        self.color_idx = shape_idx
        self.x = x  # 方块在游戏区域中的x坐标
        self.y = y  # 方块在游戏区域中的y坐标
        self.rotation = 0  # 当前旋转状态(0-3)
        self.shape = BlockShapes.get_shape(shape_idx)
        self.color = Config.COLORS[shape_idx]
    
    def rotate(self):
        """旋转方块"""
        self.rotation = (self.rotation + 1) % 4
        # 旋转后的形状是原形状的转置矩阵
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
        
        self.shape = rotated
    
    def get_cells(self):
        """获取方块所占的所有单元格坐标"""
        cells = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    cells.append((self.x + x, self.y + y))
        return cells

# 游戏类
class TetrisGame:
    def __init__(self):
        """初始化游戏"""
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        
        # 加载字体(支持中文)
        try:
            self.font = pygame.font.SysFont(Config.FONT_NAME, Config.FONT_SIZE)
        except:
            self.font = pygame.font.Font(None, Config.FONT_SIZE)
        
        # 游戏状态
        self.grid = [[0 for _ in range(Config.GRID_WIDTH)] for _ in range(Config.GRID_HEIGHT)]
        self.current_block = None
        self.next_block = None
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.high_score = self.load_high_score()
        
        # 游戏计时
        self.last_drop_time = time.time()
        self.drop_speed = Config.INITIAL_SPEED
        
        # 生成第一个方块和下一个方块
        self.spawn_block()
    
    def load_high_score(self):
        """加载最高分"""
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    
    def save_high_score(self):
        """保存最高分"""
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))
    
    def spawn_block(self):
        """生成新方块"""
        if self.next_block is None:
            # 第一次生成方块
            shape_idx = random.randint(0, len(BlockShapes.SHAPES) - 1)
            self.current_block = Block(shape_idx, Config.GRID_WIDTH // 2 - 2, 0)
            
            # 生成下一个方块
            shape_idx = random.randint(0, len(BlockShapes.SHAPES) - 1)
            self.next_block = Block(shape_idx)
        else:
            # 使用之前生成的下一个方块
            self.current_block = self.next_block
            self.current_block.x = Config.GRID_WIDTH // 2 - len(self.next_block.shape[0]) // 2
            self.current_block.y = 0
            
            # 生成新的下一个方块
            shape_idx = random.randint(0, len(BlockShapes.SHAPES) - 1)
            self.next_block = Block(shape_idx)
        
        # 检查游戏是否结束
        if self.check_collision():
            self.game_over = True
    
    def check_collision(self, dx=0, dy=0, rotated_block=None):
        """
        检查碰撞
        :param dx: x方向移动量
        :param dy: y方向移动量
        :param rotated_block: 旋转后的方块(用于检查旋转是否合法)
        :return: 是否发生碰撞
        """
        block = rotated_block if rotated_block else self.current_block
        for x, y in block.get_cells():
            # 检查边界
            if (x + dx < 0 or x + dx >= Config.GRID_WIDTH or 
                y + dy >= Config.GRID_HEIGHT):
                return True
            
            # 检查是否与已有方块重叠
            if y + dy >= 0 and self.grid[y + dy][x + dx]:
                return True
        
        return False
    
    def move_block(self, dx, dy):
        """移动方块"""
        if not self.check_collision(dx, dy):
            self.current_block.x += dx
            self.current_block.y += dy
            return True
        return False
    
    def rotate_block(self):
        """旋转方块"""
        # 保存当前状态以便回滚
        old_rotation = self.current_block.rotation
        old_shape = [row[:] for row in self.current_block.shape]
        
        # 尝试旋转
        self.current_block.rotate()
        
        # 检查旋转后是否碰撞
        if self.check_collision():
            # 如果碰撞，尝试左右移动后再旋转(墙踢机制)
            kick_offsets = [0, -1, 1, -2, 2]  # 尝试的偏移量
            for offset in kick_offsets:
                if not self.check_collision(offset, 0):
                    self.current_block.x += offset
                    return True
            
            # 无法旋转，恢复原状
            self.current_block.rotation = old_rotation
            self.current_block.shape = old_shape
            return False
        
        return True
    
    def drop_block(self):
        """立即下落方块"""
        while not self.check_collision(0, 1):
            self.current_block.y += 1
    
    def lock_block(self):
        """锁定当前方块到游戏区域"""
        for x, y in self.current_block.get_cells():
            if y >= 0:
                self.grid[y][x] = self.current_block.color_idx + 1  # +1因为0表示空
    
    def clear_lines(self):
        """消除完整的行"""
        lines_to_clear = []
        
        # 找出所有完整的行
        for y in range(Config.GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        # 如果没有完整的行，直接返回
        if not lines_to_clear:
            return 0
        
        # 消除行并计分
        lines_cleared = len(lines_to_clear)
        self.score += Config.SCORE_TABLE[lines_cleared - 1] * self.level
        self.lines_cleared += lines_cleared
        
        # 更新等级
        new_level = self.lines_cleared // Config.LEVEL_UP_LINES + 1
        if new_level > self.level:
            self.level = new_level
            self.drop_speed = max(100, Config.INITIAL_SPEED - (self.level - 1) * Config.SPEED_INCREMENT)
        
        # 从下往上消除行
        for y in sorted(lines_to_clear, reverse=True):
            # 移除当前行
            del self.grid[y]
            # 在顶部添加新的空行
            self.grid.insert(0, [0 for _ in range(Config.GRID_WIDTH)])
        
        return lines_cleared
    
    def update(self):
        """更新游戏状态"""
        if self.game_over or self.paused:
            return
        
        current_time = time.time()
        
        # 自动下落
        if current_time - self.last_drop_time > self.drop_speed / 1000.0:
            if not self.move_block(0, 1):
                # 无法下落，锁定方块
                self.lock_block()
                lines_cleared = self.clear_lines()
                
                # 更新最高分
                if self.score > self.high_score:
                    self.high_score = self.score
                
                # 生成新方块
                self.spawn_block()
            
            self.last_drop_time = current_time
    
    def draw(self):
        """绘制游戏界面"""
        # 清空屏幕
        self.screen.fill(Config.BLACK)
        
        # 绘制游戏区域背景
        pygame.draw.rect(
            self.screen, Config.GRAY,
            (Config.GAME_AREA_LEFT - 2, Config.GAME_AREA_TOP - 2,
             Config.GRID_WIDTH * Config.CELL_SIZE + 4, Config.GRID_HEIGHT * Config.CELL_SIZE + 4),
            0
        )
        
        # 绘制网格线
        for x in range(Config.GRID_WIDTH):
            for y in range(Config.GRID_HEIGHT):
                pygame.draw.rect(
                    self.screen, Config.BLACK,
                    (Config.GAME_AREA_LEFT + x * Config.CELL_SIZE,
                     Config.GAME_AREA_TOP + y * Config.CELL_SIZE,
                     Config.CELL_SIZE - 1, Config.CELL_SIZE - 1),
                    1
                )
        
        # 绘制已锁定的方块
        for y in range(Config.GRID_HEIGHT):
            for x in range(Config.GRID_WIDTH):
                if self.grid[y][x]:
                    color = Config.COLORS[self.grid[y][x] - 1]
                    pygame.draw.rect(
                        self.screen, color,
                        (Config.GAME_AREA_LEFT + x * Config.CELL_SIZE,
                         Config.GAME_AREA_TOP + y * Config.CELL_SIZE,
                         Config.CELL_SIZE - 1, Config.CELL_SIZE - 1),
                        0
                    )
        
        # 绘制当前方块
        if self.current_block:
            for x, y in self.current_block.get_cells():
                if y >= 0:
                    pygame.draw.rect(
                        self.screen, self.current_block.color,
                        (Config.GAME_AREA_LEFT + x * Config.CELL_SIZE,
                         Config.GAME_AREA_TOP + y * Config.CELL_SIZE,
                         Config.CELL_SIZE - 1, Config.CELL_SIZE - 1),
                        0
                    )
        
        # 绘制侧边栏
        sidebar_left = Config.GAME_AREA_LEFT + Config.GRID_WIDTH * Config.CELL_SIZE + 20
        sidebar_top = Config.GAME_AREA_TOP
        
        # 绘制下一个方块预览
        next_text = self.font.render("下一个:", True, Config.WHITE)
        self.screen.blit(next_text, (sidebar_left, sidebar_top))
        
        if self.next_block:
            # 计算下一个方块的绘制位置(居中)
            block_width = len(self.next_block.shape[0]) * Config.CELL_SIZE
            block_height = len(self.next_block.shape) * Config.CELL_SIZE
            block_left = sidebar_left + (Config.SIDEBAR_WIDTH - block_width) // 2
            block_top = sidebar_top + 40
            
            # 绘制下一个方块
            for y, row in enumerate(self.next_block.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            self.screen, self.next_block.color,
                            (block_left + x * Config.CELL_SIZE,
                             block_top + y * Config.CELL_SIZE,
                             Config.CELL_SIZE - 1, Config.CELL_SIZE - 1),
                            0
                        )
        
        # 绘制分数
        score_text = self.font.render(f"分数: {self.score}", True, Config.WHITE)
        self.screen.blit(score_text, (sidebar_left, sidebar_top + 150))
        
        # 绘制等级
        level_text = self.font.render(f"等级: {self.level}", True, Config.WHITE)
        self.screen.blit(level_text, (sidebar_left, sidebar_top + 180))
        
        # 绘制最高分
        high_score_text = self.font.render(f"最高分: {self.high_score}", True, Config.WHITE)
        self.screen.blit(high_score_text, (sidebar_left, sidebar_top + 210))
        
        # 绘制消除行数
        lines_text = self.font.render(f"消除行: {self.lines_cleared}", True, Config.WHITE)
        self.screen.blit(lines_text, (sidebar_left, sidebar_top + 240))
        
        # 绘制控制提示
        controls = [
            "控制方式:",
            "← → : 左右移动",
            "↑ : 旋转",
            "↓ : 加速下落",
            "空格: 立即下落",
            "P : 暂停/继续",
            "ESC: 退出"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.font.render(text, True, Config.WHITE)
            self.screen.blit(control_text, (sidebar_left, sidebar_top + 300 + i * 30))
        
        # 绘制暂停状态
        if self.paused:
            pause_text = self.font.render("游戏暂停", True, Config.WHITE)
            text_rect = pause_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)
        
        # 绘制游戏结束状态
        if self.game_over:
            game_over_text = self.font.render("游戏结束!", True, Config.RED)
            restart_text = self.font.render("按R键重新开始", True, Config.WHITE)
            
            text_rect = game_over_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(game_over_text, text_rect)
            
            text_rect = restart_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(restart_text, text_rect)
        
        # 更新屏幕
        pygame.display.flip()
    
    def reset(self):
        """重置游戏"""
        self.grid = [[0 for _ in range(Config.GRID_WIDTH)] for _ in range(Config.GRID_HEIGHT)]
        self.current_block = None
        self.next_block = None
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.drop_speed = Config.INITIAL_SPEED
        self.last_drop_time = time.time()
        self.spawn_block()
    
    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
                    
                    if not self.game_over and not self.paused:
                        if event.key == pygame.K_LEFT:
                            self.move_block(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_block(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move_block(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate_block()
                        elif event.key == pygame.K_SPACE:
                            self.drop_block()
            
            # 更新游戏状态
            self.update()
            
            # 绘制游戏
            self.draw()
            
            # 控制帧率
            clock.tick(60)
        
        # 游戏结束，保存最高分
        self.save_high_score()
        pygame.quit()

# 主函数
def main():
    game = TetrisGame()
    game.run()

if __name__ == "__main__":
    main()