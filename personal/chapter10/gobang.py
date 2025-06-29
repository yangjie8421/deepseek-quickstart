import pygame
import sys

class GomokuGame:
    def __init__(self):
        """初始化五子棋游戏"""
        pygame.init()
        pygame.font.init()
        
        # 游戏常量设置
        self.BOARD_SIZE = 15  # 15x15标准棋盘
        self.GRID_SIZE = 40   # 每个格子大小
        self.MARGIN = 50       # 棋盘边距
        self.PIECE_RADIUS = 18  # 棋子半径
        self.WIDTH = self.BOARD_SIZE * self.GRID_SIZE + 2 * self.MARGIN
        self.HEIGHT = self.BOARD_SIZE * self.GRID_SIZE + 2 * self.MARGIN + 60  # 底部留出空间放按钮和信息
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BOARD_COLOR = (220, 179, 92)  # 棋盘颜色(木质)
        self.LINE_COLOR = (0, 0, 0)        # 棋盘线颜色
        self.RED = (255, 0, 0)
        self.GRAY = (200, 200, 200)        # 按钮颜色
        self.BUTTON_HOVER = (180, 180, 180) # 按钮悬停颜色
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("五子棋")
        
        # 字体设置(使用中文黑体)
        self.font = pygame.font.SysFont('SimHei', 24)
        self.small_font = pygame.font.SysFont('SimHei', 18)
        
        # 游戏状态初始化
        self.reset_game()
    
    def reset_game(self):
        """重置游戏状态"""
        self.board = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]  # 棋盘状态
        self.current_player = "黑"  # 黑方先行
        self.game_over = False      # 游戏是否结束
        self.winner = None          # 获胜方
        self.move_history = []      # 落子历史(用于悔棋)
    
    def draw_board(self):
        """绘制棋盘和游戏界面"""
        # 绘制棋盘背景
        self.screen.fill(self.BOARD_COLOR)
        
        # 绘制网格线
        for i in range(self.BOARD_SIZE):
            # 横线
            pygame.draw.line(self.screen, self.LINE_COLOR, 
                            (self.MARGIN, self.MARGIN + i * self.GRID_SIZE), 
                            (self.WIDTH - self.MARGIN, self.MARGIN + i * self.GRID_SIZE), 2)
            # 竖线
            pygame.draw.line(self.screen, self.LINE_COLOR, 
                            (self.MARGIN + i * self.GRID_SIZE, self.MARGIN), 
                            (self.MARGIN + i * self.GRID_SIZE, self.HEIGHT - self.MARGIN - 60), 2)
        
        # 绘制棋子
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                if self.board[row][col] is not None:
                    color = self.BLACK if self.board[row][col] == "黑" else self.WHITE
                    pygame.draw.circle(self.screen, color, 
                                     (self.MARGIN + col * self.GRID_SIZE, 
                                      self.MARGIN + row * self.GRID_SIZE), 
                                     self.PIECE_RADIUS)
        
        # 绘制游戏信息
        if not self.game_over:
            info_text = f"当前回合: {self.current_player}方"
        else:
            info_text = f"游戏结束! {self.winner}方获胜!"
        
        text_surface = self.font.render(info_text, True, self.BLACK)
        self.screen.blit(text_surface, (self.MARGIN, self.HEIGHT - 50))
        
        # 绘制按钮
        mouse_pos = pygame.mouse.get_pos()
        
        # 悔棋按钮
        undo_button_rect = pygame.Rect(self.WIDTH - 180, self.HEIGHT - 50, 80, 30)
        undo_button_color = self.BUTTON_HOVER if undo_button_rect.collidepoint(mouse_pos) else self.GRAY
        pygame.draw.rect(self.screen, undo_button_color, undo_button_rect)
        undo_text = self.small_font.render("悔棋", True, self.BLACK)
        self.screen.blit(undo_text, (self.WIDTH - 160, self.HEIGHT - 45))
        
        # 重新开始按钮
        restart_button_rect = pygame.Rect(self.WIDTH - 90, self.HEIGHT - 50, 80, 30)
        restart_button_color = self.BUTTON_HOVER if restart_button_rect.collidepoint(mouse_pos) else self.GRAY
        pygame.draw.rect(self.screen, restart_button_color, restart_button_rect)
        restart_text = self.small_font.render("重新开始", True, self.BLACK)
        self.screen.blit(restart_text, (self.WIDTH - 80, self.HEIGHT - 45))
    
    def place_piece(self, row, col):
        """在指定位置放置棋子"""
        if self.board[row][col] is not None or self.game_over:
            return False
        
        # 放置棋子并记录历史
        self.board[row][col] = self.current_player
        self.move_history.append((row, col))
        
        # 检查是否获胜
        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        else:
            # 切换玩家
            self.current_player = "白" if self.current_player == "黑" else "黑"
        
        return True
    
    def check_win(self, row, col):
        """检查是否五子连珠"""
        directions = [
            [(0, 1), (0, -1)],  # 水平方向
            [(1, 0), (-1, 0)],  # 垂直方向
            [(1, 1), (-1, -1)],  # 主对角线方向
            [(1, -1), (-1, 1)]   # 副对角线方向
        ]
        
        for direction_pair in directions:
            count = 1  # 当前落子已经算1
            
            # 向两个相反方向检查相同颜色的棋子
            for dx, dy in direction_pair:
                x, y = row + dx, col + dy
                while 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE and self.board[x][y] == self.current_player:
                    count += 1
                    x += dx
                    y += dy
            
            # 如果任意方向有5个或更多连续棋子，则获胜
            if count >= 5:
                return True
        
        return False
    
    def undo_move(self):
        """悔棋一步"""
        if not self.move_history or self.game_over:
            return False
        
        # 从历史记录中移除最后一步
        row, col = self.move_history.pop()
        self.board[row][col] = None
        
        # 切换回上一个玩家
        self.current_player = "黑" if self.current_player == "白" else "黑"
        self.game_over = False
        self.winner = None
        
        return True
    
    def handle_click(self, pos):
        """处理鼠标点击事件"""
        x, y = pos
        
        # 检查是否点击了棋盘区域
        if self.MARGIN <= x < self.WIDTH - self.MARGIN and self.MARGIN <= y < self.HEIGHT - self.MARGIN - 60:
            # 计算点击的棋盘位置
            col = round((x - self.MARGIN) / self.GRID_SIZE)
            row = round((y - self.MARGIN) / self.GRID_SIZE)
            
            # 确保位置在棋盘范围内
            if 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE:
                self.place_piece(row, col)
        
        # 检查是否点击了悔棋按钮
        elif self.WIDTH - 180 <= x < self.WIDTH - 100 and self.HEIGHT - 50 <= y < self.HEIGHT - 20:
            self.undo_move()
        
        # 检查是否点击了重新开始按钮
        elif self.WIDTH - 90 <= x < self.WIDTH - 10 and self.HEIGHT - 50 <= y < self.HEIGHT - 20:
            self.reset_game()
    
    def run(self):
        """运行游戏主循环"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            # 绘制游戏界面
            self.draw_board()
            pygame.display.flip()

if __name__ == "__main__":
    game = GomokuGame()
    game.run()