"""
Attempting to replicate figure 3 from Martina's paper Confirmed traffic in LoRaWAN:pitfalls and countermeasures.

I don't know the simulation duration, trying 1 day.
Packet size? using 20 bytes as this is in the TR 45.820 report for MAR reporting.

"""

import sem
import numpy as np
import matplotlib.pyplot as plt
import sys
from psutil import virtual_memory

mem = virtual_memory()
available_mem = mem.total





# Create our SEM campaign
script = 'replicate-martina'
results_dir = 'replicate-martina-results'

#Can't get ns-3 path to work on laptop and pc for some reason
#This is a dirty hack, but their amount of RAM differs, using that
#to switch the path.
if(available_mem == 12473401344):
    ns_3_dir = '../../../../../Desktop/ns-3'
else:
    ns_3_dir = '../../../../jaco/Desktop/ns-3'


run_new = 1

if(run_new == 1):

    campaign = sem.CampaignManager.new(ns_3_dir, script, results_dir,
                                   check_repo=False, overwrite=False)
else:
    campaign = sem.CampaignManager.load(results_dir)
# Parameter space
#################

#Number of end devices to include in the simulation
nDevices_values = [100, 500, 1000, 1500, 2000 ] #, 1500, 2000]# , 2000]# , 4000 , 10000]

#The radius of the area to simulate
radius_values = [1200]

#The time for which to simulate (Seconds)
simulationTime_values = [86400] #60 x 60 x 24 = 86400

#The period in seconds to be used by periodically transmitting applications
appPeriod_values = [30*60] # every 30 mins

#Whether or not end devices require an ACK
confirmed_values = [True]

#Number of repeats (runs) to do for averaging
runs = 10

param_combinations = {
    'nDevices': nDevices_values,
    'radius': radius_values,
    'simulationTime': simulationTime_values,
    'appPeriod': appPeriod_values,
    'confirmed' : confirmed_values,
    'print' : False,
}

if(run_new == 1):
    # Run simulations with the above parameter space
    campaign.run_missing_simulations(param_combinations, runs)

example_result = campaign.db.get_complete_results()[0]



def get_mac_psucc(result):
    """
    Extract the probability of success from the simulation output.
    First two fields are mac related, the rest is phy
    """

    outcomes = [float(a) for a in result['output']['stdout'].split()]

    return outcomes[1]/outcomes[0]


def get_phy_receivedPackets(result):
    """
    Extract the probability of success from the simulation output.
    From lora-packet-tracker.cc
    Vector packetCounts will contain the following fields: totPacketsSent receivedPackets
    interferedPackets noMoreGwPackets underSensitivityPackets noMoreTx

    but result first has 2 fields which where mac output
    """

    outcomes = [float(a) for a in result['output']['stdout'].split()]

    return outcomes[3]/outcomes[2]

def get_phy_interferedPackets(result):
    """
    Extract the probability of success from the simulation output.
    From lora-packet-tracker.cc
    Vector packetCounts will contain the following fields: totPacketsSent receivedPackets
    interferedPackets noMoreGwPackets underSensitivityPackets noMoreTx

    but result first has 2 fields which where mac output
    """

    outcomes = [float(a) for a in result['output']['stdout'].split()]

    return outcomes[4]/outcomes[2]

def get_phy_noMoreGwPackets(result):
    """
    Extract the probability of success from the simulation output.
    From lora-packet-tracker.cc
    Vector packetCounts will contain the following fields: totPacketsSent receivedPackets
    interferedPackets noMoreGwPackets underSensitivityPackets noMoreTx

    but result first has 2 fields which where mac output
    """

    outcomes = [float(a) for a in result['output']['stdout'].split()]

    return outcomes[5]/outcomes[2]

def get_phy_underSensitivityPackets(result):
    """
    Extract the probability of success from the simulation output.
    From lora-packet-tracker.cc
    Vector packetCounts will contain the following fields: totPacketsSent receivedPackets
    interferedPackets noMoreGwPackets underSensitivityPackets noMoreTx

    but result first has 2 fields which where mac output
    """

    outcomes = [float(a) for a in result['output']['stdout'].split()]

    return outcomes[6]/outcomes[2]

def get_phy_noMoreTx(result):
    """
    Extract the probability of success from the simulation output.
    From lora-packet-tracker.cc
    Vector packetCounts will contain the following fields: totPacketsSent receivedPackets
    interferedPackets noMoreGwPackets underSensitivityPackets noMoreTx

    but result first has 2 fields which where mac output
    """

    outcomes = [float(a) for a in result['output']['stdout'].split()]

    return outcomes[7]/outcomes[2]



