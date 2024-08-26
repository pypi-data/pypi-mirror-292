
from stensor.common import Tensor, as_Tensor, as_array


# =============================================================================
# utility function
# =============================================================================
def accuracy(y, t):
    """
    [WAR] This function is not differentiable.
    """
    y, t = as_Tensor(y), as_Tensor(t)

    pred = y.data.argmax(axis=1).reshape(t.shape)
    result = (pred == t.data)
    acc = result.mean()
    return Tensor(as_array(acc))


__all__=["accuracy"]