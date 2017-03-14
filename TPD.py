import math as m
import matplotlib.pyplot as plt
import numpy as np
###TPD model parameters
R=8.3145*10**(-3)
nu_n=9.5*10**(13)
n=2.
theta_list=[0.05,0.1,0.2,0.5,0.8,1.0]
E_des=140.
T_ini=300.
T_fin=17000.
T_prec=2.
def E_int(theta):
     if theta >= 0.25:
	      return 15.8*(theta - 0.25)**(1.3)
     else:
		  return 0
def R_des(theta,nu_n, n,E_des, T):
    return (nu_n)*(theta**n)*(np.exp(-(E_des+E_int(theta))/(R*T)))
fig,ax=plt.subplots()
##############simulate TPD
T_list=[T_ini +z*T_prec for z in range(int((T_fin-T_ini)/T_prec)) ]

for theta_i in theta_list:
	theta=theta_i #initialize theta
	Des_list = []
	for T in T_list:	# build R_des list of values
		desorb = R_des(theta,nu_n,n,E_des,T)
		Des_list.append(desorb)
		theta=theta-desorb # update theta after each step
    ax.plot(T_list,Des_list)

	
##############simulate detection

