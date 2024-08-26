import sys
print(sys.path)
import functools
import numpy as np
from stensor.common.tensor import Tensor
from stensor.ops import functional as F

def numerical_diff(f, *input_x, eps=1e-4):
    res = []
    for i in range(len(input_x)):
        input_x_add_eps = []
        input_x_sub_eps = []
        for j, ele in enumerate(input_x):
            if i == j and isinstance(ele, Tensor):
                x0 = Tensor(ele.data - eps)
                input_x_sub_eps.append(x0)
                x1 = Tensor(ele.data + eps)
                input_x_add_eps.append(x1)
                print("add x0: ",x0)
                print("add x1: ",x1)
            else:
                input_x_sub_eps.append(ele)
                input_x_add_eps.append(ele)
                print("add other input ele: ",ele)

        y0 = f(*input_x_sub_eps)
        y1 = f(*input_x_add_eps)
       
        out = (y1.data - y0.data) / (2 * eps)
        res.append(out)
        print("numerical_grad: ", out)
        print(type(out))
    return res


def compare_func(input_x, f):
    for i, ele in enumerate(input_x):
        if not getattr(ele, "grad", None) is None and not ele.grad is None :
            out = ele.grad.data
            expect = numerical_diff(f, *input_x)[i]
            print("====================")
            print("out: ", out)
            print("expect: ", expect)
            print("====================")
            if out.shape == expect.shape:
                assert np.allclose(out, expect)
            # TODO: compare with different shape of grad.
            # else:
            #     assert np.equal(out, expect).all()
        


one_tensor_input = [Tensor(np.array(0.3))]

two_tensor_input = [Tensor(np.array(0.3)), Tensor(np.array(0.6))]

test_case_math_ops = [
    {
        "name": "add",
        "input_x": [Tensor(np.array(0.3)), Tensor(np.array(0.6))],
        "forward_func": F.add
    },
    {
        "name": "sub",
        "input_x": [Tensor(np.array(0.3)), Tensor(np.array(0.7))],
        "forward_func": F.sub
    },
    {
        "name": "mul",
        "input_x": [Tensor(np.array(0.3)), Tensor(np.array(0.6))],
        "forward_func": F.mul
    },
        {
        "name": "div",
        "input_x": [Tensor(np.array(0.3)), Tensor(np.array(0.6))],
        "forward_func": F.div
    },
        {
        "name": "neg",
        "input_x": [Tensor(np.array(0.3))],
        "forward_func": F.neg
    },
        {
        "name": "pow",
        "input_x": [Tensor(np.array(0.3)), Tensor(np.array(0.6))],
        "forward_func": F.pow
    },
        {
        "name": "sin",
        "input_x": [Tensor(np.array(1.07))],
        "forward_func": F.sin
    },
        {
        "name": "cos",
        "input_x": [Tensor(np.array(1.07))],
        "forward_func": F.cos
    },
        {
        "name": "tanh",
        "input_x": [Tensor(np.array(0.3))],
        "forward_func": F.tanh
    },
        {
        "name": "exp",
        "input_x": [Tensor(np.array(2))],
        "forward_func": F.exp
    },
        {
        "name": "log",
        "input_x": [Tensor(np.array(0.3))],
        "forward_func": F.log
    },
]

one_tensor_one_tuple_input = [Tensor(np.array([[0.1, 0.2],
                                               [0.3, 0.4]])),
                              (1, 4)]

