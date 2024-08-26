from stensor import Tensor
from stensor.ops import functional as F
import torch 
import numpy as np
import functools
np.random.seed(0)


def generate_function_testcase(function, torch_function, inputs_args, inputs_args_kwargs, torch_backword_input):
    print("=================compare forward:")
    inputs_args_stensor = [Tensor(x, requires_grad=True if np.issubdtype(x.dtype, np.floating) else False) if isinstance(x, np.ndarray) else x for x in inputs_args]
    out_stensor = function(*inputs_args_stensor, **inputs_args_kwargs)

    inputs_args_torch = [torch.tensor(x, requires_grad=True if np.issubdtype(x.dtype, np.floating) else False) if isinstance(x, np.ndarray) else x for x in inputs_args]
    out_torch = torch_function(*inputs_args_torch, **inputs_args_kwargs)
    for i, j in zip(inputs_args_stensor, inputs_args_torch):
        print("i: ", i)
        print("j: ", j)

    if isinstance(out_stensor, Tensor) and isinstance(out_torch, torch.Tensor):
        print("out_stensor: ", out_stensor.shape, out_stensor)
        print("out_torch: ", out_torch.shape, out_torch)
        np.testing.assert_allclose(out_stensor.data, out_torch.detach().numpy(), rtol=1e-3)
    else:
        assert len(out_stensor) == len(out_torch)
        print("out_stensor: ", out_stensor)
        print("out_torch: ", out_torch)
        for out_s, out_t in zip(out_stensor, out_torch):
            print("out_s: ", out_s.shape, out_s)
            print("out_t: ", out_t.shape, out_t)
            np.testing.assert_allclose(out_s.data, out_t.detach().numpy(), rtol=1e-3)

    print("=================compare backward:")
    print(torch_backword_input)
    if torch_backword_input != []:
        if isinstance(out_stensor, Tensor) and isinstance(out_torch, torch.Tensor):
            out_stensor.backward()
            torch_backword_input = [torch.tensor(x) for x in torch_backword_input]
            out_torch.backward(*torch_backword_input)
            for input_s, input_t in zip(inputs_args_stensor, inputs_args_torch):
                if isinstance(input_s, Tensor) and input_s.requires_grad:
                    print("input_s.grad: ", input_s.grad)
                    print("input_t.grad: ", input_t.grad)
                    np.testing.assert_allclose(input_s.grad.data, input_t.grad.numpy(), rtol=1e-3)
        else:
            for out_s, out_t in zip(out_stensor, out_torch):
                if isinstance(out_s, Tensor) and isinstance(out_t, torch.Tensor):
                    print("out_s: ", out_s.shape, out_s)
                    print("out_t: ", out_t.shape, out_t)
                    out_s.backward()
                    torch_backword_input = [torch.tensor(x) for x in torch_backword_input]
                    out_t.backward(*torch_backword_input)
                    for input_s, input_t in zip(inputs_args_stensor, inputs_args_torch):
                        if isinstance(input_s, Tensor) and input_s.requires_grad:
                            print("input_s.grad: ", input_s.grad)
                            print("input_t.grad: ", input_t.grad)
                            np.testing.assert_allclose(input_s.grad.data, input_t.grad.numpy(), rtol=1e-3)
                    
