# Copycat CNN: Are Random Non-Labeled Data Enough to Steal Knowledge from Black-box Models?

![Copycat](copycat.svg)

Convolutional neural networks have been successful lately enabling companies to develop neural-based products, which demand an expensive process, involving data acquisition and annotation; and model generation, usually requiring experts.
With all these costs, companies are concerned about the security of their models against copies and deliver them as black-boxes accessed by APIs.
Nonetheless, we argue that even black-box models still have some vulnerabilities.
In a preliminary work, we presented a simple, yet powerful, method to copy black-box models by querying them with natural random images.
In this work, we consolidate and extend the copycat method:
(i) some constraints are waived;
(ii) an extensive evaluation with several problems is performed;
(iii) models are copied between different architectures; and,
(iv) a deeper analysis is performed by looking at the copycat behavior.
Results show that natural random images are effective to generate copycats for several problems. 

This paper is available on [arXiv](https://arxiv.org/abs/2101.08717)

    @article{jacson2021patrec,
	  author={Jacson Rodrigues {Correia-Silva} and Rodrigo F. {Berriel} and Claudine {Badue} and Alberto F. {De Souza} and Thiago {Oliveira-Santos}},
	  title={Copycat CNN: Are random non-Labeled data enough to steal knowledge from black-box models?},
	  journal={Pattern Recognition},
	  volume={113},
	  pages={107830},
	  year={2021},
	  issn={0031-3203}
    }
