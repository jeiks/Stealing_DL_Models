### Scripts

* [extract_image_list_feature_maps.py](extract_image_list_feature_maps.py): <br>It is used to extract the image feature maps vectors from a caffe VGG model.
* [image-augmentation_N.py](image-augmentation_N.py): <br>It is used to apply augmentation process to images.<br>
  The result is a folder with M images per class, being M = N - "images that already exist in that class".
* [image_replication.py](image_replication.py): <br>It is used to replicate and remove images from dataset classes to get the desired number of examples.
* [label_the_image_list.py](label_the_image_list.py): <br>It is used to label the images by using a caffe model.
