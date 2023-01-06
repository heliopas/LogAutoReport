import os
import matplotlib.pyplot as ploterGraph
import pandas as pd
import numpy as np
import operator as op
from tabulate import tabulate
from pathlib import Path

# log source path to be loaded by program
logsfilePath = 'C:/Users/RompkoH/OneDrive - Landis+Gyr/ServTestes/LogMagnoFarmMonitor/AMS/'
# endpoint serial numbers from Farm
endPointfilePath = 'files/endpointcpu.csv'
# meters serial numbers from Farm
metersfilePath = 'files/meters.csv'
# set log quantity to plot in graphs
logPlotqtd = 12

#save processed data frame from all logs to be used to plot graphs and others
global dfArray, dfArrayMerge, resultMerge
dfArray, dfArrayMerge, resultMerge = [], [], []

# load files from folders
def loadFiles():
    global logList, filesName
    filesName , logList  = [], []

    #list all files from log dir
    logsfiles = sorted(Path(logsfilePath).iterdir(), key=os.path.getmtime)

    for aux in range(len(logsfiles)):
        if logsfiles[aux].name.__contains__('log'):
            filesName.append(logsfiles[aux].name)

    # set maximum logs to be displayed on graphs
    if logPlotqtd != 0:
        for aux in range(len(filesName)):
            if aux == logPlotqtd:
                break
            else:
                filesName.pop(0)

    # load file names start with logxx/xx/xxxx.csv
    for aux in range(len(filesName)):
        if filesName[aux].__contains__('log'):
            with open(logsfilePath + filesName[aux], "r", newline='\r\n') as file1:
                logList.append(file1.read())

    #load meter csv files
    with open(metersfilePath, "r", encoding="utf8") as file2:
        global meters
        meters = file2.read()
    return 'Arquivos carregados!!!'

# show log results using tabulate lig
def logMeter():
    loadFiles()
    MeterE212, MeterE223, MeterE234 = 0, 0, 0
    meters = []
    meterFailed = []
    colName = ["Modelo", "Quantidade", "Estado", "Fwver", "Observação"]

    splitParts = endpoint.strip().split('\r\n')

    for aux in range(len(splitParts)):
        if splitParts[aux].__contains__('kWh'):
            meters.append(splitParts[aux])
            if splitParts[aux].__contains__('Magno Grid - E212'):
                MeterE212=MeterE212+1
            if splitParts[aux].__contains__('Magno Grid - E223'):
                MeterE223=MeterE223+1
            if splitParts[aux].__contains__('Magno Grid - E234'):
                MeterE234=MeterE234+1
            if not splitParts[aux].__contains__('Normal'):
                meterFailed.append(splitParts[aux])
                if splitParts[aux].__contains__('Magno Grid - E212'):
                    MeterE212 = MeterE212 - 1
                if splitParts[aux].__contains__('Magno Grid - E223'):
                    MeterE223 = MeterE223 - 1
                if splitParts[aux].__contains__('Magno Grid - E234'):
                    MeterE234 = MeterE234 - 1

    result = [['Magno Grid - E212', MeterE212, 'Normal', '01.00.03'],['Magno Grid - E223',MeterE223, 'Normal', '01.00.03'],['Magno Grid - E234',MeterE234, 'Normal', '01.00.03']]
    print(tabulate(result, headers=colName, tablefmt="fancy_grid"))

    result.clear()

    for aux in range(len(meterFailed)):
        result.append([meterFailed[aux].split(',')[6], '----', meterFailed[aux].split(',')[2], meterFailed[aux].split(',')[7], meterFailed[aux].split(',')[0]])

    print(tabulate(result, headers=colName, tablefmt="fancy_grid"))

