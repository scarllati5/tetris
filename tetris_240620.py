import os
import sys
import pygame
import random
import time

# Pygame 초기화
pygame.init()
pygame.mixer.init()  # Pygame 믹서 초기화

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 소리 로드
block_place_sound = pygame.mixer.Sound(resource_path('block_place.wav'))
game_over_sound = pygame.mixer.Sound(resource_path('game_over.wav'))

# 배경 음악 로드
background_music_files = [
    resource_path('background_music.mp3'),
    resource_path('background_music02.mp3'),
    resource_path('background_music03.mp3'),
    resource_path('background_music04.mp3')
]

current_music_index = 0  # 현재 재생 중인 음악 인덱스

def play_next_background_music():
    global current_music_index
    pygame.mixer.music.load(background_music_files[current_music_index])
    pygame.mixer.music.play()
    current_music_index = (current_music_index + 1) % len(background_music_files)

def check_and_play_next_music():
    if not pygame.mixer.music.get_busy():  # 음악이 재생 중이 아니면
        play_next_background_music()

# 화면 크기 설정
game_screen_width = 400  # 게임 화면 너비
game_screen_height = 800  # 게임 화면 높이
score_board_width = 200  # 스코어 보드 너비
score_board_height = 800  # 스코어 보드 높이

# 전체 화면 설정
total_screen_width = game_screen_width + score_board_width
total_screen_height = game_screen_height

# 전체 화면 생성
screen = pygame.display.set_mode((total_screen_width, total_screen_height))
pygame.display.set_caption("Tetris with Scoreboard")

# 색상 정의
colors = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'L': (255, 165, 0),
    'J': (0, 0, 255),
    'T': (128, 0, 128),
    'shadow': (192, 192, 192)  # 그림자 블록의 색상 (더 어둡게 설정)
}

# 블록 모양 정의
shapes = [
    ('I', [[[1, 1, 1, 1]], [[1], [1], [1], [1]]]),
    ('O', [[[1, 1], [1, 1]]]),
    ('S', [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]]),
    ('Z', [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]]),
    ('L', [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]]),
    ('J', [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]]),
    ('T', [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]])
]

# 블록 크기 설정
block_size = 40  # 블록 크기

# 게임 보드의 열과 행 설정
columns = game_screen_width // block_size  # 열 개수
rows = game_screen_height // block_size  # 행 개수

# 게임 보드 초기화
board = [[0 for _ in range(columns)] for _ in range(rows)]

# 블록 클래스 정의
class Block:
    def __init__(self, shape):
        self.x = columns // 2 - 1
        self.y = 0
        self.shape_name, self.shape = shape
        self.color = colors[self.shape_name]
        self.rotation = 0

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)
        if check_collision(self):
            self.rotation = (self.rotation - 1) % len(self.shape)

def get_shadow_y(block, board):
    shadow_block = Block((block.shape_name, block.shape))
    shadow_block.x = block.x
    shadow_block.y = block.y
    shadow_block.rotation = block.rotation
    while not check_collision(shadow_block):
        shadow_block.y += 1
    shadow_block.y -= 1
    return shadow_block.y

def check_collision(block):
    shape = block.image()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if x + block.x < 0 or x + block.x >= columns or y + block.y >= rows or (y + block.y >= 0 and board[y + block.y][x + block.x]):
                    return True
    return False

def draw_board():
    for y in range(rows):
        for x in range(columns):
            color = board[y][x]
            if color:
                pygame.draw.rect(screen, colors[color], (x * block_size, y * block_size, block_size, block_size), 0)
            else:
                pygame.draw.rect(screen, (0, 0, 0), (x * block_size, y * block_size, block_size, block_size), 1)

def draw_block(block, offset_x=0, offset_y=0, scale=1):
    shape = block.image()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, block.color, ((block.x + x + offset_x) * block_size * scale, (block.y + y + offset_y) * block_size * scale, block_size * scale, block_size * scale), 0)

def draw_next_blocks(next_blocks):
    font = pygame.font.SysFont("System", 48)
    text_next = font.render("Next Block", True, (255, 255, 0))
    screen.blit(text_next, (game_screen_width + 10, 10))
    
    scale = 0.5
    start_x = game_screen_width + 20
    start_y = 80
    for i, block in enumerate(next_blocks):
        offset_x, offset_y = 0, start_y + i * 100
        shape = block.image()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, block.color, (start_x + x * block_size * scale, offset_y + y * block_size * scale, block_size * scale, block_size * scale), 0)

def draw_shadow(block, shadow_y):
    shape = block.image()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, colors['shadow'], ((block.x + x) * block_size, (shadow_y + y) * block_size, block_size, block_size), 0)

def merge_block(board, block):
    shape = block.image()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                board[y + block.y][x + block.x] = block.shape_name

