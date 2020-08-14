#torch
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
#general
import matplotlib.pyplot as plt
import numpy as np
import random
from tqdm import tqdm
#local files:
from model import CNN
from cifar_data import get_datasets
#system
from sys import argv, exit, stderr

def imshow(img):
    img = img / 2 + 0.5     # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()

def show_samples(data_loader, n_batches=1, classes=None):
    # get some random training images
    count = 0
    for images, labels in data_loader:
        count += 1
        # show images
        imshow(torchvision.utils.make_grid(images))
        # print labels
        ##print(' '.join(
        ##            '{:5s}'.format(
        ##              str(labels[j].item()) if classes is not None else classes[labels[j]]
        ##            ) for j in range(4))
        ##    )
        if count == n_batches: break

if __name__ == '__main__':
    if len(argv) != 2:
        print('Use: {} model_filename.pth'.format(argv[0]), file=stderr)
        exit(1)
    
    model_fn = '{}.pth'.format('.'.join(argv[1].split('.')[:-1]))

    model = CNN()
    
    datasets = get_datasets(test=False)

    s = input('Do you wanna see CIFAR10 samples? [y/N] ')
    if s.upper().startswith('Y'):
        show_samples(datasets['train'], classes=datasets['classes'])
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
    
    device = torch.device('cuda' if torch.cuda.is_available else 'cpu')

    print('Training model...')
    model = model.to(device)
    max_epochs = 20
    for epoch in range(max_epochs):
        running_loss = 0.0
        with tqdm(datasets['train']) as tqdm_train:
            for i, data in enumerate(tqdm_train):
                # get the inputs; data is a list of [inputs, labels]
                inputs, labels = data
                inputs, labels = inputs.to(device), labels.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward + backward + optimize
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                # print statistics
                running_loss += loss.item()
                if i % 200 == 199:
                    tqdm_train.set_description('Epoch: {}/{} Loss: {:.3f}'.format(
                        epoch+1, max_epochs, running_loss / 200.))
                    running_loss = 0.0

    print('Model trained.')
    print('Saving the model to "{}"'.format(model_fn))

    torch.save(model.state_dict(), model_fn)

