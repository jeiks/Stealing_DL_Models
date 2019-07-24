## Data Curve

All data curve plots were generated using the script [plot-data_curve.py](plot-data_curve.py) <br>
The data from [data.csv](data.csv) was used inside the script to create each plot. <br>
After, the inkscape was used to join all plots in one Figure.

**The _data.csv_ must have the following format for each problem:<br>**
Problem: _PROBLEM_NAME_<br>
_LABELS_ (we used "# images,Target Network,Macro – NPDD-SL,Macro – NPDD-SL+PDD-SL_SL")<br>
1,_Na1_,_Na2_,_Na3_ <br>
100000,_Nb1_,_Nb2_,_Nb3_ <br>
500000,_Nc1_,_Nc2_,_Nc3_ <br>
1000000,_Nd1_,_Nd2_,_Nd3_ <br>
1500000,_Ne1_,_Ne2_,_Ne3_ <br>
3000000,_Nf1_,_Nf2_,_Nf3_ <br>

Being N{a,...,f}{1,2,3} the Macro Accuracies for Target Network, NPDD-SL, and NPDD+PDD-SL, respectively, for each dataset size.

To create the file [data.csv](data.csv), you can use LibreOffice writer.<br>
The original values are in file [Results.ods](../Results/Results.ods)

To create the data curve plots, run:
```shell
chmod +x plot-data_curve.py
./plot-data_curve.py
```
