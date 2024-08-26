from stensor.nn.module import Module


class Sequential(Module):
    def __init__(self, *layers):
        super().__init__()
        self.layers = []
        for i, layer in enumerate(layers):
            setattr(self, 'l' + str(i), layer)
            self.layers.append(layer)

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


class ModuleList(Module):
    def __init__(self, modules=None):
        super().__init__()
        if modules is not None:
            for idx, module in enumerate(modules):
                self._submodules[str(idx)] = module

    def __bool__(self):
        return len(self._submodules) != 0

    def __len__(self):
        return len(self._submodules)

    def __iter__(self):
        return iter(self._submodules.values())

    def forward(self, *inputs):
        raise NotImplementedError


__all__=["Sequential", "ModuleList"]
