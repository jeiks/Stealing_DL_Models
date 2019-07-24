# (under evaluation) Is Random Non-Labeled Data Enough to Steal Knowledge from Black-box Models and Generate Copycat CNN?

![Copycat](copycat.svg)

Convolutional neural networks have been extremely successful in a wide range of tasks and companies have been developing products based on them. These products use models that result from an expensive process: data is acquired and annotated, then experts have prepare the data and design, implement, and train the models. With all these costs, companies are concerned about the security of their models and deliver them as black-boxes. There are still some vulnerabilities to exploit, though. In a preliminary work, we presented Copycat CNN: a simple, yet powerful, method to copy black-box models by querying them with random natural images. In this work, we consolidate and extend the copycat method by waiving some constraints and performing an extensive evaluation with several problems, copying between different architectures, and presenting a deeper analysis. Results show that random natural images are effective to generate copycat models with similar functionalities to the black-box model.

