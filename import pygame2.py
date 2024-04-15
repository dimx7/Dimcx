import pygame
import random


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)


colors = [
    (0, 0, 0),        # Background
    (255, 85, 85),    # Red
    (100, 200, 115),  # Green
    (120, 108, 245),  # Blue
    (255, 140, 50),   # Orange
    (50, 120, 52),    # Dark Green
    (146, 202, 73),   # Light Green
    (150, 161, 218)   # Purple
]


block_size = 30
feedback_messages = ["Well Done!", "Keep Going!", "You Got This!"]


shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]

def rotate_clockwise(shape):
    return [ [ shape[y][x]
            for y in range(len(shape)) ]
            for x in range(len(shape[0]) - 1, -1, -1) ]

class Tetris:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.game_over = False
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.new_piece()
        self.feedback_message = ""
        self.message_time = 0

    def new_piece(self):
        if not self.next_piece:
            self.next_piece = random.choice(shapes)
        self.current_piece = self.next_piece
        self.next_piece = random.choice(shapes)
        self.current_x = int(self.width / 2 - len(self.current_piece[0])/2)
        self.current_y = 0

        if self.check_collision(self.current_piece, (self.current_x, self.current_y)):
            self.game_over = True

    def check_collision(self, shape, offset):
        off_x, off_y = offset
        for cy, row in enumerate(shape):
            for cx, cell in enumerate(row):
                try:
                    if cell and self.board[cy + off_y][cx + off_x]:
                        return True
                except IndexError:
                    return True
        return False

    def move(self, delta_x):
        if not self.game_over:
            new_x = self.current_x + delta_x
            if not self.check_collision(self.current_piece, (new_x, self.current_y)):
                self.current_x = new_x

    def rotate(self):
        if not self.game_over:
            new_piece = rotate_clockwise(self.current_piece)
            if not self.check_collision(new_piece, (self.current_x, self.current_y)):
                self.current_piece = new_piece

    def drop(self):
        if not self.game_over:
            self.current_y += 1
            if self.check_collision(self.current_piece, (self.current_x, self.current_y)):
                self.current_y -= 1
                self.freeze()

    def freeze(self):
        for cy, row in enumerate(self.current_piece):
            for cx, cell in enumerate(row):
                if cell:
                    self.board[cy + self.current_y][cx + self.current_x] = cell
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        new_board = [row for row in self.board if 0 in row]
        cleared = len(self.board) - len(new_board)
        if cleared:
            self.board = [[0] * self.width for _ in range(cleared)] + new_board
            self.score += cleared ** 2
            self.feedback_message = random.choice(feedback_messages)
            self.message_time = pygame.time.get_ticks()

    def draw_feedback(self, screen):
        if self.feedback_message and pygame.time.get_ticks() - self.message_time < 2000:  
            font = pygame.font.Font(None, 36)
            text = font.render(self.feedback_message, True, WHITE)
            text_rect = text.get_rect(center=(self.width * block_size / 2, self.height * block_size / 2))
            screen.blit(text, text_rect)

    def draw_score(self, screen):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(text, (5, 5))  

    def draw_game_over(self, screen):
        if self.game_over:
            font = pygame.font.Font(None, 72)
            text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.width * block_size / 2, self.height * block_size / 2))
            screen.blit(text, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((block_size * 10, block_size * 20))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris(10, 20)

    
    DROP_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(DROP_EVENT, 1000)  

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move(1)
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_DOWN:
                    game.drop()
            elif event.type == DROP_EVENT:
                game.drop()  

        screen.fill(BLACK)
        
        for y, row in enumerate(game.board):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(screen, colors[val], (x * block_size, y * block_size, block_size, block_size), 0)

        
        for y, row in enumerate(game.current_piece):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(screen, colors[val], (x * block_size + game.current_x * block_size, y * block_size + game.current_y * block_size, block_size, block_size), 0)

        game.draw_feedback(screen)  
        game.draw_score(screen)  
        game.draw_game_over(screen)  
        pygame.display.flip()
        clock.tick(30)  

if __name__ == '__main__':
    main()

