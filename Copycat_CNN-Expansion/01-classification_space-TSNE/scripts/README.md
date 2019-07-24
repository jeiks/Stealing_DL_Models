This folder contains the following scritps:

* extract_feature_maps.py
  * It extracts the features maps from VGG's fc7_layer (the first layer before logits).
```shell
   # Example:
   $ ./extract_feature_maps.py                  \
        -m DIG10/prototxt/train_test.prototxt \     
        -f images.txt                         \
        -w DIG10/snapshot_number.caffemodel   \
        -i DIG10/train.mean                   \
        -o DIG10-vectors.txt                  \
        -g 0
```

-> count_class.sh
   It counts the amount of images per class.
```shell
   # Example:
   $ ./count_class.sh DIG10-vectors.txt
```

-> get_N_vectors_by_class.sh
   After generate the vectors, you can count the image by class and
   use this script to choose the amount of image per class you want
   to select.
```shell
   # Example:
   $ ./get_N_vectors_by_class.sh 1000 DIG10-vectors.txt > output.txt
```
