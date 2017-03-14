# file for dose and coverage calibration series
#we should have a series of TPD data .csv for a series of exposures (Pressure x time)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def T_calibration(V):  # convert thermocouple voltage to T (K), here the fit was done >300K
    K0  =  -76.883  
    K1  =  127.71   
    K2  =  0.  
    K3  =  0.    
    K4  =  0. 
    K5  =  0.  
    K6  =  0.
    return K0 + K1*V + K2*V**2 + K3*V**3 + K4*V**4 + K5*V**5 + K6*V**6

#################################
	#def 2nd_peak_fit(T, R_T, x_min,x_max):
	
#	return (theta2_i,E2_d)
#################################

plt.ion()

def calibration_processing():
	global fig, ax1, ax2, df, a_d

	print("Enter filename up to _:")
	filename=input()

	print("Enter number of experiments:")
	N_exp=int(input())

	print("Enter dose list in order, space-separated: (or \"none\" if not available)")
	try :
		dose_list=[int(entry) for entry in input().split()] # could add exception there 
	except ValueError:
		print("Invalid format, dose replaced by integers 1 to "+ str(N_exp))
		dose=[i for i in range(1,N_exp+1)]

	#print("Enter power list in order, space-separated (for cracker only):")
	#power_list=[int(entry) for entry in input().split()]
	
	print("Enter mass of interest in NN.NN format")
	massOfInterest=input()
	
	##Hardcoding input
	#filename="C:\\Users\\fanny\\Desktop\\espec\\141022\\141022"
    #massOfInterest='32.00'
    #N_exp=6
    #dose=[60,50,40,60,40,20,15,10,5,25,30] # here the dose is in s (P=1 10**-6 mbar) ; obtained from labbook    
	#dose=[i for i in range(N_exp)]  #replacement in case no dose available
    
    
	df=[] # list of dataframes; each dataframe contains one experiment
    
	fig, (ax1, ax2) = plt.subplots(2) #two panel figure
	fig.subplots_adjust(hspace=0.3)
    #fig, ax1 = plt.subplots()
    
	area=[]
    
	a_d = pd.DataFrame(
        {
         'dose': dose_list,
         'experiment':[i for i in range(1,N_exp+1)]
        })
    for i in range(1,N_exp+1): #loop on  experiments with different doses 
        
    	###file import and cleanup
    	### "header",0026,"lines"
    	##f = open(filename+'_'+str(i)+".csv")
    	##f.readline()
    	##header_sizeline = [word for word in f.readline().split(sep=',')]
    	##f.close()
    	##header_size=int(header_sizeline[1])+1
    	x=pd.read_csv(filename+'_'+str(i)+".csv") #import data from file ***_i.csv
        cols = [1,-1]
    	x.drop(x.columns[cols],axis=1,inplace=True)#remove useless columns
    	for ii in range(len(list(x))):
            if "32" in list(x)[ii] :
                 col_massOfInterest=list(x)[ii]
    	for iii in range(len(list(x))):
			if "0.40" in list(x)[iii] :
				Temp=list(x)[iii]
    	x.rename(columns={Temp: 'Temp'}, inplace=True)
    	#display R(T) for each experiment on same plot ax1
        x["Temp"]=T_calibration(x["Temp"]) #translate thermocouple V to T (K) in the dataframe
     
    	# here do filter bad data
		ax1.plot(x["Temp"],x[col_massOfInterest],label="exp "+str(i)+' '+str(a_d.ix[i-1,"dose"]) +" L")
    	ax1.set_ylabel("Desorption signal / arb. u.")
		ax1.set_xlabel("T / K")
		ax1.set_xlim(350,660) ##could be automated?
    	legend = ax1.legend(fontsize=8) # legend with label above
    	for label in legend.get_lines(): #few possible tweeks on the legend style 
    		label.set_linewidth(1.5)
    
    	# calculate the peak area:
    		#substract background
    	bg=x[(x.Temp>320) & (x.Temp<350)]
    	bg_2=x[(x.Temp>660) & (x.Temp<780)]
        background=bg[col_massOfInterest].mean()
    	#background_2=bg_2[col_massOfInterest].mean()
    	#background_avg=(background+background_2)/2
    	x[col_massOfInterest]=x[col_massOfInterest]-background
    		#Integrate 350 to 660 K 
    	x_temp=x[(x.Temp>350) & (x.Temp<660)]
    	x_area=np.sum([(x.ix[i,col_massOfInterest]+x.ix[i+1,col_massOfInterest])/2*(x.ix[i+1,"Temp"]-x.ix[i,"Temp"]) for i in x_temp.index])
    	#todo: second peak fitting and substract
		area.append(x_area)
    	df.append(x)
    
    a_d['area']=area
	#a_d['power']=power_list
    a_d=a_d.sort_values("dose")
    a_d=a_d.reset_index(drop=True)
	# here: do filter bad data

	ax2.plot(a_d["dose"],a_d["area"],"ko-")
    ax2.set_ylabel("Area / arb. u.")
	ax2.set_xlabel("Dosage / L")
    print(a_d)
    #show the plot and keep it on

	#linear regression of area vs dosage
	# follow the usual sklearn pattern: import, instantiate, fit 
	from sklearn.linear_model import LinearRegression
	lm = LinearRegression()
	#lm.fit(X, y) (NOTE: X is a list of dimension len(y); each element contains a set of observations for each y_i)
	test=np.array(a_d['dose'])[np.newaxis]
	test=test.T # transpose because a list of one-element lists is needed 
	lm.fit(test,a_d['area'])
	x_lm=[a_d['dose'].min(),a_d['dose'].max()]
	y_lm=x_lm*lm.coef_  + lm.intercept_
	# add fit to graph (red line)
	ax2.plot(x_lm,y_lm,'r',label='fit')
