#torch
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F

def get_transform():
    '''
    @return: torch transforms to use in CIFAR10
    '''
    transform = transforms.Compose([
        transforms.Resize( (32,32) ),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))        
    ])
    
    return transform

def get_datasets(root='data', train=True, test=True, transform=None, batch=4):
    '''
    @brief: function that obtains the CIFAR10 dataset and return
            the referent DataLoaders
    @param root: place to store original data
    @param train: when True, returns the train data
    @param test: when True, returns the test data
    @param batch: batch size to dataloaders

    @return: dictionary composed by: 'train' and 'test' datasets and 
                                      the name of the 'classes'.
             Dictionary keys: 'train', 'test', 'classes'
    '''
    assert train or test, 'You must select train, test, or both'
    ret = {}
    transform = get_transform() if transform is None else transform
    if train:
        trainset = torchvision.datasets.CIFAR10(
            root=root, train=True, download=True, transform=transform
        )
        trainloader = torch.utils.data.DataLoader(
            trainset, batch_size=batch, shuffle=True, num_workers=2
        )
        ret['train']   = trainloader
        ret['n_train'] = len(trainset)
        
    if test:
        testset = torchvision.datasets.CIFAR10(
            root=root, train=False, download=True, transform=transform
        )
        testloader = torch.utils.data.DataLoader(
            testset, batch_size=batch, shuffle=False, num_workers=2
        )
        ret['test']   = testloader
        ret['n_test'] = len(testset)

    classes = ('plane', 'car', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck')
    ret['classes'] = classes
    
    return ret
