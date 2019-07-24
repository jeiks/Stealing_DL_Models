Image list:<br>
* [ODD](OD.txt.7z)
* [PDD-OL](PD_OL.txt.7z)
* [PDD-SL](PD_SL.txt.7z)
* [TDD](TD.txt.7z)
* [NPDD with 3M images replicated to Copycat training](NPD_SL-aug.txt.7z)
* [NPDD with 3M images](NPD_SL.txt.7z)

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
To generate the SIG dataset, you have to run the scripts in [dataset_creation](dataset_creation).<br>
But, before generate the SIG dataset, you must download the TT100K and TSRD datasets.

Then, [download](http://www.nlpr.ia.ac.cn/pal/trafficdata/recognition.html) the following files:

* TSRD-Test.zip;
* tsrd-train.zip;

And [download](http://cg.cs.tsinghua.edu.cn/traffic-sign/) the following file:

* data.zip
