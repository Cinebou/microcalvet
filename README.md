# Data processing of microcalvet
1. Set the name of the file and mass adsorbent in function 'ads_heat_data_plot'. The file can be the raw output from MicroCalvet Data Processing. Depending on the output csv format of software, you need to change encoding style in line 49 or 50.

2. Run 'python microcalvet.py'. 

3. This code detects the sudden pressure change, by equation d2P/dt2 > 0.0028. The detected index of pressure change is stored.

4. In the folder 'Fig', pressure curve and heat flux curve are shown with red circle that indicates the pressure change point. You can see whether this code preperly detect the pressure change. If it doesn't work, you need to change the coefficient 'coeff_judge', (default 0.0028).

5. The integral of the heat is calculated and stored in the 'Results' folder. It calculate the Q_integral between each red circle of the graph.

