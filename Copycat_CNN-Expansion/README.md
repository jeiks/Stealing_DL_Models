# (under evaluation) Is Random Non-Labeled Data Enough to Steal Knowledge from Black-box Models and Generate Copycat CNN?

![Copycat](copycat.svg)

Convolutional neural networks have been extremely successful lately enabling companies to develop neural-based products.
These products demand an expensive process, involving data acquisition and annotation; and model generation, usually requiring experts.
With all these costs, companies are concerned about the security of their models against copies and deliver them as black-boxes accessed by APIs.
Nonetheless, we argue that even black-box models still have some vulnerabilities.
In a preliminary work, we presented a simple, yet powerful, method to copy black-box models by querying them with natural random images.
In this work, we consolidate and extend the copycat method. Firstly, some constraints are waived. Secondly, an extensive evaluation with several problems is performed. Thirdly, models are copied between different architectures. Finally, a deeper analysis is performed by looking at the copycat behavior.
Results show that natural random images are effective to generate copycats with similar functionalities w.r.t black-box models for several problems.
