import torch.nn as nn


# model definition
class MLP(nn.Module):
    # define model elements
    def __init__(self, n_inputs, hidden_layer1, hidden_layer2, hidden_layer3):
        super(MLP, self).__init__()
        self.layer_1 = nn.Linear(n_inputs, hidden_layer1)
        self.drop1 = nn.Dropout(0.5)
        self.act1 = nn.PReLU()
        self.layer_2 = nn.Linear(hidden_layer1, hidden_layer2)
        self.drop2 = nn.Dropout(0.5)
        self.act2 = nn.PReLU()
        self.layer_3 = nn.Linear(hidden_layer2, hidden_layer3)
        self.drop3 = nn.Dropout(0.5)
        self.act3 = nn.PReLU()
        self.layer_4 = nn.Linear(hidden_layer3, 1)

    # forward propagate input
    def forward(self, x):
        x = self.act1(self.drop1(self.layer_1(x)))
        x = self.act2(self.drop2(self.layer_2(x)))
        x = self.act3(self.drop3(self.layer_3(x)))
        x = self.layer_4(x)
        return x


if __name__ == "__main__":
    import torch

    model = MLP(5, 128, 256, 128)

    x = torch.randn(5)
    x = model(x)
    print(x.shape)
