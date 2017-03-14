# file for dose and coverage calibration series
#we should have a series of TPD data .csv for a series of exposures (Pressure x time)
from __future__ import division
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression



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
    
#    return (theta2_i,E2_d)
#################################

plt.ion()

def calibration_processing():
    global fig1, fig2, ax11, ax21, ax22, ax23, df, a_d, x

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
    
    fig1, (ax11) = plt.subplots(1) 
    fig2, (ax21, ax22, ax23)=plt.subplots(3) #two panel figure
	#fig.subplots_adjust(hspace=0.3)
    #fig, ax11 = plt.subplots()
    
    area=[] # peak area list
	maxT=[] # list of T at maximum 
	cross=[] # list of values at cross point, here to detect the presence of low T peak
    
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
        cols = [0,-1]
        x.drop(x.columns[cols],axis=1,inplace=True)#remove useless columns
        for ii in range(len(list(x))):
            if "32" in list(x)[ii] :
               col_massOfInterest=list(x)[ii]
        for iii in range(len(list(x))):
            if "0.40" in list(x)[iii] :
                Temp=list(x)[iii]
        x.rename(columns={Temp: 'Temp'}, inplace=True)
        #display R(T) for each experiment on same plot ax11
        x["Temp"]=T_calibration(x["Temp"]) #translate thermocouple V to T (K) in the dataframe
     
        # here do filter bad data
		
        #set min to zero for mass of interest
		x[col_massOfInterest] = x[col_massOfInterest] - x[col_massOfInterest].min() 
        
		x[col_massOfInterest] = x[col_massOfInterest]*10**7 # more reasonable values to display
		
		# calculate the peak area: 
        x_temp=x[(x.Temp>350) & (x.Temp<660)]
        x_area=np.sum([(x.ix[i,col_massOfInterest]+x.ix[i+1,col_massOfInterest])/2*(x.ix[i+1,"Temp"]-x.ix[i,"Temp"]) for i in x_temp.index])
        #todo: second peak fitting and substract
        area.append(x_area)
        df.append(x)
		
		#calculate temperature at maximum
		x_maxT_index=x_temp[col_massOfInterest].idxmax()
		x_maxT=x_temp.ix[x_maxT_index,'Temp']
		maxT.append(x_maxT)
		
		#get a cross section at 470 K to probe the first peak
		cross_value=470
		x_cross_index=pd.Series(x[x['Temp'] <= cross_value].index.tolist())
		x_cross=x.ix[x_cross_index.max(),col_massOfInterest]
		cross.append(x_cross)
		
		x[col_massOfInterest] = x[col_massOfInterest] + (i-1)*0.1  # distribute curves
		
		ax11.plot(x["Temp"],x[col_massOfInterest],'k',label=str(a_d.ix[i-1,"dose"]) +" s")
		ax11.fill_between(x["Temp"], x[col_massOfInterest], (i-1)*0.1,facecolor='grey', edgecolor='grey',interpolate=True)
        ax11.set_ylabel("Desorption signal / arb. u.",size=16)
        ax11.set_xlabel("T / K",size=16)
        ax11.set_xlim(350,660) ##could be automated?
        legend = ax11.legend(fontsize=16) # legend with label above
        for label in legend.get_lines(): #few possible tweeks on the legend style 
            label.set_linewidth(1.5)
		handles, labels = ax11.get_legend_handles_labels()
		ax11.legend(handles[::-1], labels[::-1], loc='lower right')
    
	ax11.vlines(cross_value,0,3.5, lw=2, color='r')
	
    a_d['cross']=cross
	a_d['maxT']=maxT
    a_d['area']=area
    #a_d['power']=power_list
    a_d=a_d.sort_values("dose")
    a_d=a_d.reset_index(drop=True)
    # here: do filter bad data

    ax21.plot(a_d["dose"],a_d["area"],"ko-")
    ax21.set_ylabel("Area / arb. u.",size=16)
    ax21.set_xlabel("Dosage / s",size=16)
	
	ax22.plot(a_d["dose"],a_d["maxT"],"ko-")
	ax22.set_ylabel("Temperature at maximum / K",size=16)
    ax22.set_xlabel("Dosage / s",size=16)
	ax22.vlines([420,510],530,565, lw=1, color='r')
	ax22.vlines([840,1020],530,565, lw=1, color='r')
    
	ax23.plot(a_d["dose"],a_d["cross"],"ko-")
	ax23.set_ylabel("Value at "+str(cross_value)+" K / arb. u.",size=16)
    ax23.set_xlabel("Dosage / s",size=16)
	print(a_d)

    #linear regression of area vs dosage
    # follow the usual sklearn pattern: import, instantiate, fit 
    #lm = LinearRegression()
    #lm.fit(X, y) (NOTE: X is a list of dimension len(y); each element contains a set of observations for each y_i)
    #test=np.array(a_d['dose'])[np.newaxis]
    #test=test.T # transpose because a list of one-element lists is needed 
    #lm.fit(test,a_d['area'])
    #x_lm=[a_d['dose'].min(),a_d['dose'].max()]
    #y_lm=x_lm*lm.coef_  + lm.intercept_
    # add fit to graph (red line)
    #ax21.plot(x_lm,y_lm,'r',label='fit')
	
	    #linear regression of area vs dosage for the 2d order regime
    # follow the usual sklearn pattern: import, instantiate, fit 
    a_d_2nd_O=a_d[a_d['dose']<=420]
	lm = LinearRegression()
    #lm.fit(X, y) (NOTE: X is a list of dimension len(y); each element contains a set of observations for each y_i)
    test=np.array(a_d_2nd_O['dose'])[np.newaxis]
    test=test.T # transpose because a list of one-element lists is needed 
    lm.fit(test,a_d_2nd_O['area'])
    x_lm=[a_d['dose'].min(),a_d['dose'].max()]
    y_lm=x_lm*lm.coef_  + lm.intercept_
    # add fit to graph (red line)
    ax21.plot(x_lm,y_lm,'r',label='fit_2nd_O')
	print("Area="+str(lm.coef_) +' x Dosage'+str(lm.intercept_))
