import numpy as np
import numbers
from stensor.Config import using_config
from stensor.common._register_for_tensor import tensor_operator_registry

try:
    import cupy
    array_types = (np.ndarray, cupy.ndarray)
except ImportError:
    array_types = (np.ndarray)

gpu_enable = True
try:
    import cupy as cp
    cupy = cp
except ImportError:
    gpu_enable = False


def as_Tensor(obj):
    if isinstance(obj, Tensor):
        return obj
    return Tensor(obj)


def as_array(x, array_module=np):
    if np.isscalar(x):
        return array_module.array(x)
    return x


def as_numpy(x):
    if isinstance(x, Tensor):
        x = x.data

    if np.isscalar(x):
        return np.array(x)
    elif isinstance(x, np.ndarray):
        return x
    return cp.asnumpy(x)


def as_cupy(x):
    if isinstance(x, Tensor):
        x = x.data

    if not gpu_enable:
        raise Exception('CuPy cannot be loaded. Install CuPy!')
    return cp.asarray(x)


class Tensor:
    __array_priority__ = 200

    def __init__(self, data, name=None, requires_grad=True):
        if data is not None:
            if isinstance(data,(list, tuple, numbers.Number)):
                data = np.array(data)
            elif isinstance(data, array_types):
                data = data
            elif isinstance(data, (Tensor, Parameter)):
                data = data.data
            else:
                raise TypeError('{} is not supported'.format(type(data)))

        self.data = data
        self.name = name
        self.grad = None
        self.creator = None
        self.generation = 0
        self.requires_grad = requires_grad


    @property
    def shape(self):
        return self.data.shape

    @property
    def ndim(self):
        return self.data.ndim

    @property
    def size(self):
        return self.data.size

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def T(self):
        if self.ndim != 2:
            raise ValueError("For operation 'T', the ndim of tensor must be 2, but got {}".format(self.ndim))
        return tensor_operator_registry.get('transpose')(self, 0, 1)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        if self.data is None:
            return 'Tensor(None)'
        p = str(self.data).replace('\n', '\n' + ' ' * 9)
        return 'Tensor(' + p + ')'

    def set_creator(self, func):
        self.creator = func
        self.generation = func.generation + 1

    def unchain(self):
        self.creator = None

    def cleargrad(self):
        self.grad = None

    def backward(self, dout=None, retain_grad=False, create_graph=False):
        for output in self.creator.outputs:
            if output().grad is None:
                output().grad = Tensor(np.ones_like(output().data))

        funcs = []
        seen_set = set()
        def add_func(f):
            if f not in seen_set:
                funcs.append(f)
                seen_set.add(f)
                funcs.sort(key=lambda x: x.generation)

        add_func(self.creator)
        while funcs:

            f = funcs.pop()
            # ALl outputs is Tensor.
            gys = [output().grad.data for output in f.outputs]  # output is weakref

            with using_config('enable_backprop', create_graph):
                gxs = f.backward(*gys)
                if not isinstance(gxs, tuple):
                    gxs = (gxs,)
                gxs = [as_Tensor(gx) for gx in gxs]
    
                for x, gx in zip(f.inputs, gxs):
                    # Only support Tensor gradient.
                    if not x.requires_grad:
                        continue

                    if x.grad is None:
                        x.grad = gx
                    else:
                        x.grad.data = x.grad.data + gx.data

                    if x.creator is not None:
                        add_func(x.creator)

            if not retain_grad:
                for y in f.outputs:
                    y().grad = None  # y is weakref

    def unchain_backward(self):
        if self.creator is not None:
            funcs = [self.creator]
            while funcs:
                f = funcs.pop()
                for x in f.inputs:
                    if x.creator is not None:
                        funcs.append(x.creator)
                        x.unchain()

    def __getitem__(self, index):
        out = tensor_operator_registry.get('__getitem__')(self, index)
        return out
    
    def __add__(self, other):
        out = tensor_operator_registry.get('__add__')(self, other)
        return out

    def __radd__(self, other):
        out = tensor_operator_registry.get('__radd__')(other, self)
        return out

    def __sub__(self, other):
        out = tensor_operator_registry.get('__sub__')(self, other)
        return out

    def __rsub__(self, other):
        out = tensor_operator_registry.get('__rsub__')(other, self)
        return out

    def __mul__(self, other):
        out = tensor_operator_registry.get('__mul__')(self, other)
        return out

    def __rmul__(self, other):
        out = tensor_operator_registry.get('__rmul__')(other, self)
        return out

    def __truediv__(self, other):   
        out = tensor_operator_registry.get('__div__')(self, other)
        return out

    def __rtruediv__(self, other):
        out = tensor_operator_registry.get('__rdiv__')(other, self)
        return out

    def __neg__(self):
        out = tensor_operator_registry.get('__neg__')(self)
        return out

    def __pow__(self, other):
        out = tensor_operator_registry.get('__pow__')(self, other)
        return out

    def __rpow__(self, other):
        out = tensor_operator_registry.get('__pow__')(other, self)
        return out

    def __eq__(self, x):
        return tensor_operator_registry.get('__eq__')(self, x)

    def __gt__(self, x):
        return tensor_operator_registry.get('__gt__')(self, x)

    def __ge__(self, x):
        return tensor_operator_registry.get('__ge__')(self, x)
    
    def __lt__(self, x):
        return tensor_operator_registry.get('__gt__')(self, x)

    def __le__(self, x):
        return tensor_operator_registry.get('__ge__')(self, x)

    def sin(self):
        return tensor_operator_registry.get('sin')(self)

    def cos(self):
        return tensor_operator_registry.get('cos')(self)
    
    def tan(self):
        return tensor_operator_registry.get('tan')(self)

    def exp(self):
        return tensor_operator_registry.get('tanh')(self)

    def log(self):
        return tensor_operator_registry.get('log')(self)

    def matmul(self, W):
        return tensor_operator_registry.get('matmul')(self, W)

    def sum_to(self, shape):
        return tensor_operator_registry.get('sum_to')(self, shape)

    def broadcast_to(self, shape):
        return tensor_operator_registry.get('broadcast_to')(self, shape)

    def repeat(self, shape):
        return tensor_operator_registry.get('repeat')(self, shape)

    def reshape(self, shape):
        return tensor_operator_registry.get('reshape')(self, shape)

    def view(self, *shape):
        return tensor_operator_registry.get('reshape')(self, shape)

    def transpose(self, dim0, dim1):
        return tensor_operator_registry.get('transpose')(self, dim0, dim1)

    def expand_dims(self, axis):
        return tensor_operator_registry.get('expand_dims')(self, axis)

    def unsqueeze(self, axis):
        return tensor_operator_registry.get('unsqueeze')(self, axis)

    def squeeze(self, axis):
        return tensor_operator_registry.get('squeeze')(self, axis)

    def flatten(self):
        return tensor_operator_registry.get('flatten')(self)

    def sum(self, axis=None, keepdims=False):
        return tensor_operator_registry.get('sum')(self, axis, keepdims)

    def max(self, axis=None, keepdims=False):
        return tensor_operator_registry.get('max')(self, axis, keepdims)

    def min(self, axis=None, keepdims=False):
        return tensor_operator_registry.get('min')(self, axis, keepdims)

    def get_item(self, slices):
        return tensor_operator_registry.get('get_item')(self, slices)

    def clip(self, x_min, x_max):
        return tensor_operator_registry.get('clip')(self,  x_min, x_max)

    def masked_fill(self, mask, value):
        return tensor_operator_registry.get('masked_fill')(self, mask, value)

    def concat(self, *tuple_tensor, axis=0):
        return tensor_operator_registry.get('concat')(self, tuple_tensor, axis)

    def sigmoid(self):
        return tensor_operator_registry.get('sigmoid')(self)

    def relu(self):
        return tensor_operator_registry.get('relu')(self)

    def leaky_relu(self, slope=0.2):
        return tensor_operator_registry.get('leaky_relu')(self, slope)
    
    def tanh(self):
        return tensor_operator_registry.get('tanh')(self)

    def softmax(self, axis=1):
        return tensor_operator_registry.get('softmax')(self, axis)

    def log_softmax(self, axis=1):
        return tensor_operator_registry.get('log_softmax')(self, axis)


    def astype(self, dtype):
        self.data = self.data.astype(dtype)
        return self


    def float(self):
        self.data = self.data.astype(np.float64)
        return self


    def int(self):
        self.data = self.data.astype(np.int64)
        return self


    def to_cpu(self):
        if self.data is not None:
            self.data = as_numpy(self.data)


    def to_gpu(self):
        if self.data is not None:
            self.data = as_cupy(self.data)


class Parameter(Tensor):
    def __init__(self, data, name=None, requires_grad=True):
        super().__init__(data, name=None)
        self.requires_grad = requires_grad
    
    def __repr__(self):
        if self.data is None:
            return 'Parameter(None)'
        p = str(self.data).replace('\n', '\n' + ' ' * 9)
        return 'Parameter(' + p + '), requires_grad: '+ str(self.requires_grad)


__all__ = ['Tensor', 'Parameter', 'as_Tensor', 'as_numpy', 'as_array',]
