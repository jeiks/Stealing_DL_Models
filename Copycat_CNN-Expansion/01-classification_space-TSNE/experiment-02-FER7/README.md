Firstly, 1000 examples per class were selected from ODD.<br>
The vectors referred to are in:
[FER7-OD-1000.txt](https://drive.google.com/open?id=1h-ak_IdV0eNLyCbEYCIN346ZDGcqdqD5)

After, 200000 examples were selected from NPDD.<br>
The vectors referred to are in:
[FER7_Original_NPD-a.txt](https://drive.google.com/open?id=1h-ak_IdV0eNLyCbEYCIN346ZDGcqdqD5),
[FER7_Original_NPD-b.txt](https://drive.google.com/open?id=1h-ak_IdV0eNLyCbEYCIN346ZDGcqdqD5)

Then the examples per class was counted and 3200 vectors<br>
per class were maintained:
[FER7-NPD-gray-3200.txt](https://drive.google.com/open?id=1h-ak_IdV0eNLyCbEYCIN346ZDGcqdqD5)<br>
note: the NPDD used to FER7 is in grayscale

Command to run T-SNE:<br>
`$ ./tsne.py FER7-OD-1000.txt FER7-NPD-3200.txt`
