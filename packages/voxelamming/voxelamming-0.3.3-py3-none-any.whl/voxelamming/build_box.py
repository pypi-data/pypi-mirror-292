import asyncio
import datetime
import re
from math import floor
import websockets

from matrix_util import *


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
        self.sentence = []
        self.lights = []
        self.commands = []
        self.models = []
        self.model_moves = []
        self.size = 1
        self.shape = 'box'
        self.is_metallic = 0
        self.roughness = 0.5
        self.is_allowed_float = 0
        self.build_interval = 0.01
        self.is_framing = False
        self.frame_id = 0

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
        self.sentence = []
        self.lights = []
        self.commands = []
        self.models = []
        self.model_moves = []
        self.size = 1
        self.shape = 'box'
        self.is_metallic = 0
        self.roughness = 0.5
        self.is_allowed_float = 0
        self.build_interval = 0.01
        self.is_framing = False
        self.frame_id = 0

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

    def write_sentence(self, sentence, x, y, z, r=1, g=1, b=1, alpha=1):
        x, y, z = self.round_numbers([x, y, z])
        r, g, b, alpha = self.round_two_decimals([r, g, b, alpha])
        x, y, z = map(str, [x, y, z])
        r, g, b, alpha = map(str, [r, g, b, alpha])
        self.sentence = [sentence, x, y, z, r, g, b, alpha]

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

    def send_data(self, name=''):
        print('send data')
        now = datetime.datetime.now()
        data_to_send = f"""
        {{
        "nodeTransform": {self.node_transform},
        "frameTransforms": {self.frame_transforms},
        "globalAnimation": {self.global_animation},
        "animation": {self.animation},
        "boxes": {self.boxes},
        "frames": {self.frames},
        "sentence": {self.sentence},
        "lights": {self.lights},
        "commands": {self.commands},
        "models": {self.models},
        "modelMoves": {self.model_moves},
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

        async def sender(room_name):
            async with websockets.connect('wss://websocket.voxelamming.com') as websocket:
                await websocket.send(room_name)
                await websocket.send(data_to_send)
                print(re.sub(r'\n    ', ' ', data_to_send.replace('"', '\\"')))

        # asyncio.runを使って非同期関数を実行する
        asyncio.run(sender(self.room_name))


    def round_numbers(self, num_list):
        if self.is_allowed_float:
            return self.round_two_decimals(num_list)
        else:
            return map(floor, [round(val, 1) for val in num_list])

    def round_two_decimals(self, num_list):
         return [round(val, 2) for val in num_list]
