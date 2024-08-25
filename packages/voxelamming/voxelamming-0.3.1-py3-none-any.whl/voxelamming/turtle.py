from math import sin, cos, radians


class Turtle:
    def __init__(self, voxelamming):
        self.voxelamming = voxelamming
        self.x = 0
        self.y = 0
        self.z = 0
        self.polar_theta = 90
        self.polar_phi = 0
        self.drawable = True
        self.color = [0, 0, 0, 1]
        self.size = 1

    def forward(self, length):
        z = self.z + length * sin(radians(self.polar_theta)) * cos(radians(self.polar_phi))
        x = self.x + length * sin(radians(self.polar_theta)) * sin(radians(self.polar_phi))
        y = self.y + length * cos(radians(self.polar_theta))
        x, y, z = round(x, 3), round(y, 3), round(z, 3)

        if self.drawable:
            self.voxelamming.draw_line(self.x, self.y, self.z, x, y, z, *self.color)

        self.x = x
        self.y = y
        self.z = z

    def backward(self, length):
        self.forward(-length)

    def up(self, degree):
        self.polar_theta -= degree

    def down(self, degree):
        self.polar_theta += degree

    def right(self, degree):
        self.polar_phi -= degree

    def left(self, degree):
        self.polar_phi += degree

    def set_color(self, r, g, b, alpha=1):
        self.color = [r, g, b, alpha]

    def pen_down(self):
        self.drawable = True

    def pen_up(self):
        self.drawable = False

    def set_pos(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def reset(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.polar_theta = 90
        self.polar_phi = 0
        self.drawable = True
        self.color = [0, 0, 0, 1]
        self.size = 1
