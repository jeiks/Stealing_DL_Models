This folder provides the program, sripts and configuration files used to build the LRP heatmaps.

First steps:

1. Download and build LRP Toolbox [link](https://github.com/sebastian-lapuschkin/lrp_toolbox/tree/master/caffe-master-lrp);
1. Copy this folder to "caffe-master-lrp/demonstrator";
1. Run: `make build`

Last Steps:

1. There exists a folder for each problem.<br>
Inside this folder, there is a image list inside the file "images.txt".<br>
You have to download the relative images and copy them to PROBLEM_NAME/images
1. Download all models used in [Data Curve](../03-data_curve-VGG) and the target [original models](../02-copycat-VGG_to_VGG/) (target networks).<br>
Create a link or copy each caffemodel to problem's folder with the following names:
   * original.caffemodel 
   * copycat-0k.caffemodel
   * copycat-100k.caffemodel
   * copycat-500k.caffemodel
   * copycat-1m.caffemodel
   * copycat-1.5m.caffemodel
   * copycat.caffemodel (this is the 3M caffemodel)
1. Download the [mean's files](../data) (used by original model) and copy the file "train.mean" to this problem's folder.
1. Finally, run: `make run`
