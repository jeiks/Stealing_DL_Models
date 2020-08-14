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
from image_list import ImageList
#system
from sys import argv, exit, stderr

if __name__ == '__main__':
    if len(argv) != 3:
        print('Use: {} model_filename.pth image_list.txt'.format(argv[0]), file=stderr)
        exit(1)
    
    ans = input(
                'The cache property will apply transforms (resize, create tensor, etc.) on\n'
                ' all images and store them into a single cache file.\n'
                'It will replace the process of open and apply transforms on an image to only\n'
                ' read the cache file, and create the tensor.\n'
                'On my tests, the training time per batch reduced from 2h to 1h.\n'
                'But it created a file with 32GB (data from ImageNet and Microsoft COCO).\n'
                'Would you like to use cache? [y/N] '
                )

    model_fn   = argv[1]
    imglist_fn = argv[2]
    use_cache  = True if ans.upper().startswith('Y') else False
    batch_size = 32
    max_epochs = 10
    
    model = CNN()
    
    transform = transforms.Compose([ transforms.Resize( (32,32) ), transforms.ToTensor() ])
    if use_cache:
        dataset = ImageList(imglist_fn, color=True, transform=transform, return_filename=False, cache_filename='cache.kxe')
    else:
        dataset = ImageList(imglist_fn, color=True, transform=transform, return_filename=False)
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=1e-4, momentum=0.9)
    
    device = torch.device('cuda' if torch.cuda.is_available else 'cpu')

    print('Training model...')
    model = model.to(device)
    for epoch in range(max_epochs):
        running_loss = 0.0
        with tqdm(loader) as tqdm_loader:
            for i, (inputs, labels) in enumerate(tqdm_loader):
                inputs, labels = inputs.to(device), labels.to(device)

                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item()

                if i % 200 == 199:
                    tqdm_loader.set_description('Epoch: {}/{} Loss: {:.3f}'.format(
                        epoch+1, max_epochs, running_loss/200.))
                    running_loss = 0.0

    print('Model trained.')
    print('Saving the model to "{}"'.format(model_fn))

    torch.save(model.state_dict(), model_fn)

