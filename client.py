import pygame
from network import Network
from game import BlockType
from game import Keys
from game import GameState
import traceback # errors

screen_width = 500
screen_height = 500
window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bomber")
pygame.font.init()
font = pygame.font.Font(None, 36)


def draw_window(game_info, player_number):
    board = game_info[0]
    players = game_info[1]
    bombs = game_info[2]
    # list of tuples (bomb_rect, i, time)
    # trong đó i - chỉ số trong bảng, vị trí của khối mà quả bom được đặt
    game_state = game_info[3]

    # hiển thị trạng thái của game
    if game_state == GameState.WAITING:
        str = "Waiting for players"
    if game_state == GameState.STARTED:
        str = "Game started"
    if game_state == GameState.ENDED:
        str = "Game ended"
    window.fill((0, 0, 0))
    game_state_text = font.render(str, True, (255, 255, 255))
    window.blit(game_state_text, (80, 425))

    # hiển thị người chiến thắng
    if game_state == GameState.ENDED:
        winner_color = (0, 0, 0)
        for player_id, player in players.items():
            if player.isDead is False:
                winner_color = player.color
        pygame.draw.rect(window, winner_color, (100, 460, 20, 20))
        winner_text = font.render("Won", True, (255, 255, 255))
        window.blit(winner_text, (130, 460))

    # Vẽ các khối
    for block_rect, block_type in board:
        # Xác định màu của khối dựa trên loại của nó
        if block_type == BlockType.EMPTY:
            color = (255, 255, 255)  # white
        elif block_type == BlockType.WALL:
            color = (25, 25, 25)  # grey
        else:
            color = (75, 32, 0)

        # Vẽ khối
        pygame.draw.rect(window, color, block_rect)

    # Vẽ người chơi
    for player_id, player in players.items():
        if player.isDead is False:
            pygame.draw.rect(window, player.color, player.rect)

    # Vẽ boom
    for i in range(len(bombs)):
        pygame.draw.rect(window,(255, 165, 0), bombs[i][0] )

    pygame.display.flip()



def get_keys_pressed():
    keys = {}  # dictionary (Keys.key, isClicked)
    pygame_keys = pygame.key.get_pressed()
    keys[Keys.LEFT] = False
    keys[Keys.RIGHT] = False
    keys[Keys.UP] = False
    keys[Keys.DOWN] = False
    keys[Keys.SPACE] = False

    if pygame_keys[pygame.K_LEFT]:
        keys[Keys.LEFT] = True
    if pygame_keys[pygame.K_RIGHT]:
        keys[Keys.RIGHT] = True
    if pygame_keys[pygame.K_UP]:
        keys[Keys.UP] = True
    if pygame_keys[pygame.K_DOWN]:
        keys[Keys.DOWN] = True
    if pygame_keys[pygame.K_SPACE]:
        keys[Keys.SPACE] = True
    return keys

def run_game():
    clock = pygame.time.Clock()  # để duy trì khung hình / giây
    network = Network()  # tạo đối tượng Network để giao tiếp với máy chủ
    player_number = network.connect()


    # vòng lặp
    game_running = True
    while game_running:
        # dừng vòng lặp trò chơi trong khoảng thời gian cần thiết để
        # duy trì tốc độ khung hình 60 khung hình mỗi giây
        clock.tick(60)
        keys = get_keys_pressed()


        # client - server giao tiếp
        try:
             # sending and receiving (gửi và nhận thông tin)
            game_info = network.send(keys)  # send keys pressed, nhận thông tin trò chơi
        except:
            game_running = False
            print("Error: client-server communication")
            break

        # quiting game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                pygame.quit()
                break

        try:
            draw_window(game_info, player_number)
        except:
            print("drawing problem, disconnected")


run_game()