def clear_lines(board):
    lines = 0
    for y in range(rows):
        if all(board[y]):
            del board[y]
            board.insert(0, [0 for _ in range(columns)])
            lines += 1
    return lines

def get_fall_speed(level):
    return max(100, 3000 - (level - 1) * 58)  # 레벨에 따른 속도 조절 (최소 100ms)

def draw_status_table(level, lines_cleared, score):
    pygame.draw.rect(screen, (0, 204, 255), (game_screen_width, 0, score_board_width, score_board_height))  # 흰색 배경
    font = pygame.font.SysFont("System", 48)  # 시스템 글꼴 사용
    text_level = font.render(f"Level: {level}", True, (255, 255, 0))
    text_lines = font.render(f"Lines: {lines_cleared}", True, (255, 255, 0))
    text_score = font.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(text_level, (game_screen_width + 20, 400))
    screen.blit(text_lines, (game_screen_width + 20, 500))
    screen.blit(text_score, (game_screen_width + 20, 600))

def calculate_score(lines_cleared, level):
    score = lines_cleared * 500 + (level - 1) * 5000
    return score

def draw_game_over(level, score, play_time):
    font = pygame.font.SysFont("System", 48)
    text1 = font.render("TOTAL SCORE", True, (255, 255, 255))
    text2 = font.render(f"Level: {level}", True, (255, 255, 255))
    text3 = font.render(f"Score: {score}", True, (255, 255, 255))
    text4 = font.render(f"Time: {play_time:.0f} seconds", True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(text1, (total_screen_width // 2 - text1.get_width() // 2, total_screen_height // 4))
    screen.blit(text2, (total_screen_width // 2 - text2.get_width() // 2, total_screen_height // 4 + 60))
    screen.blit(text3, (total_screen_width // 2 - text3.get_width() // 2, total_screen_height // 4 + 120))
    screen.blit(text4, (total_screen_width // 2 - text4.get_width() // 2, total_screen_height // 4 + 180))
    pygame.display.update()

class Button:
    def __init__(self, text, pos, size, font_size, bg_color, text_color, bold=False):
        self.text = text
        self.pos = pos
        self.size = size
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("NanumGothic", 35, bold=bold)
        self.rect = pygame.Rect(pos, size)

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def draw_game_over_screen(level, score, play_time):
    game_over_font = pygame.font.SysFont("Batang", 64, bold=True)
    font = pygame.font.SysFont("Batang", 35, bold=True)
    text1 = font.render("GAME OVER",40, True, (255, 0, 0))
    text2 = font.render(f"Level: {level}", True, (255, 255, 255))
    text3 = font.render(f"Score: {score}", True, (255, 255, 255))
    text4 = font.render(f"Time: {play_time:.2f} seconds", True, (255, 255, 255))
    
    restart_button = Button("CONTINUE", (total_screen_width // 2 - 80, total_screen_height // 2 + 150), (150, 40), 36, (0, 255, 0), (0, 0, 0))
    quit_button = Button("STOP", (total_screen_width // 2 - 80, total_screen_height // 2 + 200), (150, 40), 36, (255, 0, 0), (0, 0, 0))

    screen.fill((0, 0, 0))
    screen.blit(text1, (total_screen_width // 2 - text1.get_width() // 2, total_screen_height // 4))
    screen.blit(text2, (total_screen_width // 2 - text2.get_width() // 2, total_screen_height // 4 + 60))
    screen.blit(text3, (total_screen_width // 2 - text3.get_width() // 2, total_screen_height // 4 + 120))
    screen.blit(text4, (total_screen_width // 2 - text4.get_width() // 2, total_screen_height // 4 + 180))
    restart_button.draw(screen)
    quit_button.draw(screen)
    pygame.display.update()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_for_input = False
                return False  # 게임 종료
            if restart_button.is_clicked(event):
                return True
            if quit_button.is_clicked(event):
                return False

def game_loop():
    global game_over, level, lines_cleared, score, game_start_time, current_block, next_blocks, board

    clock = pygame.time.Clock()
    fall_time = 0
    move_time = 0  # 좌우 이동 시간을 위한 변수 추가
    initial_move_interval = 200  # 초기 좌우 이동 간격 (밀리초)
    continuous_move_interval = 50  # 지속적인 좌우 이동 간격 (밀리초)
    last_move_time = 0
    current_block = Block(random.choice(shapes))
    next_blocks = [Block(random.choice(shapes)) for _ in range(2)]
    game_over = False
    level = 1  # 초기 레벨 설정
    fall_speed = get_fall_speed(level)  # 초기 떨어지는 속도 설정
    level_start_time = pygame.time.get_ticks()  # 레벨 시작 시간
    lines_cleared = 0  # 초기 줄 제거 카운트
    score = 0  # 초기 점수
    game_start_time = time.time()  # 게임 시작 시간

    # 키 상태를 저장할 변수
    keys = {
        "left": False,
        "right": False,
        "down": False,
        "space": False  # 스페이스바 상태 추가
    }

    fall_speed_normal = get_fall_speed(level)  # 기본 떨어지는 속도
    fall_speed_fast = 50  # 다운키를 눌렀을 때의 빠른 속도 (50ms)
    fall_speed = fall_speed_normal

    move_direction = None  # 이동 방향 저장
    move_timer_started = False  # 이동 타이머 시작 여부

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    keys["left"] = True
                    move_direction = "left"
                    move_timer_started = False
                if event.key == pygame.K_RIGHT:
                    keys["right"] = True
                    move_direction = "right"
                    move_timer_started = False
                if event.key == pygame.K_DOWN:
                    keys["down"] = True
                    fall_speed = fall_speed_fast  # 다운키를 누르면 빠르게 떨어지도록
                if event.key == pygame.K_UP:
                    current_block.rotate()
                if event.key == pygame.K_SPACE:  # 스페이스바로 블록을 빠르게 내리기
                    while not check_collision(current_block):
                        current_block.y += 1
                    current_block.y -= 1
                    merge_block(board, current_block)
                    current_block = next_blocks.pop(0)
                    next_blocks.append(Block(random.choice(shapes)))
                    block_place_sound.play()  # 블록이 쌓일 때 소리 재생
                    if check_collision(current_block):
                        game_over = True
                    lines_cleared += clear_lines(board)  # 제거된 줄 수 업데이트
                    score = calculate_score(lines_cleared, level)  # 점수 업데이트
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    keys["left"] = False
                    move_direction = None
                    move_timer_started = False
                if event.key == pygame.K_RIGHT:
                    keys["right"] = False
                    move_direction = None
                    move_timer_started = False
                if event.key == pygame.K_DOWN:
                    keys["down"] = False
                    fall_speed = fall_speed_normal  # 다운키를 떼면 속도를 정상으로 되돌림
                if event.key == pygame.K_SPACE:
                    keys["space"] = False

        fall_time += clock.get_rawtime()
        move_time += clock.get_rawtime()
        clock.tick()

        # 좌우 이동 처리
        current_time = pygame.time.get_ticks()
        if move_direction:
            if not move_timer_started or current_time - last_move_time >= initial_move_interval:
                if keys[move_direction]:
                    if move_direction == "left":
                        current_block.x -= 1
                        if check_collision(current_block):
                            current_block.x += 1
                    if move_direction == "right":
                        current_block.x += 1
                        if check_collision(current_block):
                            current_block.x -= 1
                    last_move_time = current_time
                    move_timer_started = True
                if current_time - last_move_time >= continuous_move_interval:
                    if keys[move_direction]:
                        if move_direction == "left":
                            current_block.x -= 1
                            if check_collision(current_block):
                                current_block.x += 1
                        if move_direction == "right":
                            current_block.x += 1
                            if check_collision(current_block):
                                current_block.x -= 1
                        last_move_time = current_time

        if fall_time >= fall_speed:  # 블록 떨어지는 속도
            fall_time = 0
            current_block.y += 1
            if check_collision(current_block):
                current_block.y -= 1
                merge_block(board, current_block)
                current_block = next_blocks.pop(0)
                next_blocks.append(Block(random.choice(shapes)))
                block_place_sound.play()  # 블록이 쌓일 때 소리 재생
                if check_collision(current_block):
                    game_over = True
                lines_cleared += clear_lines(board)  # 제거된 줄 수 업데이트
                score = calculate_score(lines_cleared, level)  # 점수 업데이트

        # 레벨업 처리
        if pygame.time.get_ticks() - level_start_time >= 30000:  # 30초마다 레벨업
            level += 1
            fall_speed_normal = get_fall_speed(level)
            fall_speed = fall_speed_normal
            level_start_time = pygame.time.get_ticks()  # 레벨 시작 시간 초기화

        screen.fill((0, 0, 0))
        draw_status_table(level, lines_cleared, score)  # 상단 테이블 그리기
        draw_next_blocks(next_blocks)  # 다음 블록들 그리기
        draw_board()
        shadow_y = get_shadow_y(current_block, board)
        draw_shadow(current_block, shadow_y)  # 그림자 블록 그리기
        draw_block(current_block)
        pygame.display.update()

    # 게임 종료 후 결과 화면 표시
    play_time = time.time() - game_start_time
    draw_game_over(level, score, play_time)
    pygame.time.wait(0)  # 게임 오버 메시지를 2초 동안 표시 ->0초(현재)
    return draw_game_over_screen(level, score, play_time)

# 초기 배경 음악 재생
play_next_background_music()

# 메인 루프
running = True
while running:
    board = [[0 for _ in range(columns)] for _ in range(rows)]  # 게임 보드 초기화
    running = game_loop()
    check_and_play_next_music()  # 배경 음악 체크 및 재생

pygame.quit()
