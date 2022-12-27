import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from os import path, mkdir
if not path.exists('Fig'):
    mkdir('./Fig')
    mkdir('./Results')
plt.rcParams["font.size"] = 24
plt.rcParams["font.family"] = "Times New Roman"


# base line construct!!!!

def main():
    ads_heat_data_plot()

def ads_heat_data_plot():
    file = '1211-UiO66-adsorption-303K_1.csv'
    mass = 24.4 / 1000 # g
    mof = MicroCalvet(file,mass)

class MicroCalvet():
    def __init__(self, file_name,mass):
        self.file_name = file_name
        self.mass = mass

        # set index pre
        self.index_before = 1

        name_column = ['time(min)', 'T_furnace', 'T_sample', 'HeatFlow','Pressure(Gauge)']
        self.exp_data = pd.read_csv(self.file_name, skiprows=13,header=None,names=name_column,sep='\t',encoding='UTF-16 LE')
        self.__modify_unit()
        self.p_change_index = self.pressure_change_time()
        self.pressure_level, self.heat_level = self.pressure_at_each_step()
        self.heatflow_integral(self.p_change_index[1],self.p_change_index[2])
        self.Qads_list = self.heatflow_all()
        self.plot_data_P()
        self.plot_data_W()

        data_all = [self.pressure_level[:-1]] + [self.pressure_level[1:]]+ [self.Qads_list]
        data_all = pd.DataFrame(data_all).T
        data_all.to_csv('./Results/'+self.file_name.replace('.csv','data_sum.csv'),index=None,header=['low pressure(MPa)','high pressure(MPa)','H_ads(J/g)'])

    # modify the output unit
    def __modify_unit(self):
        self.time = self.exp_data['time(min)'] * 60 # sec
        self.pressure = self.exp_data['Pressure(Gauge)'] + 0.1 # MPa
        self.heatflow = self.exp_data['HeatFlow'] * 0.001 # W

    # detect the pressure change time
    def pressure_change_time(self):
        p_change_index = [0]
        self.step_time = []
        for i in range(1, len(self.pressure)):
            if self.pressure[i] > self.pressure[i-1] + 0.005: # when pressure increases by 0.005 MPa
                if max(p_change_index) + 80 < i: # don't record in the same step
                    p_change_index.append(i-self.index_before)
                    self.step_time.append(self.time[i-self.index_before])
        
        # add last step
        last_index = len(self.pressure) - self.index_before
        p_change_index.append(last_index)
        self.step_time.append(self.time[last_index])

        print("time steps \n",[self.time[i] for i in p_change_index])
        return p_change_index


    # define the pressure at each step,
    # using the last sec pressure
    def pressure_at_each_step(self):
        pressure_level = []
        heat_level = []
        for i in range(1,len(self.p_change_index)):
            pressure_level.append(self.pressure[self.p_change_index[i]])
            heat_level.append(self.heatflow[self.p_change_index[i]])
        print("pressure steps \n",pressure_level)
        return np.array(pressure_level), np.array(heat_level)


    # calc sum of heat
    def heatflow_integral(self, start, fin):
        # adsorption heat
        Qads_each = integrate.cumtrapz(self.heatflow[start: fin],self.time[start:fin])
        
        # baseline construction
        heat_baseline = (self.heatflow[start] + self.heatflow[fin]) / 2
        Q_baseline = heat_baseline * (self.time[fin] - self.time[start])
        return Qads_each[-1] - Q_baseline

    
    # calc for all 
    def heatflow_all(self):
        Qheat = []
        for each_step in range(1, len(self.p_change_index)):
            start = self.p_change_index[each_step-1]
            fin = self.p_change_index[each_step]
            #print(self.time[start],self.time[fin])
            Qheat.append(self.heatflow_integral(start,fin))
        return np.array(Qheat[1:]) / self.mass


    # plot data for pressure
    def plot_data_P(self):
        fig = plt.figure(figsize=(9,6))
        ax = fig.add_subplot(111)
        ax.plot(self.time,self.pressure,label='Pressure (MPa)')
        ax.scatter(self.step_time,self.pressure_level,s=20, facecolors='none', edgecolors='r')
        ax.set_xlabel('time [sec]')
        ax.set_ylabel('Pressure [MPa]')
        #ax.legend(loc='upper left', borderaxespad=0)
        ax.grid()
        fig.savefig('./Fig/'+self.file_name.replace('.csv','pres.png'))

    # plot data for heat flow
    def plot_data_W(self):
        fig = plt.figure(figsize=(9,6))
        ax = fig.add_subplot(111)
        ax.plot(self.time,self.heatflow,label='HeatFlow(mW)')
        ax.scatter(self.step_time,self.heat_level,s=20, facecolors='none', edgecolors='r')
        ax.set_xlabel('time [sec]')
        ax.set_ylabel('HeatFlow [W]')
        #ax.legend(loc='upper left', borderaxespad=0)
        ax.set_ylim(-0.0015, 0.01)
        #ax.set_ylim(-0.0005, 0.0005)
        #ax.set_xlim(7600,8200)
        ax.grid()
        fig.savefig('./Fig/'+self.file_name.replace('.csv','work.png'))


if __name__=='__main__':
    main()