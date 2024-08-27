import datetime
from math import floor
import websocket

from .matrix_util import *


class Voxelamming:
    texture_names = ["grass", "stone", "dirt", "planks", "bricks"]
    model_names = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Sun",
                   "Moon", "ToyBiplane", "ToyCar", "Drummer", "Robot", "ToyRocket", "RocketToy1", "RocketToy2", "Skull"]

    def __init__(self, room_name):
        self.room_name = room_name
        self.is_allowed_matrix = 0
        self.saved_matrices = []
        self.node_transform = [0, 0, 0, 0, 0, 0]
        self.matrix_transform = [0, 0, 0, 0, 0, 0]
        self.frame_transforms = []
        self.global_animation = [0, 0, 0, 0, 0, 0, 1, 0]
        self.animation = [0, 0, 0, 0, 0, 0, 1, 0]
        self.boxes = []
        self.frames = []
        self.sentences = []
        self.lights = []
        self.commands = []
        self.models = []
        self.model_moves = []
        self.sprites = []
        self.sprite_moves = []
        self.game_score = -1
        self.game_screen = []  # width, height, angle=90, red=1, green=1, blue=1, alpha=0.5
        self.size = 1
        self.shape = 'box'
        self.is_metallic = 0
        self.roughness = 0.5
        self.is_allowed_float = 0
        self.build_interval = 0.01
        self.is_framing = False
        self.frame_id = 0
        self.rotation_styles = {}  # 回転の制御（送信しない）
        self.websocket = None

    def clear_data(self):
        self.is_allowed_matrix = 0
        self.saved_matrices = []
        self.node_transform = [0, 0, 0, 0, 0, 0]
        self.matrix_transform = [0, 0, 0, 0, 0, 0]
        self.frame_transforms = []
        self.global_animation = [0, 0, 0, 0, 0, 0, 1, 0]
        self.animation = [0, 0, 0, 0, 0, 0, 1, 0]
        self.boxes = []
        self.frames = []
        self.sentences = []
        self.lights = []
        self.commands = []
        self.models = []
        self.model_moves = []
        self.sprites = []
        self.sprite_moves = []
        self.game_score = -1
        self.game_screen = []
        self.size = 1
        self.shape = 'box'
        self.is_metallic = 0
        self.roughness = 0.5
        self.is_allowed_float = 0
        self.build_interval = 0.01
        self.is_framing = False
        self.frame_id = 0
        self.rotation_styles = {}  # 回転の制御（送信しない）

    def set_frame_fps(self, fps=2):
        self.commands.append(f'fps {fps}')

    def set_frame_repeats(self, repeats=10):
        self.commands.append(f'repeats {repeats}')

    def frame_in(self):
        self.is_framing = True

    def frame_out(self):
        self.is_framing = False
        self.frame_id += 1

    def push_matrix(self):
        self.is_allowed_matrix += 1
        self.saved_matrices.append(self.matrix_transform)

    def pop_matrix(self):
        self.is_allowed_matrix -= 1
        self.matrix_transform = self.saved_matrices.pop()

    def transform(self, x, y, z, pitch=0, yaw=0, roll=0):
        if self.is_allowed_matrix:
            # 移動用のマトリックスを計算する
            matrix = self.saved_matrices[-1]
            base_position = matrix[:3]

            if len(matrix) == 6:
                base_rotation_matrix = get_rotation_matrix(*matrix[3:])
            else:
                base_rotation_matrix = [
                    matrix[3:6],
                    matrix[6:9],
                    matrix[9:12]
                ]

            # 移動後の位置を計算する
            # 転置行列を使用
            add_x, add_y, add_z = transform_point_by_rotation_matrix([x, y, z], transpose_3x3(base_rotation_matrix))
            print('add_x, add_y, add_z: ', add_x, add_y, add_z)
            x, y, z = add_vectors(base_position, [add_x, add_y, add_z])
            x, y, z = self.round_numbers([x, y, z])

            # 移動後の回転を計算する
            transform_rotation_matrix = get_rotation_matrix(-pitch, -yaw, -roll)  # 逆回転
            rotate_matrix = matrix_multiply(transform_rotation_matrix, base_rotation_matrix)

            self.matrix_transform = [x, y, z, *rotate_matrix[0], *rotate_matrix[1], *rotate_matrix[2]]
        else:
            x, y, z = self.round_numbers([x, y, z])

            if self.is_framing:
                self.frame_transforms.append([x, y, z, pitch, yaw, roll, self.frame_id])
            else:
                self.node_transform = [x, y, z, pitch, yaw, roll]

    def create_box(self, x, y, z, r=1, g=1, b=1, alpha=1, texture=''):
        if self.is_allowed_matrix:
            # 移動用のマトリックスにより位置を計算する
            matrix_transform = self.matrix_transform
            base_position = matrix_transform[:3]

            if len(matrix_transform) == 6:
                base_rotation_matrix = get_rotation_matrix(*matrix_transform[3:])
            else:
                base_rotation_matrix = [
                    matrix_transform[3:6],
                    matrix_transform[6:9],
                    matrix_transform[9:12]
                ]

            # 移動後の位置を計算する
            # 転置行列を使用
            add_x, add_y, add_z = transform_point_by_rotation_matrix([x, y, z], transpose_3x3(base_rotation_matrix))
            x, y, z = add_vectors(base_position, [add_x, add_y, add_z])

        x, y, z = self.round_numbers([x, y, z])
        r, g, b, alpha = self.round_two_decimals([r, g, b, alpha])

        # 重ねておくことを防止
        self.remove_box(x, y, z)
        if texture not in self.texture_names:
            texture_id = -1
        else:
            texture_id = self.texture_names.index(texture)

        if self.is_framing:
            self.frames.append([x, y, z, r, g, b, alpha, texture_id, self.frame_id])
        else:
            self.boxes.append([x, y, z, r, g, b, alpha, texture_id])

    def remove_box(self, x, y, z):
        x, y, z = self.round_numbers([x, y, z])

        if self.is_framing:
            for box in self.frames:
                if box[0] == x and box[1] == y and box[2] == z and box[8] == self.frame_id:
                    self.frames.remove(box)
        else:
            for box in self.boxes:
                if box[0] == x and box[1] == y and box[2] == z:
                    self.boxes.remove(box)

    def animate_global(self, x, y, z, pitch=0, yaw=0, roll=0, scale=1, interval=10):
        x, y, z = self.round_numbers([x, y, z])
        self.global_animation = [x, y, z, pitch, yaw, roll, scale, interval]

    def animate(self, x, y, z, pitch=0, yaw=0, roll=0, scale=1, interval=10):
        x, y, z = self.round_numbers([x, y, z])
        self.animation = [x, y, z, pitch, yaw, roll, scale, interval]

    def set_box_size(self, box_size):
        self.size = box_size

    def set_build_interval(self, interval):
        self.build_interval = interval

    def write_sentence(self, sentence, x, y, z, r=1, g=1, b=1, alpha=1, font_size=16, is_fixed_width=False):
        x, y, z = self.round_numbers([x, y, z])
        r, g, b, alpha = self.round_two_decimals([r, g, b, alpha])
        x, y, z = map(str, [x, y, z])
        r, g, b, alpha, font_size = map(str, [r, g, b, alpha, font_size])
        is_fixed_width = "1" if is_fixed_width else "0"
        self.sentences.append([sentence, x, y, z, r, g, b, alpha, font_size, is_fixed_width])

    def set_light(self, x, y, z, r=1, g=1, b=1, alpha=1, intensity=1000, interval=1, light_type='point'):
        x, y, z = self.round_numbers([x, y, z])
        r, g, b, alpha = self.round_two_decimals([r, g, b, alpha])

        if light_type == 'point':
            light_type = 1
        elif light_type == 'spot':
            light_type = 2
        elif light_type == 'directional':
            light_type = 3
        else:
            light_type = 1
        self.lights.append([x, y, z, r, g, b, alpha, intensity, interval, light_type])

    def set_command(self, command):
        self.commands.append(command)

        if command == 'float':
            self.is_allowed_float = 1

    def draw_line(self, x1, y1, z1, x2, y2, z2, r=1, g=1, b=1, alpha=1):
        x1, y1, z1, x2, y2, z2 = map(floor, [x1, y1, z1, x2, y2, z2])
        diff_x = x2 - x1
        diff_y = y2 - y1
        diff_z = z2 - z1
        max_length = max(abs(diff_x), abs(diff_y), abs(diff_z))
        # print(x2, y2, z2)

        if diff_x == 0 and diff_y == 0 and diff_z == 0:
            return False

        if abs(diff_x) == max_length:
            if x2 > x1:
                for x in range(x1, x2 + 1):
                    y = y1 + (x - x1) * diff_y / diff_x
                    z = z1 + (x - x1) * diff_z / diff_x
                    self.create_box(x, y, z, r, g, b, alpha)
            else:
                for x in range(x1, x2 - 1, -1):
                    y = y1 + (x - x1) * diff_y / diff_x
                    z = z1 + (x - x1) * diff_z / diff_x
                    self.create_box(x, y, z, r, g, b, alpha)
        elif abs(diff_y) == max_length:
            if y2 > y1:
                for y in range(y1, y2 + 1):
                    x = x1 + (y - y1) * diff_x / diff_y
                    z = z1 + (y - y1) * diff_z / diff_y
                    self.create_box(x, y, z, r, g, b, alpha)
            else:
                for y in range(y1, y2 - 1, -1):
                    x = x1 + (y - y1) * diff_x / diff_y
                    z = z1 + (y - y1) * diff_z / diff_y
                    self.create_box(x, y, z, r, g, b, alpha)
        elif abs(diff_z) == max_length:
            if z2 > z1:
                for z in range(z1, z2 + 1):
                    x = x1 + (z - z1) * diff_x / diff_z
                    y = y1 + (z - z1) * diff_y / diff_z
                    self.create_box(x, y, z, r, g, b, alpha)
            else:
                for z in range(z1, z2 - 1, -1):
                    x = x1 + (z - z1) * diff_x / diff_z
                    y = y1 + (z - z1) * diff_y / diff_z
                    self.create_box(x, y, z, r, g, b, alpha)

    def change_shape(self, shape):
        self.shape = shape

    def change_material(self, is_metallic=False, roughness=0.5):
        if is_metallic:
            self.is_metallic = 1
        else:
            self.is_metallic = 0
        self.roughness = roughness

    def create_model(self, model_name, x=0, y=0, z=0, pitch=0, yaw=0, roll=0, scale=1, entity_name=''):
        if model_name in self.model_names:
            print(f'Find model name: {model_name}')
            x, y, z, pitch, yaw, roll, scale = self.round_two_decimals([x, y, z, pitch, yaw, roll, scale])
            x, y, z, pitch, yaw, roll, scale = map(str, [x, y, z, pitch, yaw, roll, scale])

            self.models.append([model_name, x, y, z, pitch, yaw, roll, scale, entity_name])
        else:
            print(f'No model name: {model_name}')

    def move_model(self, entity_name, x=0, y=0, z=0, pitch=0, yaw=0, roll=0, scale=1):
        x, y, z, pitch, yaw, roll, scale = self.round_two_decimals([x, y, z, pitch, yaw, roll, scale])
        x, y, z, pitch, yaw, roll, scale = map(str, [x, y, z, pitch, yaw, roll, scale])

        self.model_moves.append([entity_name, x, y, z, pitch, yaw, roll, scale])

    # Game API

    def set_game_screen(self, width, height, angle=90, r=1, g=1, b=0, alpha=0.5):
        self.game_screen = [width, height, angle, r, g, b, alpha]

    def set_game_score(self, score):
        self.game_score = float(score)

    def send_game_over(self):
        self.commands.append('gameOver')

    def set_rotation_style(self, sprite_name, rotation_style='all around'):
        self.rotation_styles[sprite_name] = rotation_style

    def create_sprite(self, sprite_name, color_list, x, y, direction=90, scale=1, visible=True):
        # 新しいスプライトデータを配列に追加
        x, y, direction = self.round_numbers([x, y, direction])
        x, y, direction, scale = map(str, [x, y, direction, scale])
        self.sprites.append([sprite_name, color_list, x, y, direction, scale, '1' if visible else '0'])

    def move_sprite(self, sprite_name, x, y, direction=90, scale=1, visible=True):
        # x, y, directionを丸める
        x, y, direction = self.round_numbers([x, y, direction])
        x, y, direction, scale = map(str, [x, y, direction, scale])

        # rotation_styleを取得
        if sprite_name in self.rotation_styles:
            rotation_style = self.rotation_styles[sprite_name]

            # rotation_styleが変更された場合、新しいスプライトデータを配列に追加
            if rotation_style == 'left-right':
                direction_mod = direction % 360  # 常に0から359の範囲で処理（常に正の数になる）
                if (direction_mod > 90 and direction_mod < 270):
                    direction = "-180"  # -180は左右反転するようにボクセラミング側で実装されている
                else:
                    direction = "0"
            elif rotation_style == "don't rotate":
                direction = "0"
            else:
                direction = str(direction)
        else:
            # rotation_styleが設定されていない場合、そのままの値を使う
            direction = str(direction)

        # sprites配列から同じスプライト名の要素を削除
        self.sprite_moves = [sprite_info for sprite_info in self.sprite_moves if sprite_info[0] != sprite_name]

        # 新しいスプライトデータを配列に追加
        self.sprite_moves.append([sprite_name, x, y, direction, scale, '1' if visible else '0'])

    def send_data(self, name=''):
        print('Sending data...')
        now = datetime.datetime.now()
        data_to_send = f"""
        {{
        "nodeTransform": {self.node_transform},
        "frameTransforms": {self.frame_transforms},
        "globalAnimation": {self.global_animation},
        "animation": {self.animation},
        "boxes": {self.boxes},
        "frames": {self.frames},
        "sentences": {self.sentences},
        "lights": {self.lights},
        "commands": {self.commands},
        "models": {self.models},
        "modelMoves": {self.model_moves},
        "sprites": {self.sprites},
        "spriteMoves": {self.sprite_moves},
        "gameScore": {self.game_score},
        "gameScreen": {self.game_screen},
        "size": {self.size},
        "shape": "{self.shape}",
        "interval": {self.build_interval},
        "isMetallic": {self.is_metallic},
        "roughness": {self.roughness},
        "isAllowedFloat": {self.is_allowed_float},
        "name": "{name}",
        "date": "{now}"
        }}
        """.replace("'", '"')

        if self.websocket is None or not self.websocket.connected:
            # WebSocket接続を初期化
            self.websocket = websocket.WebSocket()
            self.websocket.connect('wss://websocket.voxelamming.com')
            self.websocket.send(self.room_name)
            print(f"Joined room: {self.room_name}")

        # WebSocketが接続中か確認
        if self.websocket.connected:
            self.websocket.send(data_to_send)
            print('Sent data:', data_to_send)

    # 明示的にWebsocket接続を閉じる（必要な場合のみ）
    def close_connection(self):
        if self.websocket is not None:
            print('Closing WebSocket connection.')
            self.websocket.close()
            self.websocket = None

    def round_numbers(self, num_list):
        if self.is_allowed_float:
            return self.round_two_decimals(num_list)
        else:
            return list(map(floor, [round(val, 1) for val in num_list]))  # 修正

    @staticmethod
    def round_two_decimals(num_list):
        return [round(val, 2) for val in num_list]