test_case_common_ops = [
    {
        "name": "reshape",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]])),
                   (1, 4)],
        "forward_func": F.reshape
    },
    {
        "name": "expend_dims",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]])),
                   2],
        "forward_func": F.expand_dims
    },
    {
        "name": "flatten",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]]))
                   ],
        "forward_func": F.flatten
    },
    {
        "name": "sum",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]])),
                   0, True],
        "forward_func": F.sum
    },
    {
        "name": "sum_to",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]])),
                   (2, 1)],
        "forward_func": F.sum_to
    },
    {
        "name": "broadcast_to",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]])),
                   (2, 2, 2)],
        "forward_func": F.broadcast_to
    },
    #TODO: 
    # {
    #     "name": "matmul",
    #     "input_x": [Tensor(np.array([[0.1, 0.2],
    #                                  [0.3, 0.4]])),
    #                 Tensor(np.array([[0.5],
    #                                  [0.6]])),],
    #     "forward_func": F.matmul
    # },
    # {
    #     "name": "transpose",
    #     "input_x": [Tensor(np.array([[0.1, 0.2],
    #                                  [0.3, 0.4]]))],
    #     "forward_func": F.transpose
    # },
    {
        "name": "get_item",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]])),   
                    0],
        "forward_func": F.get_item
    },
    # {
    #     "name": "max",
    #     "input_x": [Tensor(np.array([[0.1, 0.2],
    #                                  [0.3, 0.4]])),   
    #                 1],
    #     "forward_func": F.max
    # },
    # {
    #     "name": "min",
    #     "input_x": [Tensor(np.array([[0.1, 0.2],
    #                                  [0.3, 0.4]])),   
    #                 0],
    #     "forward_func": F.min
    # },
    {
        "name": "clip",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]])),   
                    0.19, 0.31],
        "forward_func": F.clip
    },
]

test_case_activation_ops = [
    {
        "name": "sigmoid",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]]))],
        "forward_func": F.sigmoid
    },
    {
        "name": "relu",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]]))],
        "forward_func": F.relu
    },
    {
        "name": "softmax",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]]))],
        "forward_func": F.softmax
    },
    #TODO:
    # {
    #     "name": "log_softmax",
    #     "input_x": [Tensor(np.array([[0.1, 0.2],
    #                                  [0.3, 0.4]]))],
    #     "forward_func": F.log_softmax
    # },
    {
        "name": "leaky_relu",
        "input_x": [Tensor(np.array([[0.1, 0.2],
                                     [0.3, 0.4]]))],
        "forward_func": F.leaky_relu
    },
]

test_case_nn_ops = [
    # {
    #     "name": "dropout",
    #     "input_x": [Tensor(np.array([[10.1, 10.2],
    #                                  [10.3, 10.4]]))],
    #     "forward_func": F.dropout
    # },
    # {
    #     "name": "batch_norm",
    #     "input_x": [Tensor(np.ones([2, 2])),
    #                 Tensor(np.ones([2])),
    #                 Tensor(np.ones([2])),
    #                 Tensor(np.ones([2])),
    #                 Tensor(np.ones([2]))],
    #     "forward_func": F.batch_norm
    # },
    {
        "name": "conv2d",
        "input_x": [Tensor(np.ones([2, 2, 2, 2])),
                    Tensor(np.ones([2, 2, 3, 3]))],
        "forward_func": F.conv2d
    },
    {
        "name": "deconv2d",
        "input_x": [Tensor(np.ones([2, 2, 2, 2])),
                    Tensor(np.ones([2, 2, 3, 3]))],
        "forward_func": F.deconv2d
    },
    {
        "name": "pooling",
        "input_x": [Tensor(np.ones([2, 2, 2, 2])),
                    1],
        "forward_func": F.pooling
    },
    {
        "name": "pooling",
        "input_x": [Tensor(np.ones([2, 2, 2, 2])),
                    1],
        "forward_func": F.average_pooling
    },
    {
        "name": "im2col",
        "input_x": [Tensor(np.ones([2, 2, 2, 2])),
                    1],
        "forward_func": F.im2col
    },
    {
        "name": "col2im",
        "input_x": [Tensor(np.ones([2, 2, 2, 2])),
                    (2, 2, 2, 2), 2],
        "forward_func": F.col2im
    },
]

test_case_lists = [test_case_math_ops, test_case_common_ops, test_case_activation_ops, test_case_nn_ops]

test_cases = functools.reduce(lambda x, y: x + y, test_case_lists)

def test_exec():
    for case in test_cases:
        #name = case["name"]
        input_x = case["input_x"]
        f = case["forward_func"]
        name = f.__name__
        print("start to execute operation test: ", name, "##########################")
        y =  f(*input_x)
        print("forward out: ", y)
        y.backward()
        compare_func(input_x, f)
