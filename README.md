# Copycat CNN

Here you can find the models, the datasets information and the code used in our experiments ([Copycat](README.md#1-stealing-knowledge-by-persuading-confession-with-random-non-labeled-data) and [Copycat Expansion](README.md#2-copycat-cnn-are-random-non-labeled-data-enough-to-steal-knowledge-from-black-box-models)).
Feel free to contact me for any questions or suggestions (jacsonrcsilva at gmail).

Note that we used the Caffe Framework ([1](https://caffe.berkeleyvision.org/), [2](https://ngc.nvidia.com/catalog/containers/nvidia:caffe)).
Therefore, you will find the "prototxt" files to replicate our experiments.

But if you don't want to use Caffe, it is not a problem.
In order to make it easier for you, we are also providing the following codes implemented in **PyTorch**:
* [Copycat Example](Example_of_use); and
* [Copycat Framework](https://github.com/jeiks/copycat_framework) to you apply/test Copycat Method against your own data.

Also, if you want to see an interactive comparison between Oracle and Copycat models, visit: [Copycat CNN Explainer](http://www.jeiks.net/copycat-cnn-explainer/)
<br>It is implemented in TensorflowJS, using the [CNN Explainer](https://github.com/poloclub/cnn-explainer) system.

If something here was useful to you, please kindly cite our article (s) below.

😊

## 1. Stealing Knowledge by Persuading Confession with Random Non-Labeled Data

<div align="center"><img src="Copycat_CNN/copycat.svg" alt="Copycat" width="60%"></div>

[Project Details and Code](Copycat_CNN/)

This paper is available on [arXiv](https://arxiv.org/abs/1806.05476)

    @inproceedings{Correia-Silva-IJCNN2018,
      author={Jacson Rodrigues {Correia-Silva} and Rodrigo F. {Berriel} and Claudine {Badue} and Alberto F. {de Souza} and Thiago {Oliveira-Santos}},
      booktitle={2018 International Joint Conference on Neural Networks (IJCNN)},
      title={Copycat CNN: Stealing Knowledge by Persuading Confession with Random Non-Labeled Data},
      year={2018},
      pages={1-8},
      doi={10.1109/IJCNN.2018.8489592},
      ISSN={2161-4407},
      month={July}
    }

## 2. Copycat CNN: Are Random Non-Labeled Data Enough to Steal Knowledge from Black-box Models?

<div align="center"><img src="Copycat_CNN-Expansion/copycat.svg" alt="Copycat" width="80%"></div>

[Project Details and Code](Copycat_CNN-Expansion/)

This paper is available on [arXiv](https://arxiv.org/abs/2101.08717)

    @article{Correia-Silva-PATREC2021,
	  author={Jacson Rodrigues {Correia-Silva} and Rodrigo F. {Berriel} and Claudine {Badue} and Alberto F. {De Souza} and Thiago {Oliveira-Santos}},
	  title={Copycat CNN: Are random non-Labeled data enough to steal knowledge from black-box models?},
	  journal={Pattern Recognition},
	  volume={113},
	  pages={107830},
	  year={2021},
	  issn={0031-3203}
    }

## 3. An example of how to use Copycat Method

[Example Code for Copycat in *PyTorch*](Example_of_use)

## 4. Our Framework in PyTorch to use Copycat Method on your experiments/data

[Copycat Framework](https://github.com/jeiks/copycat_framework)

[The PyTorch Weights for Oracle and Copycat models can be downloaded here](https://drive.google.com/drive/folders/1t1yANSFisafcLRtt3ibTUp81RF1I2NzP?usp=drive_link)

## 5. My Thesis:

[Copycat CNN: Convolutional Neural Network Extraction Attack with Unlabeled Natural Images](https://sappg.ufes.br/tese_drupal//tese_17166_Tese-Jacson-2018142921.pdf)
([more details](https://informatica.ufes.br/pt-br/pos-graduacao/PPGI/detalhes-da-tese?id=17166))<br>
([2nd download option](https://drive.google.com/file/d/1ceLIJOvPMyRc2IN5hkE3-Ncgp4PxM6wQ/view?usp=sharing))

[The PyTorch Weights for Oracle and Copycat models can be downloaded here](https://drive.google.com/drive/folders/1t1yANSFisafcLRtt3ibTUp81RF1I2NzP?usp=drive_link)

    @phdthesis{correia-silva-phd-2023,
        author = {Correia-Silva, Jacson Rodrigues},
        title = {Copycat CNN: Convolutional Neural Network Extraction Attack with Unlabeled Natural Images},
        year = {2023},
        school = {Universidade Federal do Esp\'{i}rito Santo},
        address = {Esp\'{i}rito Santo, Brazil},
    }
