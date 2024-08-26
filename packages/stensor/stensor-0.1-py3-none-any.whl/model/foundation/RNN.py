import numpy as np
from stensor.nn.module import  Module
from stensor.nn import layer as L
from stensor.common import Parameter
from stensor.ops import functional as F
from stensor.dataset.utils import get_file


# =============================================================================
# RNN
# =============================================================================
class RNN(Module):
    def __init__(self, hidden_size, out_size):
        super().__init__()
        self.rnn = L.RNN(hidden_size)
        self.fc = L.Linear(out_size)

    def reset_state(self):
        self.rnn.reset_state()
    
    def forward(self, x):
        h = self.rnn(x)
        y = self.fc(h)
        return y
