from math import *


def get_rotation_matrix(pitch, yaw, roll):
    pitch, yaw, roll = map(radians, [pitch, yaw, roll])
    # Pitch (X軸周りの回転)
    Rx = [
        [1, 0, 0],
        [0, cos(pitch), -sin(pitch)],
        [0, sin(pitch), cos(pitch)]
    ]

    # Yaw (Y軸周りの回転)
    Ry = [
        [cos(yaw), 0, sin(yaw)],
        [0, 1, 0],
        [-sin(yaw), 0, cos(yaw)]
    ]

    # Roll (Z軸周りの回転)
    Rz = [
        [cos(roll), -sin(roll), 0],
        [sin(roll), cos(roll), 0],
        [0, 0, 1]
    ]

    # Ry, Rz, Rxの順に行列を積算 (Rx xRz x Ry)
    R = matrix_multiply(Rx, matrix_multiply(Rz, Ry))
    return R


# 行列の積を計算する関数
def matrix_multiply(A, B):
    result = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                result[i][j] += A[i][k] * B[k][j]
    return result


def transform_point_by_rotation_matrix(point, R):
    x, y, z = point
    x_new = R[0][0] * x + R[0][1] * y + R[0][2] * z
    y_new = R[1][0] * x + R[1][1] * y + R[1][2] * z
    z_new = R[2][0] * x + R[2][1] * y + R[2][2] * z
    return x_new, y_new, z_new


def add_vectors(vector1, vector2):
    return [vector1[i] + vector2[i] for i in range(3)]


def transpose_3x3(matrix):
    return [
        [matrix[0][0], matrix[1][0], matrix[2][0]],
        [matrix[0][1], matrix[1][1], matrix[2][1]],
        [matrix[0][2], matrix[1][2], matrix[2][2]]
    ]