#print(results_std)

# Plot lines with error bars
fig, axs = plt.subplots(6, frameon = False) #,sharex=True, sharey=True
#fig.figsize = [12,12]
fig.dpi = 100

#plt.figure(figsize=[6, 6], dpi=100)
legend_entries = []

func_list = [get_mac_psucc, get_phy_receivedPackets, get_phy_interferedPackets , get_phy_noMoreGwPackets,
                get_phy_underSensitivityPackets, get_phy_noMoreTx ]
plot_legend_list = ["MAC success", "PHY success", "PHY interfered", "PHY lost NoMoreGw", "PHY lost sensitivity", "PHY lost GW TX"]

i= 0
for index, func in enumerate(func_list):
    results = campaign.get_results_as_xarray(param_combinations,
                                                func, '', runs)

    print("\nResults for ", plot_legend_list[i], "\n")
    results_average = results.reduce(np.mean, 'runs')
    results_std = results.reduce(np.std, 'runs')

    for confirmed_flag in param_combinations['confirmed']:

        avg = results_average.sel(confirmed=confirmed_flag)
        std = results_std.sel(confirmed=confirmed_flag)

        #iterate through for printing
        z = 0
        avgList = np.squeeze(avg)
        for numNodes in nDevices_values:

            if(index == 0 or index == 1): #First two are mac succ and phy succ, want to convert to loss percentage
                print("Loss perc For ", numNodes, " devices (conf = ", confirmed_flag, ") : ", 1- avgList[z].values)
            else:
                print("Loss perc For ", numNodes, " devices (conf = ", confirmed_flag, ") : ", avgList[z].values)

            z=z+1
        
        axs[i].errorbar(x=param_combinations['nDevices'], y=np.squeeze(avg), yerr=6*np.squeeze(std))
        axs[i].set_title(plot_legend_list[i])
        axs[i].set_ylabel("Probability")
        axs[i].set_xticks(param_combinations['nDevices'])
        axs[i].set_ylim([0,1])
       
        if( i == 2): #add legend to the right of second subfigure

          if(len( param_combinations['confirmed']) == 2):  #test to see if we are showing both types or only confirmed
            lgd =  axs[i].legend(['Unconfirmed', 'Confirmed'], title = "Traffic type", loc=(1.01,0.5))
          else:
            lgd =  axs[i].legend(['Confirmed'], title = "Traffic type", loc=(1.01,0.5))
    i=i+1



plt.xlabel("Number of End Devices")
plt.subplots_adjust(right = 0.85, hspace = 1.3) # give legend some space + increase space betwween subplots to show titles

mac_results = campaign.get_results_as_numpy_array(param_combinations, get_mac_psucc, runs)

#print("mac_results", np.array2string(mac_results, separator=', '), " shape ", mac_results.shape)

mac_succprobs = np.mean(campaign.get_results_as_numpy_array(param_combinations, get_mac_psucc,
                                                         runs),
                    axis=-1).squeeze()


#print("mac_results averaged ",  np.mean(mac_succprobs,axis = -1)) 
#print("mac squeezed",  np.mean(mac_succprobs,axis = -1).squeeze() )

phy_receivedPackets  = np.mean(campaign.get_results_as_numpy_array(param_combinations, get_phy_receivedPackets,
                                                         runs),
                    axis=-1).squeeze()

#print("PHY received ",campaign.get_results_as_numpy_array(param_combinations, get_phy_receivedPackets,
#                                        runs))

phy_interferedPackets  = np.mean(campaign.get_results_as_numpy_array(param_combinations, get_phy_interferedPackets,
                                                         runs),
                    axis=-1).squeeze()

phy_noMoreGwPackets  = np.mean(campaign.get_results_as_numpy_array(param_combinations, get_phy_noMoreGwPackets,
                                                         runs),
                    axis=-1).squeeze()
phy_underSensitivityPackets  = np.mean(campaign.get_results_as_numpy_array(param_combinations, get_phy_underSensitivityPackets,
                                                         runs),
                    axis=-1).squeeze()

phy_noMoreTx  = np.mean(campaign.get_results_as_numpy_array(param_combinations, get_phy_noMoreTx,
                                                         runs),
                    axis=-1).squeeze()



# print("phy_results", phy_receivedPackets)
# print("phy_interf", phy_interferedPackets)
# print("phy_gw", phy_noMoreGwPackets)
# print("phy_sen", phy_underSensitivityPackets)
# print("phy_tx", phy_noMoreTx)

plt.show()
