Image list:<br>
* [ODD](ODD.txt.7z)
* [PDD-OL](PDD_OL.txt.7z)
* [PDD-SL](PDD_SL.txt.7z)
* [TDD](TDD.txt.7z)
* [NPDD with 3M images replicated to Copycat training](NPD-aug.txt.7z)
* [NPDD with 3M images](NPD.txt.7z)

Data Curve:<br>
* [NPDD with 1k images replicated to Copycat training](NPD_SL-0.1mi-aug.txt.7z)
* [NPDD with 1k images](NPD_SL-0.1mi.txt.7z)
* [NPDD with 5k images replicated to Copycat training](NPD_SL-0.5mi-aug.txt.7z)
* [NPDD with 5k images](NPD_SL-0.5mi.txt.7z)
* [NPDD with 1M images replicated to Copycat training](NPD_SL-1.0mi-aug.txt.7z)
* [NPDD with 1M images](NPD_SL-1.0mi.txt.7z)
* [NPDD with 1.5M images replicated to Copycat training](NPD_SL-1.5mi-aug.txt.7z)
* [NPDD with 1.5M images](NPD_SL-1.5mi.txt.7z)

note: the image lists with replicated images were generated with [image_replication.py](../../scripts/image_replication.py) 

Mean file: [train.mean](train.mean)

<hr>
To create the ODD, PDD and TDD, you have to:

1. Download the original dataset:<br>
   * UCF101.rar<br>
   * UCF101TrainTestSplits-RecognitionTask.zip<br>
   from: [https://www.crcv.ucf.edu/data/UCF101.php](https://www.crcv.ucf.edu/data/UCF101.php)
1. Download the [scripts](scripts) folder.
1. Extract the file UCF101.rar and UCF101TrainTestSplits-RecognitionTask.zip
   1. Copy [extract_images.sh](./scripts/extract_images.sh) to UCF-101 folder.
   1. Run: `./extract_images.sh`<br>
   note: you can run it in several terminals at same time to speed up the process.
1. Copy [separate.sh](./scripts/separate.sh) and [apply_pattern.py](./scripts/apply_pattern.py) to root folder.
   1. Run: `./separate.sh`

It will generate the folders "train" and "test" and the files "train.txt" and "test.txt" based on UCF-101 images.<br>
You can now randomly select 2 random imagesets (images generated from an specific video) per class using "train.txt" annotations. Use them to generate the PDD.<br>
Use the remaining annotations of "train.txt" to generate ODD.<br>
And use "test.txt" to generate the TDD.