test_case_math_ops = [
    {
        "function": F.add,
        "torch_function": torch.add,
        "inputs_args": [((2, 3), np.float32), ((2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3), np.float32)]
    },
    {
        "function": F.add,
        "torch_function": torch.add,
        "inputs_args": [((1,), np.float32), ((2, 2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.sub,
        "torch_function": torch.sub,
        "inputs_args": [((2, 3), np.float32), ((2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3), np.float32)]
    },
    {
        "function": F.sub,
        "torch_function": torch.sub,
        "inputs_args": [((1,), np.float32), ((2, 2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.mul,
        "torch_function": torch.mul,
        "inputs_args": [((2, 3), np.float32), ((2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3), np.float32)]
    },
    {
        "function": F.mul,
        "torch_function": torch.mul,
        "inputs_args": [((1,), np.float32), ((2, 2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.div,
        "torch_function": torch.div,
        "inputs_args": [((2, 3), np.float32), ((2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3), np.float32)]
    },
    {
        "function": F.div,
        "torch_function": torch.div,
        "inputs_args": [((1,), np.float32), ((2, 2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.neg,
        "torch_function": torch.neg,
        "inputs_args": [((2, 2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.pow,
        "torch_function": torch.pow,
        "inputs_args": [((2, 2, 3), np.float32), (2,)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.sin,
        "torch_function": torch.sin,
        "inputs_args": [((2, 2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.cos,
        "torch_function": torch.cos,
        "inputs_args": [((2, 2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.tan,
        "torch_function": torch.tan,
        "inputs_args": [((2, 2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.exp,
        "torch_function": torch.exp,
        "inputs_args": [((2, 2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    #TODO: RuntimeWarning: invalid value encountered in log
    # {
    #     "function": F.log,
    #     "torch_function": torch.log,
    #     "inputs_args": [((2, 2, 3), np.float32)],
    #     "inputs_args_kwargs":{},
    #     "torch_backword_input": [((2, 2, 3), np.float32)]
    # },
    {
        "function": F.eq,
        "torch_function": torch.eq, 
        "inputs_args": [((2, 3, 4), np.float32),((2, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
    {
        "function": F.eq,
        "torch_function": torch.eq, 
        "inputs_args": [((2, 3, 4), np.float32),((1, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
    {
        "function": F.gt,
        "torch_function": torch.gt, 
        "inputs_args": [((2, 3, 4), np.float32),((2, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
    {
        "function": F.gt,
        "torch_function": torch.gt, 
        "inputs_args": [((2, 3, 4), np.float32),((1, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
    {
        "function": F.ge,
        "torch_function": torch.ge, 
        "inputs_args": [((2, 3, 4), np.float32),((2, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
    {
        "function": F.ge,
        "torch_function": torch.ge, 
        "inputs_args": [((2, 3, 4), np.float32),((1, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
    {
        "function": F.lt,
        "torch_function": torch.lt, 
        "inputs_args": [((2, 3, 4), np.float32),((2, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
    {
        "function": F.lt,
        "torch_function": torch.lt, 
        "inputs_args": [((2, 3, 4), np.float32),((1, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
        {
        "function": F.le,
        "torch_function": torch.le, 
        "inputs_args": [((2, 3, 4), np.float32),((2, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
    {
        "function": F.le,
        "torch_function": torch.le, 
        "inputs_args": [((2, 3, 4), np.float32),((1, 3, 4), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": []
    },
    {
        "function": F.matmul,
        "torch_function": torch.matmul, 
        "inputs_args": [((3, 4), np.float32),((4, 2), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((3, 2), np.float32)]
    },
    {
        "function": F.matmul,
        "torch_function": torch.matmul, 
        "inputs_args": [((2, 3, 4), np.float32),((4, 2), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3, 2), np.float32)]
    },
    {
        "function": F.matmul,
        "torch_function": torch.matmul, 
        "inputs_args": [((3, 4), np.float32),((2, 4, 2), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3, 2), np.float32)]
    },
    {
        "function": F.matmul,
        "torch_function": torch.matmul, 
        "inputs_args": [((2, 3, 4), np.float32),((2, 4, 5), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3, 5), np.float32)]
    },
    {
        "function": F.matmul,
        "torch_function": torch.matmul, 
        "inputs_args": [((2, 2, 3, 4), np.float32),((2, 4, 2), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3, 2), np.float32)]
    },
    {
        "function": F.matmul,
        "torch_function": torch.matmul, 
        "inputs_args": [((2, 3, 4), np.float32),((2, 2, 4, 2), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3, 2), np.float32)]
    },
    {
        "function": F.matmul,
        "torch_function": torch.matmul, 
        "inputs_args": [((2, 2, 3, 4), np.float32),((2, 2, 4, 5), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3, 5), np.float32)]
    }
]

test_case_common_ops = [
    {
        "function": F.broadcast_to,
        "torch_function": torch.broadcast_to, 
        "inputs_args": [((1, 3, 4), np.float32),((2, 3, 4),)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3, 4), np.float32)]
    },

    #TODO:
    # {
    #     "function": F.repeat,
    #     "torch_function": torch.Tensor.repeat, 
    #     "inputs_args": [((1, 2, 3), np.float32),((1, 3, 1),)],
    #     "inputs_args_kwargs":{},
    #     "torch_backword_input": [((1, 6, 3), np.float32)]
    # },
    {
        "function": F.reshape,
        "torch_function": torch.reshape,
        "inputs_args": [((2, 2, 3), np.float32), ((2, 3, 2),)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3, 2), np.float32)]
    },
    {
        "function": F.expand_dims,
        "torch_function": torch.Tensor.unsqueeze,
        "inputs_args": [((2, 3, 4), np.float32), (0,)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((1, 2, 3, 4), np.float32)]
    },
    {
        "function": F.unsqueeze,
        "torch_function": torch.unsqueeze,
        "inputs_args": [((2, 3, 4), np.float32), (0,)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((1, 2, 3, 4), np.float32)]
    },
    {
        "function": F.squeeze,
        "torch_function": torch.squeeze,
        "inputs_args": [((1, 2, 1, 4), np.float32),],
        "inputs_args_kwargs":{"dim":(0)},
        "torch_backword_input": [((2, 1, 4), np.float32)]
    },
    {
        "function": F.squeeze,
        "torch_function": torch.squeeze,
        "inputs_args": [((1, 2, 1, 4), np.float32),],
        "inputs_args_kwargs": {},
        "torch_backword_input": [((2, 4), np.float32)]
    },
    # {
    #     "function": F.flatten,
    #     "torch_function": torch.flatten, 
    #     "inputs_args": [((2, 3, 4), np.float32),],
    #     "inputs_args_kwargs":{"start_dim":1},
    #     "torch_backword_input": [((2, 12), np.float32)]
    # },
    {
        "function": F.flatten,
        "torch_function": torch.flatten, 
        "inputs_args": [((2, 3, 4), np.float32),],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((24,), np.float32)]
    },

    {
        "function": F.transpose,
        "torch_function": torch.transpose, 
        "inputs_args": [((2, 3, 4), np.float32),((0,)),((1,))],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((3, 2, 4), np.float32)]
    },
    {
        "function": F.masked_fill,
        "torch_function": torch.masked_fill, 
        "inputs_args": [((1, 2, 3), np.float32),((np.array([[[True, False, True],[False, True, True]]]),)),((1,))],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((1, 2, 3), np.float32)]
    },
    {
        "function": F.sum,
        "torch_function": torch.sum, 
        "inputs_args": [((2, 2, 3, 4), np.float32),((0,)),((True,))],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((1, 2, 3, 4), np.float32)]
    },
    {
        "function": F.sum,
        "torch_function": torch.sum, 
        "inputs_args": [((2, 2, 3, 4), np.float32),((0,)),((False,))],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3, 4), np.float32)]
    },
    {
        "function": F.sum,
        "torch_function": torch.sum, 
        "inputs_args": [((2, 2, 3, 4), np.float32),((-1,)),((True,))],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3, 1), np.float32)]
    },
    {
        "function": F.sum,
        "torch_function": torch.sum, 
        "inputs_args": [((2, 2, 3, 4), np.float32),((-1,)),((False,))],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3), np.float32)]
    },
    {
        "function": F.clip,
        "torch_function": torch.clip, 
        "inputs_args": [((2, 2, 3, 4), np.float32),((0.2,)),((0.8,))],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2, 3, 4), np.float32)]
    },
]

test_case_activation_ops = [
    {
        "function": F.sigmoid,
        "torch_function": torch.sigmoid, 
        "inputs_args": [((2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3), np.float32)]
    },
    {
        "function": F.relu,
        "torch_function": torch.relu, 
        "inputs_args": [((2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3), np.float32)]
    },
    {
        "function": F.leaky_relu,
        "torch_function": torch.nn.functional.leaky_relu, 
        "inputs_args": [((2, 3), np.float32), (0.2,)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3), np.float32)]
    },
    {
        "function": F.tanh,
        "torch_function": torch.tanh, 
        "inputs_args": [((2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3), np.float32)]
    },
    {
        "function": F.softmax,
        "torch_function": torch.softmax, 
        "inputs_args": [((2, 3), np.float32), (-1,)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 3), np.float32)]
    },
]


test_case_nn_ops = [
    {
        "function": F.linear,
        "torch_function": torch.nn.functional.linear, 
        "inputs_args": [((2, 3), np.float32), ((2, 3), np.float32)],
        "inputs_args_kwargs":{},
        "torch_backword_input": [((2, 2), np.float32)]
    },

]

test_case_lists = [test_case_math_ops, test_case_common_ops, test_case_activation_ops, test_case_nn_ops]

test_cases = functools.reduce(lambda x, y: x + y, test_case_lists)

def test_exec():
    for case in test_cases:
        f = case["function"]
        torch_function = case["torch_function"]
        print("########################## start to execute function test: ", f.__name__, " ##########################")
        inputs_args = case["inputs_args"]
        inputs_args = [np.random.normal(0.0, 1.0,(i[0])).astype(i[1]) if isinstance(i[0], tuple) and len(i) == 2 else i[0] for i in inputs_args ]
        inputs_args_kwargs = case["inputs_args_kwargs"]
        torch_backword_input = case["torch_backword_input"]
        torch_backword_input = [np.ones(i[0]).astype(i[1]) for i in torch_backword_input]   
        generate_function_testcase(f, torch_function, inputs_args, inputs_args_kwargs, torch_backword_input)


def test_function_max1():
    x = np.random.rand(2, 3, 4)
    x_s = Tensor(x, requires_grad=True)
    x_t = torch.tensor(x, requires_grad=True)
    value_s, indences_s = F.max(x_s, 0, False)
    value_t, indences_t = torch.max(x_t, 0, False)
    assert np.allclose(value_s.data, value_t.detach().numpy()), f"max test failed"
    assert np.allclose(indences_s.data, indences_t.detach().numpy()), f"max test failed" 

    value_s.backward()
    value_t.backward(torch.tensor((np.ones((3, 4)))))
    assert np.allclose(x_s.grad.data, x_t.grad.numpy()), f"max test backward failed"

    # indences_s.backward()
    # indences_t.backward(torch.tensor(np.ones((3, 4))))
    # assert np.allclose(x_s.grad.data, x_t.grad.numpy()), f"max test backward failed"

def test_function_max2():
    x = np.random.rand(2, 3, 4)
    x_s = Tensor(x, requires_grad=True)
    x_t = torch.tensor(x, requires_grad=True)
    value_s, indences_s = F.max(x_s, -1, True)
    value_t, indences_t = torch.max(x_t, -1, True)
    assert np.allclose(value_s.data, value_t.detach().numpy()), f"max test failed"
    assert np.allclose(indences_s.data, indences_t.detach().numpy()), f"max test failed" 

    value_s.backward()
    value_t.backward(torch.tensor((np.ones((2, 3, 1)))))
    assert np.allclose(x_s.grad.data, x_t.grad.numpy()), f"max test backward failed"


def test_function_min():
    x = np.random.rand(2, 3, 4)
    x_s = Tensor(x, requires_grad=True)
    x_t = torch.tensor(x, requires_grad=True)
    value_s, indences_s = F.min(x_s, 0, False)
    value_t, indences_t = torch.min(x_t, 0, False)
    assert np.allclose(value_s.data, value_t.detach().numpy()), f"min test failed"
    assert np.allclose(indences_s.data, indences_t.detach().numpy()), f"min test failed" 

    value_s.backward()
    value_t.backward(torch.tensor((np.ones((3, 4)))))
    assert np.allclose(x_s.grad.data, x_t.grad.numpy()), f"min test backward failed"


def test_function_getitem1():
    x = np.random.rand(2, 3, 4)
    x_s = Tensor(x, requires_grad=True)
    x_t = torch.tensor(x, requires_grad=True)
    value_s = F.get_item(x_s, 0)
    value_t = x_t[0]
    assert np.allclose(value_s.data, value_t.detach().numpy())

    value_s.backward()
    value_t.backward(torch.tensor((np.ones((3, 4)))))
    assert np.allclose(x_s.grad.data, x_t.grad.numpy())


def test_function_getitem2():
    x = np.random.rand(2, 3, 4)
    x_s = Tensor(x, requires_grad=True)
    x_t = torch.tensor(x, requires_grad=True)

    flat_ids = Tensor(np.array([1, 2, 3]))       #[8, 128] -> [8*128,]

    value_s = F.get_item(x_s, (slice(0,1,1),slice(0,1,1),slice(0,2,1)))
    value_t = x_t[0:1:1, 0:1:1, 0:2:1]
    print(value_s.shape)
    assert np.allclose(value_s.data, value_t.detach().numpy())

    value_s.backward()
    value_t.backward(torch.tensor((np.ones((1, 1, 2)))))
    print(x_s.grad)
    print(x_t.grad)
    assert np.allclose(x_s.grad.data, x_t.grad.numpy())


def test_function_softmax():
    x = np.random.rand(2, 3)
    x_s = Tensor(x, requires_grad=True)
    x_t = torch.tensor(x, requires_grad=True)      #[8, 128] -> [8*128,]

    value_s = F.softmax(x_s, -1)
    value_t = torch.nn.Softmax(-1)(x_t)
    print(value_s)
    assert np.allclose(value_s.data, value_t.detach().numpy())

    value_s.backward()
    value_t.backward(torch.tensor((np.ones((2,3)))))
    print(x_s.grad)
    print(x_t.grad)
    assert np.allclose(x_s.grad.data, x_t.grad.numpy())


def test_function_concat():
    x1 = np.random.rand(2, 3)
    x2 = np.random.rand(2, 3)
    x_s1 = Tensor(x1, requires_grad=True)
    x_t1 = torch.tensor(x1, requires_grad=True)      #[8, 128] -> [8*128,]
    x_s2 = Tensor(x2, requires_grad=True)
    x_t2 = torch.tensor(x2, requires_grad=True) 

    value_s = F.concat(x_s1, x_s2, axis=-1)
    value_t = torch.cat((x_t1, x_t2), -1)
    print(value_s)
    assert np.allclose(value_s.data, value_t.detach().numpy())

    value_s.backward()
    value_t.backward(torch.tensor((np.ones((2,6)))))
    print(x_s1.grad)
    print(x_t1.grad)
    assert np.allclose(x_s1.grad.data, x_t1.grad.numpy())
    print(x_s2.grad)
    print(x_t2.grad)
    assert np.allclose(x_s2.grad.data, x_t2.grad.numpy())

#TODO
# def test_function_dropout():  
#     x = np.random.rand(2, 3)
#     x_s = Tensor(x, requires_grad=True)
#     x_t = torch.tensor(x, requires_grad=True)      #[8, 128] -> [8*128,]

#     value_s = F.dropout(x_s, 0.1)
#     value_t = torch.dropout(0.1)(x_t)
#     print(value_s)
#     assert np.allclose(value_s.data, value_t.detach().numpy())

#     value_s.backward()
#     value_t.backward(torch.tensor((np.ones((2,3)))))
#     print(x_s.grad)
#     print(x_t.grad)
#     assert np.allclose(x_s.grad.data, x_t.grad.numpy())