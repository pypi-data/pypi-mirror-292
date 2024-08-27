from math import floor


def get_boxes_from_ply(ply_file):
    box_positions = set()
    with open(ply_file, 'r') as f:
        lines = f.read()
        lines = lines.replace('\r\n', '\n')
        lines = lines.strip()
        positions = [list(map(float, ln.split())) for ln in lines.split('\n') if is_included_six_numbers(ln)]

        number_of_faces = int(len(positions) / 4)
        for i in range(number_of_faces):
            vertex1 = positions[i * 4]
            vertex2 = positions[i * 4 + 1]
            vertex3 = positions[i * 4 + 2]
            vertex4 = positions[i * 4 + 3]  # no need
            x = min(vertex1[0], vertex2[0], vertex3[0])
            y = min(vertex1[1], vertex2[1], vertex3[1])
            z = min(vertex1[2], vertex2[2], vertex3[2])
            r = float(vertex1[3]) / 255
            g = float(vertex1[4]) / 255
            b = float(vertex1[5]) / 255
            alpha = 1

            # ボックスを置く方向を解析
            if vertex1[0] == vertex2[0] and vertex2[0] == vertex3[0]:  # y-z plane
                step = max(vertex1[1], vertex2[1], vertex3[1]) - y
                if vertex1[1] != vertex2[1]:
                    x -= step
            elif vertex1[1] == vertex2[1] and vertex2[1] == vertex3[1]:  # z-x plane
                step = max(vertex1[2], vertex2[2], vertex3[2]) - z
                if vertex1[2] != vertex2[2]:
                    y -= step
            else:  # x-y plane
                step = max(vertex1[0], vertex2[0], vertex3[0]) - x
                if vertex1[0] != vertex2[0]:
                    z -= step

            # minimum unit: 0.1
            position_x = floor(round(x * 10.0 / step) / 10.0)
            position_y = floor(round(y * 10.0 / step) / 10.0)
            position_z = floor(round(z * 10.0 / step) / 10.0)
            box_positions.add(
                (
                    position_x,
                    position_z,
                    -position_y,
                    r,
                    g,
                    b,
                    alpha
                )
            )

        return box_positions


def is_included_six_numbers(_line):
    line_list = _line.split()
    if len(line_list) != 6:
        return False
    for i in range(6):
        try:
            float(line_list[i])
        except ValueError:
            return False
    return True


if __name__ == '__main__':
    get_boxes_from_ply('piyo.ply')
