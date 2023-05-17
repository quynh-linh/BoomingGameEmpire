from player import Player
import pygame
from enum import Enum
import random
import time

# keys in keyboard
class Keys(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SPACE = 5
# các kiểu của khối có trong game
class BlockType(Enum):
    EMPTY = 1
    WALL = 2
    BLOWABLE = 3
    BOMB = 4
# trạng thái game
class GameState(Enum):
    WAITING = 1
    STARTED = 2
    ENDED = 3

class Game:
    def __init__(self, game_id):
        self.seconds_to_detonate = 3
        self.board_size = 20
        self.player_rect_size = 13
        self.bomb_rect_size = 6
        self.block_rect_size = 20
        self.game_state = GameState.WAITING
        self.game_id = game_id
        self.players = {}  # dictionary { player_number, player }
        # list of tuples (bomb_rect, i, time)
        # where i - index in board, position of block on which the bomb was planted
        # time - time of planting
        self.bombs = []
        self.player_colors = ((255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0))
        self.board = self.create_board()  # list of tuples (block_rect, block_type)

    # hàm đặt boom
    def plant_bomb(self, player_rect):
        bomb_rect  = pygame.Rect(0, 0, self.bomb_rect_size, self.bomb_rect_size)
        index = 0
        current_time = time.time()

        # Kiểm tra xem khối player_rect nằm ở bảng nào
        for i, (block_rect, block_type) in enumerate(self.board):
            if block_rect.colliderect(player_rect):
                # player_rect được chứa trong khối này
                index = i  # return chỉ mục của khối trong danh sách bảng
                bomb_rect.centerx = block_rect.centerx
                bomb_rect.centery = block_rect.centery

        self.bombs.append((bomb_rect, index, current_time))

    # hủy khối và cập nhập lại khối (kiểm tra người đã chết hay không)
    def destroy_surrounding_blocks(self, index):
        
        index_to_check = [index, index+1, index-1, index+self.board_size, index-self.board_size]
        for i in index_to_check:
            block = self.board[i]
            block_rect = block[0]
            type = block[1]
            if type == BlockType.BLOWABLE:
                self.board[i] = (block_rect, BlockType.EMPTY)

            for player_number, player in self.players.items():
                if block_rect.colliderect(player.rect):
                    player.isDead = True

    # check trạng thái của game
    def check_if_ended(self):
        # trạng thái chờ người chơi
        if self.game_state == GameState.WAITING:
            return
        # đếm player 
        alive_players = 0
        for player_number, player in self.players.items():
            if player.isDead is False:
                alive_players += 1
        # kết thúc game khi player nhỏ <=1
        if alive_players <= 1:
            self.game_state = GameState.ENDED

    # trạng thái của quả boom
    def activate_bombs(self):

        current_time = time.time()
        for bomb in self.bombs:
            bomb_time = bomb[2]
            # lấy thời gian hiện tại - thời gian đặt boom > thời gian khởi tạo
            # sau đó boom sẽ phát nổ
            if current_time - bomb_time > self.seconds_to_detonate:
                self.destroy_surrounding_blocks(bomb[1])
                # xóa quả boom đã phát nổ ra khỏi danh sách
                self.bombs.remove(bomb)

    # player move
    def react_to_keys(self, keys, player_number):
        if self.game_state == GameState.WAITING or self.game_state == GameState.ENDED:
            return
        try:
            player_rect = self.players[player_number].rect
            player_rect_copy = player_rect.copy()

            if keys[Keys.LEFT]:
                # velocity (Vận tốc di chuyển)
                player_rect_copy.x -= self.players[player_number].velocity
            if keys[Keys.RIGHT]:
                player_rect_copy.x += self.players[player_number].velocity
            if keys[Keys.UP]:
                player_rect_copy.y -= self.players[player_number].velocity
            if keys[Keys.DOWN]:
                player_rect_copy.y += self.players[player_number].velocity
            if keys[Keys.SPACE]:
                self.plant_bomb(player_rect)
            if (keys[Keys.LEFT] or keys[Keys.RIGHT] or keys[Keys.UP] or keys[Keys.DOWN]) is False:
                return

            collision = False

            # Kiểm tra khi người chơi di chuyển va chạm với tường or blowable
            for block_rect, block_type in self.board:
                # Kiểm tra WALL (tường) or Khối không
                if block_type == BlockType.WALL or block_type == BlockType.BLOWABLE:
                    # Kiểm tra người chơi có va chạm với khối không
                    if player_rect_copy.colliderect(block_rect):
                        # Không cho người chơi di chuyển
                        collision = True

            if collision is False:
                self.players[player_number].rect = player_rect_copy.copy()
        except:
            print("disconnected while reading keys")

    # returns về thông tin cho client to để vẽ lên màn hình của game
    def get_game_info(self):
        return self.board, self.players, self.bombs, self.game_state

    # hàm thêm người chơi
    def add_player(self, player_number):
        player_rect = pygame.Rect(0, 0, self.player_rect_size, self.player_rect_size)

        # Set up vị trí người trong 4 góc của màn hình
        if player_number == 0:
            index = self.board_size + 1 # góc trên trái màn hình
        if player_number == 1:
            index = 2 * self.board_size - 2 # góc trên phải màn hình
        if player_number == 2:
            index = self.board_size * (self.board_size - 2) + 1 # dưới trái góc màn hình
        if player_number == 3:
            index = (self.board_size-1) * self.board_size - 2 # dưới phải góc màn hình

        # căn giữa người chơi (hcn) trong hcn của màn hình
        player_rect.centerx = self.board[index][0].centerx
        player_rect.centery = self.board[index][0].centery

        # khởi tạo player mới 
        self.players[player_number] = Player(player_rect, self.player_colors[player_number], player_number)

    # hàm tạo bảng
    def create_board(self):
        pygame.init()
        board = self.randomize_board()  # danh sách bảng

        # Đặt cột và hàng đầu tiên và cuối cùng thành các khối tường
        for i in range(self.board_size):
            board[i] = (board[i][0], BlockType.WALL)
            board[(self.board_size - 1) * self.board_size + i] = (
            board[(self.board_size - 1) * self.board_size + i][0], BlockType.WALL)
            board[i * self.board_size] = (board[i * self.board_size][0], BlockType.WALL)
            board[(i + 1) * self.board_size - 1] = (board[(i + 1) * self.board_size - 1][0], BlockType.WALL)

        return board

    # random các khối xuất hiện ngẫu nhiên trên màn hình
    def randomize_board(self):
        # Xác định các loại khối có thể và xác suất của chúng
            # Các loại khối
        block_types = [BlockType.EMPTY, BlockType.WALL, BlockType.BLOWABLE]
            # Xác xuất xuất hiện của từng loại khối
        block_probabilities = [0.6, 0.1, 0.3]

        # Create the board as a list of tuples
        board = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                # Tạo một đối tượng rect Pygame cho hình chữ nhật hiện tại
                block_rect = pygame.Rect(col * self.block_rect_size, row * self.block_rect_size, self.block_rect_size, self.block_rect_size)

                # giữ góc trống
                if row in [0, 1, 2, self.board_size - 1, self.board_size - 2, self.board_size - 3] \
                        and col in [0, 1, 2, self.board_size - 1, self.board_size - 2, self.board_size - 3]:
                    block_type = BlockType.EMPTY
                else:
                    # Chọn loại khối ngẫu nhiên dựa trên xác suất đã xác định
                    block_type = random.choices(block_types, block_probabilities)[0]

                # Thêm hình chữ nhật hiện tại vào danh sách bảng dưới dạng một bộ (rect, is_traversable, color)
                board.append((block_rect, block_type))

        return board
