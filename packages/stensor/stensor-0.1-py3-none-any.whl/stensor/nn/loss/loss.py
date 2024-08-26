from stensor.nn.module import Module
from stensor.ops import functional as F


class MeanSquaredErrorLoss(Module):
    r"""
    Calculates the mean squared error between the predicted value and the label value.

    For simplicity, let :math:`x` and :math:`y` be 1-dimensional Tensor with length :math:`N`,
    the unreduced loss (i.e. with argument reduction set to 'none') of :math:`x` and :math:`y` is given as:

    .. math::
        \ell(x, y) = L = \{l_1,\dots,l_N\}^\top, \quad \text{with} \quad l_n = (x_n - y_n)^2.

    where :math:`N` is the batch size. If `reduction` is not ``'none'``, then:

    .. math::
        \ell(x, y) =
        \begin{cases}
            \operatorname{mean}(L), & \text{if reduction} = \text{'mean';}\\
            \operatorname{sum}(L),  & \text{if reduction} = \text{'sum'.}
        \end{cases}


    """
    def __init__(self):
        super().__init__()

    def __call__(self, x, t):
        return F.mean_squared_error(x, t)



class SoftmaxCrossEntropy(Module):
    r"""
    Computes softmax cross entropy between logits and labels.

    Measures the distribution error between the probabilities of the input (computed with softmax function) and the
    labels where the classes are mutually exclusive (only one class is positive) using cross entropy loss.

    Typical input into this function is unnormalized scores denoted as :math:`x` whose shape is :math:`(N, C)` ,
    and the corresponding targets.

    Typically, the input to this function is the fractional value of each category and the corresponding target value,
    and the input format is :math:`(N, C)` .

    For each instance :math:`x_i`, :math:`i` ranges from 0 to N-1, the loss is given as:

    .. math::
        \ell(x_i, c) = - \log\left(\frac{\exp(x_i[c])}{\sum_j \exp(x_i[j])}\right)
        =  -x_i[c] + \log\left(\sum_j \exp(x_i[j])\right)

    where :math:`x_i` is a 1D score Tensor, :math:`c` is the index of 1 in one-hot.

    Note:
        While the labels classes are mutually exclusive, i.e., only one class is positive in the labels, the predicted
        probabilities does not need to be exclusive. It is only required that the predicted probability distribution
        of entry is a valid one.

    """
    def __init__(self):
        super().__init__()

    def __call__(self, x, t):
        return F.softmax_cross_entropy(x, t)
