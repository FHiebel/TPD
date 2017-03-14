#test effect of sampling on peak area this time we want to bin values
import math as m
import matplotlib.pyplot as plt
import numpy as np
###TPD model parameters
R=8.3145*10**(-3)
nu_n=9.5*10**(13)
n=2.
theta=0.5
E_des=140.
T_ini=400.
T_fin=600
T_ideal_prec=1.
def E_int(theta):
     if theta >= 0.25:
	      return 15.8*(theta - 0.25)**(1.3)
     else:
		  return 0
def R_des(theta,nu_n, n,E_des, T):
    return (nu_n)*(theta**n)*(np.exp(-(E_des+E_int(theta))/(R*T)))

fig, (ax1, ax2) = plt.subplots(2) #two panels
##############simulate TPD
T_prec_list=[float(x) for x in range(1,20)]



T_list=[T_ini +z*T_ideal_prec for z in range(int((T_fin-T_ini)/T_ideal_prec)) ]
Des_list = []
theta=1.0
for T in T_list:	# build R_des list of values
	desorb = R_des(theta,nu_n,n,E_des,T)
	Des_list.append(desorb)
	theta=theta-desorb # update theta after each step
	if theta<0:
		theta=0
ax1.plot(T_list,Des_list,'k',lw=1)
ax1.fill_between(T_list, 0, Des_list,alpha=0.1)

##############simulate detection
A=[]
for T_prec_i in T_prec_list:
    print(T_prec_i)
	index_sample=[ii for ii in range(len(Des_list)-int(T_prec_i)-1) if ii%T_prec_i==0]
    A_Des=[]
	Des_list_sampled=[]
    for i in index_sample:
        temp=[Des_list[i+j] for j in range(int(T_prec_i)+1)]
		Des_list_sampled.append(np.sum(temp)/(T_prec_i+1))
		A_Des.append(np.sum(temp)/(T_prec_i+1)*(T_prec_i))
	A.append(np.sum(A_Des))
	
	T_list_sampled=[T_list[ii+int(T_prec_i/2)] for ii in index_sample] 
	ax1.plot(T_list_sampled,Des_list_sampled)

ax2.plot(T_prec_list,A)

	


