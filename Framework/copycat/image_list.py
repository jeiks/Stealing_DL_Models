import warnings
import torch.utils.data as data
import os.path
import numpy as np
import torch
import cv2
#from PIL import Image
from torchvision.transforms import ToPILImage
from tqdm import tqdm
from sys import stderr

from ctypes import Structure, c_int16, c_float, c_char, sizeof as ctypes_sizeof
import io

class ImageHeader(Structure):
    pass

class CacheDataset():
    def __init__(self, filename, dataset):
        self.filename = filename
        self.dataset = dataset
        self.save_filename = dataset.return_filename
        self.original_shape, self.__size = self.__set_ImageHeader_and_get_item_size()
        if not self.__use_existing_cache(): self.__create_cache()
    
    def __set_ImageHeader_and_get_item_size(self):
        '''
        set _fields_ in ImageHeader and returns the struct size
        '''
        img_aux = self.dataset.getitem(0)
        img_n_floats = img_aux[0].view(-1).shape[0]
        if type(img_aux[1]) == int:
            cat_size = c_int16
            cat_shape = 1
        else:
            #TODO: test it
            cat_size = c_float*img_aux[1].shape[0]
            cat_shape = img_aux[1].shape
        
        if self.save_filename:
            ImageHeader._fields_ = [('img', c_float*img_n_floats), ('cat', cat_size), ('fn', c_char*80)]
        else:
            ImageHeader._fields_ = [('img', c_float*img_n_floats), ('cat', cat_size)]
        
        
        return img_aux[0].shape, ctypes_sizeof(ImageHeader)
        
    def __use_existing_cache(self):
        '''
        return:
            True: to create a new cache
            False: to use already created cache instead of create a new one
        '''
        ans = 'N'
        if os.path.exists(self.filename):
            print('The file "{}" already exists.'.format(self.filename), file=stderr)
            print('Do you want to use it?', file=stderr)
            print('(only answer YES if all files listed in "txt" file are cached in {})'.format(self.filename), file=stderr)
            ans = input('[y/N]? ')

        return True if ans.upper().startswith('Y') else False
       
    def __create_cache(self):
        print('Creating cache (it can take some time)... ', file=stderr)
        with open(self.filename, 'wb') as fd:
            if self.save_filename:
                for img, cat, fn in tqdm(self.dataset):
                    hdr = self.__fill_structure(img, cat)
                    self.__fill_fn(hdr, fn)
                    fd.write(hdr)
            else:
                for img, cat in tqdm(self.dataset):
                    hdr = self.__fill_structure(img, cat)
                    fd.write(hdr)
    
    def __fill_structure(self, img, cat):
        hdr = ImageHeader()
        hdr.img = (hdr._fields_[0][1])(*img.view(-1).numpy().tolist())
        if type(cat) == int:
            hdr.cat = (hdr._fields_[1][1])(cat)
        else:
            #TODO: test it
            hdr.cat = (hdr._fields_[1][1])(*cat)
        return hdr
    
    def __fill_fn(self, hdr, fn):
        hdr.fn = bytes(fn.encode('utf-8'))
        
    def get_cached_item(self, index):
        with open(self.filename,'rb') as fd:
            fd.seek(self.__size*index)
            item = ImageHeader()
            io.BytesIO( fd.read(self.__size) ).readinto(item)
        
        if type(item.cat) != int:
            cat = np.array(item.cat, order='C', dtype=np.float32)
        else:
            cat = item.cat
            
        if self.save_filename:
            return (torch.tensor(item.img).reshape(self.original_shape), cat, item.fn.decode('utf-8'))
        else:
            return (torch.tensor(item.img).reshape(self.original_shape), cat)

