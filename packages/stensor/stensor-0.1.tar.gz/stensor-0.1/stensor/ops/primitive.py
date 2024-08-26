import numpy as np
import weakref
from stensor.common import Tensor, as_Tensor
from stensor.Config import Config


class Primitive:
    def __call__(self, *inputs):
        # Make sure that all operations' inputs is Tensor.
        inputs = [as_Tensor(x) for x in inputs]
        # Pull the real data to compute.
        xs = [x.data for x in inputs]

        ys = self.forward(*xs)  # Single op execution

        if not isinstance(ys, tuple):
            ys = (ys,)
        outputs = [as_Tensor(y) for y in ys]

        if Config.enable_backprop:
            self.generation = max([x.generation for x in inputs])
            for output in outputs:
                output.set_creator(self)
            self.inputs = inputs
            self.outputs = [weakref.ref(y) for y in outputs]
            self.xs = xs
            #self.ys = [weakref.ref(y) for y in ys]   
            # the output of P.softmax_cross_entropy is float which not have weakref
            self.ys = ys

        return outputs if len(outputs) > 1 else outputs[0]

    def forward(self, xs):
        raise NotImplementedError()

    def backward(self, gys):
        raise NotImplementedError()


__all__=["Primitive"]
