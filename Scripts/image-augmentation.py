#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from imageio import imread, imwrite
from imgaug import augmenters as iaa
import imgaug as ia
import numpy as np
from matplotlib import pylab as plt


def check_args():
    from sys import argv, exit
    from os import access, R_OK, path, mkdir
    if len(argv) != 3:
        print("Use: {} images_file.txt target_dir".format(argv[0]))
        exit(1)
    if not access(argv[1], R_OK):
        print("ERROR: cannot access '{}'".format(argv[1]))
        exit(2)
    if path.isdir(argv[2]):
        print("ERROR: '{}' already exists. Remove it to continue.".format(argv[2]))
        exit(3)
    else:
        mkdir(argv[2], 0o755)

    return argv[1], argv[2]


def print_msg(msg):
    from sys import stdout
    stdout.write(msg)
    stdout.flush()


def open_file(filename):
    print_msg('Opening file "{}"... '.format(filename))
    images = np.array([x.split() for x in open(filename).readlines()])
    classes = {}
    for i in np.unique(images[:,1]):
        classes[int(i)] = [x[0] for x in images[images[:, 1] == i]]
    print('done')
    return classes


def read_images(filenames):
    return [imread(x) for x in filenames]


def get_aug_methods():
    # options: ["constant", "edge", "symmetric", "reflect", "wrap"]
    mode = "edge"
    seq = (
     # rotate + shear + translate + scale
     iaa.Affine(rotate=(-20, 20), shear=(-20, 20), translate_percent=(-.2, .2), scale=(0.9, 1.0), order=[0, 1, 2, 3], mode=mode),
     # shear + rotate + translate + scale
     iaa.Affine(shear=(-20, 20), rotate=(-20, 20), translate_percent=(-.2, .2), scale=(0.9, 1.0), order=[0, 1, 2, 3], mode=mode),
     # scale + shear + rotate + translate + scale
     iaa.Affine(scale=(0.85, 1.0), shear=(-20, 20), rotate=(-20, 20), translate_percent=(-.2, .2), order=[0, 1, 2, 3], mode=mode),
     # rotate + translate + shear + scale
     iaa.Affine(rotate=(-20, 20), translate_percent=(-.2, .2), shear=(-20, 20), scale=(0.9, 1.0), order=[0, 1, 2, 3], mode=mode),
     # rotate + translate + scale
     iaa.Affine(rotate=(-20, 20), translate_percent=(-.2, .2), scale=(0.9, 1.0), order=[0, 1, 2], mode=mode),
     # scale + rotate + translate
     iaa.Affine(scale=(0.9, 1.0), rotate=(-20, 20), translate_percent=(-.2, .2), order=[0, 1, 2], mode=mode),
     # crop + translate + shear
     iaa.Sequential([
        iaa.Crop(percent=(0, 0.1)),
        iaa.Affine(translate_percent=(-.1, .1), shear=(-15, 15), order=[0,1], mode=mode)
     ]),
     # crop + rotate + translate + shear
     iaa.Sequential([
         iaa.Crop(percent=(0, 0.1)),
         iaa.Affine(rotate=(-10,10), translate_percent=(-.1, .1), shear=(-15, 15), order=[0, 1, 2], mode=mode)
     ]),
     # crop + rotate + translate + shear + flipr
     iaa.Sequential([
         iaa.Crop(percent=(0, 0.1)),
         iaa.Affine(rotate=(-10, 10), translate_percent=(-.1, .1), shear=(-15, 15), order=[0, 1, 2], mode=mode),
         iaa.Fliplr(0.9)
     ]),
     # gaussian noise
     iaa.AdditiveGaussianNoise(scale=(0, 0.08 * 255)),
     # sharpen
     iaa.Sharpen(alpha=(0.5, 1.0), lightness=(0.7, 2.)),
     # crop
     iaa.Crop(percent=(0, 0.15)),
     # gaussian + flipr
     iaa.Sequential([
        iaa.AdditiveGaussianNoise(scale=(0, 0.08 * 255)),
        iaa.Fliplr(0.9)
     ]),
     # sharpen + flipr
     iaa.Sequential([
        iaa.Sharpen(alpha=(0.5, 1.0), lightness=(0.7, 2.)),
        iaa.Fliplr(0.9)
     ]),
     # crop + flipr
     iaa.Sequential([
        iaa.Crop(percent=(0, 0.15)),
        iaa.Fliplr(0.9)
     ]),
     # gaussian blur
     iaa.GaussianBlur(sigma=(1.,1.5)),
     # add
     iaa.Add((-20, 40)),
     # contrast normalization
     iaa.ContrastNormalization((1., 1.5)),
     # piecewise affine 1
     iaa.PiecewiseAffine(scale=(0.01, 0.05)),
     # piecewise affine 2
     iaa.PiecewiseAffine(scale=(0.01, 0.05)),
     # piecewise affine 3
     iaa.PiecewiseAffine(scale=(0.01, 0.05)),
     # rotate + translate + scale + piecewise affine
     iaa.Sequential([
        iaa.Affine(rotate=(-20, 20), translate_percent=(-.2, .2), scale=(0.9, 1.0), order=[0, 1, 2], mode=mode),
        iaa.PiecewiseAffine(scale=(0.01, 0.05))
     ])
    )
    return seq


def show_image(img):
    plt.imshow(img, cmap='gray')
    plt.show()


def create_images(classes, augmentations, target_dir, split_size=None, show=False):
    print('Creating images...')
    if not split_size:
        aux = list(classes.keys())[0]
        split_size = int(len(classes[aux])/10.)
        if split_size == 0: split_size = 1
        del aux

    for k in classes.keys():
        count     = 0
        img_count = 0
        class_len = len(classes[k])
        split_data = np.array_split(classes[k], int(class_len / split_size))

        for filenames in split_data:
            img_count += len(filenames)
            print_msg("\rCreating {}/{} from class {}: {}{}".format(
                      img_count, class_len, k, '.' * len(augmentations), '\b' * len(augmentations)))

            images = read_images(filenames)
            for aug in augmentations:
                print_msg("·")
                aug_images = aug.augment_images(images)
                for img in aug_images:
                    if show: show_image(img)
                    imwrite('{}/class_{}-{}.jpg'.format(target_dir, k, format(count, '06')), img)
                    count += 1
                del aug_images
            del images

        print()


if __name__ == '__main__':
    filenames, targetdir = check_args()

    # NOTE: same feed generates the same data
    ia.seed(1)
    classes = open_file(filenames)
    seq     = get_aug_methods()
    from sys import exit
    for i in seq:
        print(i)
        print('')
        create_images(classes, seq, targetdir)
