This dataset was created with images from ImageNet and Microsoft COCO.

Firstly, download the images from:

* Microsoft COCO:
  * Link: _2017 Unlabeled images [123K/19GB]_
  * URL: [Microsoft COCO](http://cocodataset.org/#download)
* ImageNet:
  * Link: _Decathlon data, 6.1 GB_
  * Link: _Download links to ILSVRC2017 image data._
    * Link: _CLS-LOC dataset. 155GB_
    * Link: _DET dataset. 55GB_
  * URL: [ImageNet](http://image-net.org/download-images)

Next, extract all 'tar' and 'zip' files to root folder.<br>
After, extract [images.index.txt.7z](images.index.txt.7z).<br>
Then, run the [organize.sh](organize.sh) in root folder.
```shell
chmod +x organize.sh
./organize.sh
```

It will generate the file "images.txt" with all NPDD images.
