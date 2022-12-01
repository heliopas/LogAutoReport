import os
import matplotlib.pyplot as ploterGraph
import pandas as pd
import numpy as np
import operator as op
from tabulate import tabulate

logsfilePath = 'files/'

def loadFiles():
    global logList
    global filesName
    filesName = []
    logList = []
    #lista arquivos do diretório
    for logfiles in os.listdir(logsfilePath):
        if logfiles.startswith('log'):
            filesName.append(logfiles)
    #carrega arquivos com nome logxx/xx/xxxx.csv

    for aux in range(len(filesName)):
        if filesName[aux].startswith('log'):
            with open(logsfilePath + filesName[aux], "r", newline='\r\n') as file1:
                logList.append(file1.read())

    return 'Arquivos carregados!!!'

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

def plotGraph():

    endpoint =[]

    for aux in range(len(logList)):
        counter = aux
        endpoint = logList[aux]

        devide = endpoint.strip().split('\r\n')

        medidor = []
        consumo = []

        for aux in range(len(devide)):
            if devide[aux].__contains__('kWh'):
                medidor.append(devide[aux].split(',')[0])
                aux = devide[aux].split(',')[1].removeprefix('Initial/Latest kWh 0 /').strip()
                consumo.append(aux)

        print(medidor+consumo)

        ploterGraph.title('Grafico de consumo')
        ploterGraph.xlabel('Medidor')
        ploterGraph.ylabel('kWh')

        for aux in range(len(consumo)):
            if consumo[aux] != '':
                conv = '{0:2f}'.format(float(consumo[aux]))
                consumo[aux] = conv
            else:
                consumo[aux] = '0'

        consumoFloat = np.array(consumo)
        floatarray = consumoFloat.astype(float)

        zipList = zip(floatarray, medidor)
        sorlist = sorted(zipList)

        aux = zip(*sorlist)
        consumo, medidor = [ list(aux1) for aux1 in aux]

        ploterGraph.plot(medidor, consumo, label= filesName[counter])
        ploterGraph.legend()

        ploterGraph.draw()
    ploterGraph.show()


print(loadFiles())
#logMeter()
plotGraph()