# convert log data to dataframe structure
def logtodataFrame():
    meterOrded, kWhOrded, endpoint, meterLanID, meterplotGraph  = [], [], [], [], []
    data = {}

    #split meter from file using \n delimiter
    meterLanIDfile = meters.split('\n')
    meterLanID = []
    meterplotGraph = []

    # if contains 0 meter will be tested if not test will skip it
    for aux in range(len(meterLanIDfile)):
        if meterLanIDfile[aux].__contains__(',0'):
            meterLanID.append(meterLanIDfile[aux])

    for aux in range(len(logList)):
        counter = aux
        endpoint = logList[aux]
        devide = endpoint.strip().split('\r\n')

        medidor, consumo  = [], []
        plotmeter, plotkWh = [], []

        # remove from line Initial/Latest kWh 0 / and keep only the consuption value
        for aux in range(len(devide)):
            if devide[aux].__contains__('kWh'):
                medidor.append(devide[aux].split(',')[0])
                aux = devide[aux].split(',')[3].removeprefix('Initial/Latest kWh 0 /').strip()
                consumo.append(aux)

        # convert the consuption value from each meter from string to float
        for aux in range(len(consumo)):
            if consumo[aux] != '':
                conv = '{0:2f}'.format(float(consumo[aux]))
                consumo[aux] = conv
            else: # if there isn't consuption information then value is 0
                consumo[aux] = '0'

        # remove ,0 from meter serial number and store it in plotmeter plotkWh to plot them in graphs
        for aux in range(len(meterLanID)):
            try:
                index = medidor.index(meterLanID[aux].removesuffix(',0'))
                plotmeter.append(medidor[index])
                plotkWh.append(float(consumo[index]))
            except ValueError:
                plotmeter.append(meterLanID[aux].removesuffix(',0'))
                plotkWh.append(float(0))

        # get meters for plot reference, they will used to plot all meters logs
        if len(meterplotGraph) == 0:
            meterplotGraph = plotmeter

        # ploterGraph.title('Gráfico de consumo - Monitoramento')
        # ploterGraph.xlabel('Medidor')
        # ploterGraph.ylabel('kWh')

        data = { 'meter': meterplotGraph, 'kWh': plotkWh }
        df = pd.DataFrame(data)
        df.sort_values('kWh', ascending=True)

        dfArray.append(df)

    #     ploterGraph.plot('meter', 'kWh' , data=df,label=filesName[counter])
    #     ploterGraph.draw()
    #
    # ploterGraph.legend()
    #ploterGraph.show()

# merge data from small data frames to commum data frame
def mergeDf():
    global resultMerge
    for aux in range(len(dfArray)):
        if len(dfArrayMerge) == 0:
            dfArrayMerge.append(dfArray[aux].meter)
            dfArrayMerge.append(dfArray[aux].kWh)
        else:
            dfArrayMerge.append(dfArray[aux].kWh)

    resultMerge = pd.concat(dfArrayMerge, axis=1, join="inner")
    return resultMerge

# this function generete consuption graph from monitoring system
def plotconsuptionGraph():
    ploterGraph.title('Gráfico de consumo - Monitoramento')
    ploterGraph.xlabel('Medidor')
    ploterGraph.ylabel('kWh')
    ploterGraph.plot('meter', 'kWh', data=resultMerge, label=filesName)
    ploterGraph.legend()
    ploterGraph.show()

def plotconsuptionIndividual():
    # mean calculation
    resultMerge['mean'] = resultMerge.mean(axis=1, numeric_only=float)
    # subtract the consumption value from last log days
    resultMerge['sub'] = resultMerge.iloc[:, (resultMerge.columns.size-2)] - resultMerge.iloc[:, (resultMerge.columns.size-3)]

    fig, axs = ploterGraph.subplots(2)

    fig.suptitle('Consumo em kWh P/dia')
    ploterGraph.xlabel('Medidor')
    ploterGraph.ylabel('kWh')
    #plot value from last days logs
    axs[0].plot('meter', 'sub', data=resultMerge)

    ploterGraph.title('Histograma de consumo')
    axs[1].hist(x=resultMerge['sub'], bins=15, align='mid', histtype='bar')
    ploterGraph.show()


print(loadFiles())
#logMeter()
logtodataFrame()
mergeDf()
plotconsuptionGraph()
plotconsuptionIndividual()
