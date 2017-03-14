# file for dose and coverage calibration series
#we should have a series of TPD data .csv for a series of exposures (Pressure x time)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
filename="C:\\Users\\fanny\\Desktop\\espec\\141030\\141030"
massOfInterest='32'
dose=[60,50,40,60,40,20,15,10,5,25,30] # here the dose is in s (P=1 10**-6 mbar) ; obtained from labbook
exp_legend={5:'k',10:'b',15:'r',20:'g',25:'purple',30:'brown',40:'yellow',50:'teal',60:'silver'}
def T_calibration(V):  # convert thermocouple voltage to T (K)
    K0  =  -62.088  
    K1  =  347.29   
    K2  =  -163.62  
    K3  =  56.32    
    K4  =  -10.278  
    K5  =  0.94778  
    K6  =  -0.034799
    return K0 + K1*V + K2*V**2 + K3*V**3 + K4*V**4 + K5*V**5 + K6*V**6
df=[] # list of dataframes; each dataframe contains one experiment
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4) #two panel figure
#fig, ax1 = plt.subplots()
area=[]
a_d = pd.DataFrame(
    {
     'dose': dose,
     'experiment':[i for i in range(1,12)]
    })
for i in range(1,12): #loop on 11 experiments with different doses 
    
	#file import and cleanup
	x=pd.read_csv(filename+'_'+str(i)+".csv",header=25) #import data from file ***_i.csv
    x.drop(["Time","Unnamed: 7"],inplace=True,axis=1) #remove useless columns
    
	#display R(T) for each experiment on same plot ax1
    x["Temp"]=T_calibration(x["Temp"]) #translate thermocouple V to T (K) in the dataframe
	if i>3: 
		ax1.plot(x["Temp"],x["Scan 4 : mass 32.00"],exp_legend[a_d.ix[i-1,"dose"]],label="exp "+str(i)+' '+str(a_d.ix[i-1,"dose"]) +" L")
		ax1.set_xlim(350,660) ##could be automated?
		legend = ax1.legend() # legend with label above
		for label in legend.get_lines(): #few possible tweeks on the legend style 
			label.set_linewidth(1.5)
	else:
		ax3.plot(x["Temp"],x["Scan 4 : mass 32.00"],exp_legend[a_d.ix[i-1,"dose"]],label="exp "+str(i)+' '+str(a_d.ix[i-1,"dose"]) +" L")
    	ax3.set_xlim(350,660) ##could be automated?
		legend3 = ax3.legend() # legend with label above
		for label in legend3.get_lines(): #few possible tweeks on the legend style 
			label.set_linewidth(1.5)
			
	# calculate the peak area:
		#substract background
	bg=x[(x.Temp>320) & (x.Temp<350)]
	bg_2=x[(x.Temp>660) & (x.Temp<780)]
    background=bg["Scan 4 : mass 32.00"].mean()
	background_2=bg_2["Scan 4 : mass 32.00"].mean()
	background_avg=(background+background_2)/2
	x["Scan 4 : mass 32.00"]=x["Scan 4 : mass 32.00"]-background_avg
		#Integrate 350 to 660 K 
	x_temp=x[(x.Temp>350) & (x.Temp<660)]
	x_area=np.sum([(x.ix[i,"Scan 4 : mass 32.00"]+x.ix[i+1,"Scan 4 : mass 32.00"])/2*(x.ix[i+1,"Temp"]-x.ix[i,"Temp"]) for i in x_temp.index])
	area.append(x_area)
	df.append(x)

a_d['area']=area
a_d=a_d.sort_values("dose")
a_d=a_d.reset_index(drop=True)
ax2.plot(a_d["dose"],a_d["area"])

#show the plot and keep it on
plt.ion()
plt.show()