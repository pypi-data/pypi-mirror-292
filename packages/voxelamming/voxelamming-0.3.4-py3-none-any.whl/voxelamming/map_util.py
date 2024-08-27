import csv
from math import floor


def get_map_data_from_csv(csv_file, height_scale, column_num=257, row_num=257):
    # csvファイルから地図データを読み込み
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        # 標高データ
        heights = [floor(float(h) * height_scale) if h != '0' else -1 for h in next(reader)]
        # 高さによって色を変えるため、最大高さを求める
        max_height = floor(max(heights))
        print('max', max_height)
        # キューブの標高を２次元のリストに変換
        box_positions = [[heights[j + column_num * i] for j in range(column_num)] for i in range(row_num)]
        #       print(cube_positions[0])
        map_data = {'boxes': box_positions, 'maxHeight': max_height}

        return map_data


def get_box_color(height, max_height, high_color, low_color):
    # 高さによって色を変える
    r = (high_color[0] - low_color[0]) * height / max_height + low_color[0]
    g = (high_color[1] - low_color[1]) * height / max_height + low_color[1]
    b = (high_color[2] - low_color[2]) * height / max_height + low_color[2]

    return r, g, b


if __name__ == '__main__':
    CSV_FILE = '../map_file/map_38_138_100km.csv'
    HEIGHT_SCALE = 100
    get_map_data_from_csv(CSV_FILE, HEIGHT_SCALE)
