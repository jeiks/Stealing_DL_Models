#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#Author: Jacson R Correia-Silva <jacsonrcsilva@gmail.com>

''' Copycat CNN Method applied on a Simple Network:
    |x_00, x_01| -> [k0 k1] ->  |w_0|  -> ŷ = sign(.)
    |x_10, x_11|                |w_1| 
       Image        kernel     Weights (1 neuron)
       
    Examples:
    |1 0| = -1    |0 1| = 1
    |0 1|         |1 0|
    
Note: the network does NOT has biases, pooling, and dropout
'''
import torch
from torch import nn

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.conv = nn.Conv2d(1, 1,
                              kernel_size=(2, 1),
                              stride=(1, 1),
                              bias=False)
        self.linear = nn.Linear(2, 1, bias=False)
    
    def forward(self, x):
        x = self.conv(x)
        x = self.linear(x)
        return x
    
    def get_feature_map(self, x):
        return self.conv(x)
    
    def _print_list(self, l, d=8):
        for x in l.squeeze().tolist():
            print(f'{x:{d+3}.{d}f}', end=' ')
            
    def _print(self, msg, w, decimals=8):
        if w is not None:
            print(f'  {msg}: [', end=' ')
            self._print_list(w, d=decimals)
            print(']')
        
    def print_parameters(self):
        self._print('Conv Kernel', self.conv.weight)
        self._print(' {Conv Grad', self.conv.weight.grad)
        self._print('Lin Weights', self.linear.weight)
        self._print(' {Lin  Grad', self.linear.weight.grad)
        print('-'*40)

def tensor_to_img(img):
    return (img*255).squeeze().detach().numpy().astype(np.uint8)

def plt_images(X, save=False, rows=2, title=None):
    N = X.shape[0]
    fig, ax = plt.subplots(rows, N//rows)
    if title is not None: fig.suptitle(title)
    for idx,img in enumerate(X):
        row = idx // (N // rows)
        col = idx % (N // rows)
        img = tensor_to_img(img)
        ax[row,col].imshow(img, cmap='gray', vmin=0, vmax=255)
        #ax[row,col].set_axis_off()
        ax[row,col].set_xticks([])
        ax[row,col].set_yticks([])
        #print(img)
    plt.tight_layout()
    if save:
        plt.savefig('figures-simple-cnn.svg')
    else:
        plt.show()

def save_images(X, size=(100,100)):
    for idx,img in enumerate(X):
        img = tensor_to_img(img)
        Image.fromarray(img).resize(size, 0).save(f'image-{idx:03d}.png')

def train_model(net, X, y, max_epochs, lr):
    loss_fn = torch.nn.MSELoss()
    optimizer = torch.optim.SGD(net.parameters(), lr=lr)
    net.train(True)
    for epoch in range(max_epochs):
        optimizer.zero_grad()
        outputs = net(X)
        loss = loss_fn(outputs, y)
        loss.backward(retain_graph=True)
        optimizer.step()
        print(f'Epoch: {epoch+1:03d}')
        outputs = torch.sign(outputs.detach())
        print(f'      Outputs: ', end='')
        print([x.item() for x in outputs])
        print(f'         Loss: {loss.item():.8f}')
        net.print_parameters()
        if loss.item() < 0.01: break
    net.eval()
    
    return net

def plt_feature_map(net, X, y, marker='o', colors=['g','b']):
    for p, t in zip(X, y):
        group = int(t.squeeze().item())
        c = 'r' if group==-1 else 'b'
        point = net.get_feature_map(p.unsqueeze(0))
        point = point.squeeze().detach().numpy()
        plt.plot(point[0], point[1], marker=marker, c=c)

def plt_classification_space(net):
    w = net.linear.weight.squeeze().detach().numpy()
    w = w / np.linalg.norm(w)
    # ortogonal:
    v = np.array([-w[1],w[0]])
    
    origin = np.array([[0, 0, 0],[0, 0, 0]])
    #print(f'weights: {w}')
    plt.quiver(*origin, w[0], w[1], color=['g'],
               angles='xy', scale_units='xy',
               scale=1, label='Weights', width=0.004)
    # plot dimensions
    aux = np.linspace(min(plt.xlim()[0], plt.ylim()[0],w[0],w[1])-0.2,
                      max(plt.xlim()[1], plt.ylim()[1],w[0],w[1])+0.2, 2)
    plt.xlim(aux)
    plt.ylim(aux)
    plt.plot(aux, aux*(v[1]/v[0]))

def get_inputs_2points():
    X = [  # 1st:
           [[ [1.0 , 0.0 ],
              [0.0 , 1.0 ] ]],
           # 2nd:
           [[ [0.0 , 1.0 ],
              [1.0 , 0.0 ] ]]  ]
    y = [  [[[-1.]]],   #1st
           [[[ 1.]]]  ] #2nd
    return (X,y)

def get_inpus_8points():
    X = [  # 1st group:
           [[ [1.0 , 0.0 ],
              [0.0 , 1.0 ] ]],
           [[ [0.75, 0.0 ],
              [0.0 , 0.75] ]],
           [[ [0.5 , 0.0 ],
              [0.0 , 0.5 ] ]],
           [[ [0.25, 0.0 ],
              [0.0 , 0.25] ]],
           # 2nd group:
           [[ [0.0 , 1.0 ],
              [1.0 , 0.0 ] ]],
           [[ [0.0 , 0.75],
              [0.75, 0.0 ] ]],
           [[ [0.0 , 0.5 ],
              [0.5 , 0.0 ] ]],
           [[ [0.0 , 0.25],
              [0.25, 0.0 ] ]]  ]
    y = [  [[[-1.]]], [[[-1.]]], [[[-1.]]], [[[-1.]]],   #1st
           [[[ 1.]]], [[[ 1.]]], [[[ 1.]]], [[[ 1.]]]  ] #2nd
    return (X,y)

if __name__ == '__main__':
    max_epochs = 100
    lr = 0.1
    uniform_distrib = True
    # uniform or normal distribution:
    rand = torch.rand if uniform_distrib else torch.randn
    plt.ion()
    
    # Getting points to train the Oracle:
    X,y = get_inpus_8points()
    X = torch.tensor(X, requires_grad=True)    
    y = torch.tensor(y, requires_grad=True)
    # Generating image attack
    attack_x = rand(3*X.shape[0], 1, 2, 2)
    
    # Plotting images:
    plt_images(X, rows=2, title='Training dataset')
    plt_images(attack_x, rows=4, title='Attack dataset')
    
    # Training the Oracle:
    oracle = SimpleNet()
    oracle.print_parameters()
    oracle = train_model(oracle, X, y, max_epochs, lr)
    
    # ATTACK: Getting labels from the oracle
    attack_y = torch.sign(oracle(attack_x))
    
    # Plotting results:
    plt.figure(figsize=(8,8))
    plt.title('Oracle')
    plt_feature_map(oracle, X, y, marker='o')
    plt_classification_space(oracle)
    plt_feature_map(oracle, attack_x, attack_y, marker='x')
    
    # Training the Copycat
    copycat = SimpleNet()
    copycat.print_parameters()
    copycat = train_model(copycat, attack_x, attack_y, max_epochs, lr)
    
    plt.figure(figsize=(8,8))
    plt.title('Copycat')
    plt_feature_map(copycat, X, y, marker='o')
    plt_classification_space(copycat)
    plt_feature_map(copycat, attack_x, attack_y, marker='x')

    input('Press ENTER to finish...')