class ImageList(data.Dataset):
    '''
    Image List Dataset
    Args:
        filename (string): Image List Filename
        color (optional): Open images as RGB instead of Grayscale
        root (string, optional): Root directory of image files
        transform (callable, optional): A function/transform that takes in an PIL
            image and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): same as transform but applied only
            on target(labels, outputs)
        return_filename (boolean, optional): In addition to the image and label, it
            also returns the image filename: (image, label, filename)
        logits (optional): {True, NUM_CLASSES} it will consider several outputs instead
            of only one label
        cache_filename (optional): save images in cache_filename to load them faster during training
            (it is good to be used when you have to resize bigger images to small ones)
    '''
    @property
    def train_labels(self):
        warnings.warn("train_labels has been renamed targets")
        return self.targets

    @property
    def test_labels(self):
        warnings.warn("test_labels has been renamed targets")
        return self.targets

    @property
    def train_data(self):
        warnings.warn("train_data has been renamed data")
        return self.data

    @property
    def test_data(self):
        warnings.warn("test_data has been renamed data")
        return self.data

    def __init__(self, filename, color=False, root=None, transform=None, target_transform=None,
                 return_filename=False, logits={'logits': False, 'num_classes': 0}, cache_filename=None):
        self.filename = filename
        self.color = cv2.IMREAD_COLOR if color else cv2.IMREAD_GRAYSCALE
        self.array_type = np.uint8 if self.color else np.float32
        self.root = os.path.expanduser(root) if root else None
        self.transform = transform
        self.target_transform = target_transform
        self.return_filename = return_filename
        self.getitem = self.__getitem__with_filename__ if return_filename else self.__getitem_simple__
        self.logits = logits['logits']
        if self.logits:
            dtype=['S80']+[np.float32 for _ in range(logits['num_classes'])]
            usecols = tuple(range(len(dtype)))
            data = np.genfromtxt(filename, dtype=dtype, usecols=usecols)
            self.data = np.array(data['f0'], dtype=str)
            self.targets = np.array( [ data['f{}'.format(x)]
                                       for x in usecols[1:] ]).T
        else:
            more_than_one_col = len(open(filename).readline().split()) > 1
            if more_than_one_col:
                data = np.genfromtxt(filename, dtype=['S80', int], usecols=(0,1))
                self.data = np.array(data['f0'], dtype=str)
                self.targets = np.array(data['f1'], dtype=int)
            else:
                data = np.atleast_1d( np.genfromtxt(filename, dtype=['S80'],usecols=0) )
                self.data = np.array(data, dtype=str)
                self.targets = np.zeros(len(self.data))
        del data
        
        if cache_filename is not None:
            self.cache = CacheDataset(cache_filename, self)
            self.getitem = self.cache.get_cached_item
            
    # the implementation was done in this way to let it faster.. TODO: performance tests
    def __getitem__(self, index):
        return self.getitem(index)

    def __getitem__with_filename__(self, index):
        return self.__getitem__aux__(index)

    def __getitem_simple__(self, index):
        return self.__getitem__aux__(index)[:-1]

    def __getitem__aux__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (image, target) where target is index of the target class.
        """            
        if self.logits:
            img_fn, target = self.data[index], self.targets[index]
        else:
            img_fn, target = self.data[index], int(self.targets[index])
        
        if self.root:
            img_fn = os.path.join(self.root, img_fn)

        #img = Image.open(img_fn)
        # the network output was different without this conversion:
        img = np.array(cv2.imread(img_fn, self.color), dtype=self.array_type)
        # to be compatible with pytorch:
        img = ToPILImage()( img )
        #img = cv2.imread(img_fn)
        
        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target, img_fn


    def __len__(self):
        return len(self.targets)
    

    def __repr__(self):
        fmt_str = 'Dataset ' + self.__class__.__name__ + '\n'
        fmt_str += '    Number of datapoints: {}\n'.format(self.__len__())
        tmp = '    Transforms (if any): '
        fmt_str += '{0}{1}\n'.format(tmp, self.transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        tmp = '    Target Transforms (if any): '
        fmt_str += '{0}{1}'.format(tmp, self.target_transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        return fmt_str
