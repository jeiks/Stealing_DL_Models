#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from imageio import imread, imwrite
from imgaug import augmenters as iaa
import imgaug as ia
import numpy as np
from matplotlib import pylab as plt
from sys import exit, stdout


def check_args():
    from sys import argv, exit
    from os import access, R_OK, path, mkdir
    if len(argv) != 4:
        print("Use: {} images_file.txt target_dir n_instances_per_class".format(argv[0]))
        exit(1)
    if not access(argv[1], R_OK):
        print("ERROR: cannot access '{}'".format(argv[1]))
        exit(2)
    if path.isdir(argv[2]):
        print("ERROR: '{}' already exists. Remove it to continue.".format(argv[2]))
        exit(3)
    else:
        mkdir(argv[2], 0o755)

    return argv[1], argv[2], int(argv[3])


def print_msg(msg):
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
    ret = []
    for i in filenames:
        x = imread(i)
        ret.append(x[:,:,:3] if x.shape[-1] == 4 else x)
    return ret


def get_aug_methods():
    # options: ["constant", "edge", "symmetric", "reflect", "wrap"]
    mode = "edge"
    seq = np.array([
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
    ])
    return seq


def show_image(img):
    plt.imshow(img, cmap='gray')
    plt.show()


def create_images(classes, augmentations, target_dir, n_for_class_general, split_size=None, show=False):
    print('Creating images...')
    for k in classes.keys():
        if len(classes[k]) >= n_for_class_general:
            continue
        else:
            n_for_class = n_for_class_general - len(classes[k])
            n_size = n_for_class // len(classes[k])
            aug_this_n = tuple(augmentations[np.random.permutation(len(augmentations))[:n_size]])

        count     = 0
        img_count = 0
        class_len = len(classes[k])
        split_size = class_len // 10
        split_data = np.array_split(classes[k], class_len if split_size==0 else split_size)

        stop = False
        for filenames in split_data:
            if stop: break
            if img_count >= n_for_class: break
            img_count += len(filenames)
            print_msg("\rCreating {:4d}/{:4d} from class {}: {}{}".format(
                      img_count, class_len, k, '.' * len(aug_this_n), '\b' * len(aug_this_n)))

            images = read_images(filenames)
            for aug in aug_this_n:
                if stop: break
                print_msg("·")
                aug_images = aug.augment_images(images)
                for img in aug_images:
                    if show: show_image(img)
                    imwrite('{}/class_{}-{}.jpg'.format(target_dir, k, format(count, '06')), img)
                    count += 1
                    if count >= n_for_class:
                        stop = True
                        break
                del aug_images
            del images

        while count < n_for_class:
            img = classes[k][np.random.randint(class_len)]
            aug = augmentations[np.random.randint(len(augmentations))]
            imwrite('{}/class_{}-{}.jpg'.format(target_dir, k, format(count, '06')), aug.augment_image(imread(img)))
            count+=1

        print()


if __name__ == '__main__':
    filenames, targetdir, n_for_class = check_args()

    # NOTE: same feed generates the same data
    ia.seed(1)
    classes = open_file(filenames)
    seq     = get_aug_methods()
    create_images(classes, seq, targetdir, n_for_class)
