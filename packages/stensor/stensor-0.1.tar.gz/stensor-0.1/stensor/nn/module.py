import os
import weakref

from collections import OrderedDict
import numpy as np

from stensor.common.tensor import Parameter
from stensor.nn.utils import plot_dot_graph
from stensor.Config import no_grad


class Module:
    def __init__(self):
        self._parameters = OrderedDict()
        self._submodules = OrderedDict()
        self.training = True

    def __setattr__(self, name, value):
        if isinstance(value, Parameter):
            self._set_attr_for_parameter(name, value)
        elif isinstance(value, Module):
            self._set_attr_for_module(name, value)         
            
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in self._parameters:
            del self._parameters[name]
        elif name in self._submodules:
            del self._submodules[name]
        else:
            object.__delattr__(self, name)

    def __call__(self, *inputs):
        outputs = self.forward(*inputs)
        if not isinstance(outputs, tuple):
            outputs = (outputs,)
        self.inputs = [weakref.ref(x) for x in inputs]
        self.outputs = [weakref.ref(y) for y in outputs]
        return outputs if len(outputs) > 1 else outputs[0]


    def _set_attr_for_parameter(self, name, value):
        """Set attr for parameter."""
        submodules = self.__dict__.get('_submodules')
        params = self.__dict__.get('_parameters')
        if params is None:
            raise AttributeError("For 'Module', can not assign params before Module.__init__() is called.")
        if name in self.__dict__:
            if self.__dict__[name] is not None:
                raise TypeError(f"For 'Module', the {name} should not be Parameter.")
            del self.__dict__[name]
        if submodules and name in submodules:
            raise TypeError(f"For 'Module', the {name} must be Module, but got Parameter.")
        self.insert_param_to_module(name, value)


    def insert_param_to_module(self, param_name, param, check_name_contain_dot=True):
        """
        Adds a parameter to the current submodule.

        Args:
            param_name (str): Name of the parameter.
            param (Parameter): Parameter to be inserted to the submodule.
            check_name_contain_dot (bool): Determines whether the name input is compatible. Default: ``True`` .

        Raises:
            KeyError: If the name of parameter is null or contains dot.
            TypeError: If the type of parameter is not Parameter.
        """
        if not param_name:
            raise KeyError(f"For 'insert_param_to_module', the argument 'param_name' should not be None.")
        if check_name_contain_dot and '.' in param_name:
            raise KeyError(f"For 'insert_param_to_module', the argument 'param_name' should not contain'.' ")
        if '_parameters' not in self.__dict__:
            raise AttributeError(f"For 'insert_param_to_module', please call Module.__init__() firstly.")
        if hasattr(self, param_name) and param_name not in self._parameters:
            raise KeyError(f"For 'insert_param_to_module', the {param_name} parameter already exists in the network."
                           f"Cannot insert another parameter with the same name.")
        if not isinstance(param, Parameter) and param is not None:
            raise TypeError(f"For 'insert_param_to_module', the argument 'param' must be 'Parameter' if not None, "
                            f"but got {type(param)}.")
        self._parameters[param_name] = param


    def _set_attr_for_module(self, name, value):
        """Set attr for module."""
        submodules = self.__dict__.get('_submodules')
        params = self.__dict__.get('_parameters')
        if submodules is None:
            raise AttributeError("For 'Module', can not assign module before Module.__init__() is called.")
        if name in self.__dict__:
            del self.__dict__[name]
        if params and name in params:
            raise TypeError(f"For 'Module', the {name} must be Parameter, but got module.")
        submodules[name] = value


    def names_and_parameters(self, name_prefix='', expand=True):
        """
        Returns an iterator over submodule parameters.

        Includes the parameter's name and itself.

        Args:
            name_prefix (str): Namespace. Default: ``''`` .
            expand (bool): If true, yields parameters of this submodule and all subsubmodules. Otherwise, only yield parameters
                           that are direct members of this submodule. Default: ``True`` .

        Returns:
            Iteration, all the names and corresponding parameters in the submodules.

        """
        submodules = []
        if expand:
            submodules = self.names_and_submodules(name_prefix=name_prefix)
        else:
            submodules.append((name_prefix, self))

        params_set = set()
        for submodule_name, submodule in submodules:
            params = submodule._parameters.items()
            for par_name, par in params:
                # if par is not None and par.inited_param is not None:
                #     par = par.inited_param
                if par is not None and id(par) not in params_set:
                    params_set.add(id(par))
                    par_new_name = par_name
                    if submodule_name:
                        par_new_name = submodule_name + '.' + par_new_name

                    yield par_new_name, par


    def names_and_submodules(self, submodules=None, name_prefix=''):
        """
        Returns an iterator over all submodules in the network, including the submodule's name and itself.

        Args:
            submodules (str): submodules to iterate over. Default: ``None`` .
            name_prefix (str): Namespace. Default: ``''`` .

        Returns:
            Iteration, all the child submodules and corresponding names in the submodule.

        """
        t_submodules = submodules if submodules else set()
        if self in t_submodules:
            return

        t_submodules.add(self)
        yield name_prefix, self

        for name, submodule in self._submodules.items():
            if submodule:
                submodules_name_prefix = name
                if name_prefix:
                    submodules_name_prefix = name_prefix + '.' + submodules_name_prefix
                for ele in submodule.names_and_submodules(t_submodules, submodules_name_prefix):
                    yield ele


    def submodules(self, name_prefix='', expand=True):
        return [p for n, p in self.names_and_submodules(name_prefix)]


    def parameters(self, name_prefix='', expand=True):
        return [p for n, p in self.names_and_parameters(name_prefix, expand)]


    def current_name_and_submodules(self):
        """
        Returns an iterator over all immediate submodules in the network.

        Include name of the submodule and submodule itself.

        Returns:
            Dict, all the child submodules and corresponding names in the submodule.
        """
        value_set = set()
        submodules = OrderedDict()
        for name, submodule in self._submodules.items():
            if submodule is not None and submodule not in value_set:
                value_set.add(submodule)
                submodules[name] = submodule
        return submodules


    def current_submodules(self):
        """
        Returns an iterator over immediate submodules.

        Returns:
            Iteration, the immediate submodules in the submodule.

        """
        return self.current_name_and_submodules().values()


    def _apply(self, fn):
        for module in self._submodules().items():
            module._apply(fn)

        for key, param in self._parameters.items():
            if param is not None:
                # Tensors stored in modules are graph leaves, and we don't want to
                # track autograd history of `param_applied`, so we have to use
                # `with no_grad():`
                with no_grad():
                    param_applied = fn(param)
                    assert isinstance(param_applied, Parameter)
                    #assert param.is_leaf
                    self._parameters[key] = Parameter(param_applied, param.requires_grad)

            if param.grad is not None:
                with no_grad():
                    grad_applied = fn(param.grad)
                    assert isinstance(grad_applied, Parameter)
                    #assert param.grad.is_leaf
                    self._parameters[key].grad = grad_applied.requires_grad(param.grad.requires_grad)
        return self


    def type(self, dst_type):
        return self._apply(lambda t: t.data.astype(dst_type) if isinstance(t.data, np.ndarray) else t)


    def train(self, mode=True): 
        self.training = mode
        for module in self.current_submodules():
            module.train(mode)
        return self


    def eval(self):
        return self.train(False)


    def apply(self, fn):
        """
        Applies fn recursively to every submodules (as returned by .submodules()) as well as self.
        Typical use includes initializing the parameters of a model.

        Args:
            fn (function): function to be applied to each submodules.

        Returns:
            self.
        Example::
        >>> def init_weights(m):
        >>>     print(m)
        >>>     if type(m) == nn.Linear:
        >>>         m.weight.data.fill_(1.0)
        >>>         print(m.weight)
        >>> net = nn.Sequential(nn.Linear(2, 2), nn.Linear(2, 2))
        >>> net.apply(init_weights)
        """
        for submodule in self.current_submodules():
            submodule.apply(fn)
        fn(self)
        return self


    def forward(self, inputs):
        raise NotImplementedError()


    def cleargrads(self):
        for param in self.parameters():
            if param.grad is not None and param.requires_grad:
                param.cleargrad()


    def to_cpu(self):
        for param in self.parameters():
            param.to_cpu()


    def to_gpu(self):
        for param in self.parameters():
            param.to_gpu()


    def _flatten_params(self, params_dict, parent_key=""):
        for name, para in self.names_and_parameters():
            #print(name, para)
            key = parent_key + '/' + name if parent_key else name
            params_dict[key] = para


    def save_weights(self, path):
        self.to_cpu()

        params_dict = {}
        self._flatten_params(params_dict)
        array_dict = {key: param.data for key, param in params_dict.items()
                      if param is not None}
        try:
            np.savez_compressed(path, **array_dict)
        except (Exception, KeyboardInterrupt) as e:
            if os.path.exists(path):
                os.remove(path)
            raise


    def load_weights(self, path):
        npz = np.load(path)
        for name, para in self.names_and_parameters():
            para.data = npz[name]



    def plot(self, *inputs, to_file='model'):
        outputs = self.forward(*inputs)
        return plot_dot_graph(outputs, verbose=True, to_file=to_file)


__all__=["Module"]
