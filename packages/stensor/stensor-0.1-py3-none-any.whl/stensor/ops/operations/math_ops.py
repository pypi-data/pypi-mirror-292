import numpy as np
from stensor.ops.primitive import Primitive
from stensor.ops.operations._impl import sum_to


class Add(Primitive):
    def forward(self, x0, x1):
        self.x0_shape, self.x1_shape = x0.shape, x1.shape
        y = x0 + x1
        return y

    def backward(self, gy):
        gx0, gx1 = gy, gy
        if self.x0_shape != self.x1_shape:
            gx0 = sum_to(gx0, self.x0_shape)
            gx1 = sum_to(gx1, self.x1_shape)
        return gx0, gx1 


class Sub(Primitive):
    def forward(self, x0, x1):
        self.x0_shape, self.x1_shape = x0.shape, x1.shape
        y = x0 - x1
        return y

    def backward(self, gy):
        gx0, gx1 = gy, -gy
        if self.x0_shape != self.x1_shape:
            gx0 = sum_to(gx0, self.x0_shape)
            gx1 = sum_to(gx1, self.x1_shape)
        return gx0, gx1 


class Mul(Primitive):
    def forward(self, x0, x1):
        self.x0_shape, self.x1_shape = x0.shape, x1.shape
        y = x0 * x1
        return y

    def backward(self, gy):
        gx0, gx1 = gy * self.xs[1], gy * self.xs[0]
        if self.x0_shape != self.x1_shape:
            gx0 = sum_to(gx0, self.x0_shape)
            gx1 = sum_to(gx1, self.x1_shape)
        return gx0, gx1


class Div(Primitive):
    def forward(self, x0, x1):
        self.x0_shape, self.x1_shape = x0.shape, x1.shape
        y = x0 / x1
        return y

    def backward(self, gy):
        gx0 = gy / self.xs[1]
        gx1 = gy * (-self.xs[0] / self.xs[1] ** 2)
        if self.x0_shape != self.x1_shape:
            gx0 = sum_to(gx0, self.x0_shape)
            gx1 = sum_to(gx1, self.x1_shape)
        return gx0, gx1


class Neg(Primitive):
    def forward(self, x):
        return -x

    def backward(self, gy):
        return -gy


class Pow(Primitive):
    def forward(self, x, exponent):
        y = x ** exponent
        return y

    def backward(self, gy):
        x, exponent = self.xs
        gx = exponent * x ** (exponent - 1) * gy
        return gx


class Sin(Primitive):
    def forward(self, x):
        y = np.sin(x)
        return y

    def backward(self, gy):
        gx = gy * (np.cos(self.xs[0]))
        return gx


class Cos(Primitive):
    def forward(self, x):
        y = np.cos(x)
        return y

    def backward(self, gy):
        gx = gy * (-np.sin(self.xs[0]))
        return gx


class Tan(Primitive):
    def forward(self, x):
        y = np.tan(x)
        return y

    def backward(self, gy):
        gx = gy /(np.cos(self.xs[0]) ** 2)
        return gx


class Exp(Primitive):
    def forward(self, x):
        y = np.exp(x)
        return y

    def backward(self, gy):
        gx = gy * self.ys[0]
        return gx


class Log(Primitive):
    def forward(self, x):
        y = np.log(x)
        return y

    def backward(self, gy):
        gx = gy / self.xs[0]
        return gx


class MatMul(Primitive):
    def forward(self, x1, x2):
        y = np.matmul(x1, x2)
        return y

    def backward(self, gy):
        x1, x2 = self.xs
        #only consider the dim of x or W less than 5.
        gx1 = np.matmul(gy, np.swapaxes(x2, -1, -2))
        if gx1.shape != x1.shape:
            gx1 = sum_to(gx1, x1.shape)

        gx2 = np.matmul(np.swapaxes(x1, -1, -2), gy)
        if gx2.shape != x2.shape:
            gx2 = sum_to(gx2, x2.shape)

        return gx1, gx2
