"""
/*
 * This script attempts to replicate Fig 2 of Davide's A Thorough Study of LoRaWAN Performance 
 *  Under Different Parameter Settings paper. I want to see the impact that num of devices has on
 * reaching the target arrival rate (packets/sec)
 * 
 * Sim setup
 * No shadowing
 * Trying 100% confirmed, 100% unconfirmed traffic
 * num of trans = 8
 * target data rate sweeped from 10^-2 to 10 pkt/s
 * radius 1200m (assumption, not stated)
 * 1 gateway
 * no ADR, using set SF up
 * packet size 20 bytes, from TR report. Might need to test 32 bytes (only value in paper)
 * GW DC enabled (this is so by default in gateway-lorawan-mac.cc)
 * TX is priorities (this is so by default m_txPriority in lora-phy-helper.h)
 * Sub-band prioritization is Off (by default, sim needs additional code to enable this)
 * RX2 data rate is SF12 (LorawanMacHelper setup for EU function sets this)
 * Number of TX attempts, m = 8 (set in this script  edLorawanMac->SetMaxNumberOfTransmissions (numberOfTransmissions);)
 * Full duplex = No (by default, sim needs additional code for this)
 * Reception paths = 8 (LorawanMacHelper setup for EU function sets this)
 * Number of devices, using 600 (approximated using count_dots.py)
 */
"""

import sem
import numpy as np
import matplotlib.pyplot as plt
import sys
from psutil import virtual_memory

mem = virtual_memory()
available_mem = mem.total


# Create our SEM campaign
script = 'replicate-fig2davide'
results_dir = 'testNumDevices-results'

#Can't get ns-3 path to work on laptop and pc for some reason
#This is a dirty hack, but their amount of RAM differs, using that
#to switch the path.
if(available_mem == 12473401344):
    ns_3_dir = '../../../../../../Desktop/ns-3'
else:
    ns_3_dir = '../../../../../jaco/Desktop/ns-3'


run_new = 1

if(run_new == 1):

    campaign = sem.CampaignManager.new(ns_3_dir, script, results_dir,
                                   check_repo=False, overwrite=False)
else:
    campaign = sem.CampaignManager.load(results_dir)
# Parameter space
#################

#Number of end devices to include in the simulation
nDevices_values = [] #, 1500, 2000]# , 2000]# , 4000 , 10000]

#The radius of the area to simulate
radius_values = [1200]

#The time for which to simulate (Seconds)
simulationTime_values = [600] #10 minutes

#The period in seconds to be used by periodically transmitting applications
appPeriod_values = [30] # every 30 secs

#Whether or not end devices require an ACK
confirmed_values = [False,True]

#Number of repeats (runs) to do for averaging
runs = 1

arrival_rates = list(np.logspace(start= -2, stop=1, num=14))
arrival_rates_printing = []
#print("Arrival rates: ", arrival_rates, " in pkts/s")
totals_required = []
appRates_values= [] #Plan B is to fix devices and vary app rate

for arrival_rate in arrival_rates:
    totals_required.append(arrival_rate*simulationTime_values[0])
    num_required = np.ceil(totals_required[-1]/(simulationTime_values[0]/appPeriod_values[0]))
    nDevices_values.append(num_required)
    nDevices_values.append(num_required*2)
    nDevices_values.append(num_required*5)
    arrival_rates_printing.append(arrival_rate) #appending 3 times due to testing 3 devices values per arrival rate
    arrival_rates_printing.append(arrival_rate)
    arrival_rates_printing.append(arrival_rate)
    print("For ", np.round(arrival_rate,3), " pkt/s. A total of ", np.round(totals_required[-1],3), " pkts in ",
           simulationTime_values[0], " seconds is required. Thus there must be ", np.round(nDevices_values[-3],3), " devices.")





param_combinations = {
    'nDevices': nDevices_values,
    'radius': radius_values,
    'simulationTime': simulationTime_values,
    'appPeriod': appPeriod_values,
    'confirmed' : confirmed_values,
    'print' : False,
}

print(param_combinations)

if(run_new == 1):
    # Run simulations with the above parameter space
    campaign.run_missing_simulations(param_combinations, runs)

example_result = campaign.db.get_complete_results()[0]

def get_arr_rate(result):
    """
    Extract the arrival rate from the simulation output.
    First field is the total packets send 
    """

    outcomes = [float(a) for a in result['output']['stdout'].split()]

    return outcomes[1]/simulationTime_values[0]


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


calculated_arr_rates = np.mean(campaign.get_results_as_numpy_array(param_combinations, get_arr_rate,
                                                         runs),
                    axis=-1).squeeze()



func_list = [get_mac_psucc,  ]# , get_phy_interferedPackets , get_phy_noMoreGwPackets,                get_phy_underSensitivityPackets, get_phy_noMoreTx ]
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
        z = 0 #get PDR value

        avgList = np.squeeze(avg)
        for numNodes in nDevices_values:

            print("PDR for ", numNodes, " devices (conf = ", confirmed_flag, ") : ", np.round(avgList[z].values,2),)
            calc_arrival_rate = calculated_arr_rates[z]
            if(confirmed_flag):
                print("      Calculated arrival rates was ", np.round(calc_arrival_rate[1],2), " goal ", np.round(arrival_rates_printing[z],2))
            else:
                print("       Calculated arrival rates was ", np.round(calc_arrival_rate[0],2), " goal ", np.round(arrival_rates_printing[z],2)) 

            z=z+1

        print(" ")
      
        axs[i].errorbar(x=param_combinations['nDevices'], y=np.squeeze(avg), yerr=6*np.squeeze(std))
        axs[i].set_title(plot_legend_list[i])
        axs[i].set_ylabel("Probability")
        axs[i].set_xticks(param_combinations['nDevices'])
        #axs[i].set_ylim([0,1])
       
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

#plt.show()
