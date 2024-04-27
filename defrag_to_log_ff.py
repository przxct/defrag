###############################################################################
#                                                                             #
#    DEFRAG	(DEtection of fetal FRaction And Gender)        				  #
#    Copyright(C) 2014  VU University Medical Center Amsterdam    			  #
#    Authors: 																  #
#	 Daphne van Beek, d.vanbeek@vumc.nl  									  #
#	 Roy Straver, r.straver@vumc.nl                                 		  #
#                                                                             #
#    This script is supplementary to WISECONDOR.                       		  #
#                                                                             #
#    WISECONDOR is free software: you can redistribute it and/or 	  		  #
#	 modify it under the terms of the GNU General Public License as 		  #
#	 published by the Free Software Foundation, either version 3 of the 	  #
# 	 License, or (at your option) any later version.                          #
#                                                                             #
#    WISECONDOR is distributed in the hope that it will be useful,     		  #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with WISECONDOR. If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

import glob
import pickle
import matplotlib
matplotlib.use('Agg')
from pylab import *
import argparse
import numpy as np
import os
import time
import re
    

def getYPerc(sample):
    return sum(sample[testChrom])/sum([sum(sample[chrom]) for chrom in sample])


def getYPercMean(sampleList):
    values=[]
    for sample in sampleList:
        values.append(getYPerc(sampleList[sample]))
    #print "Upper limit: " + str(max(values))
    #print "Lower limit: " + str(min(values))
    #return median(values)
    return mean(values)


def solveFetalFraction(percYMales, percYFemales, percYSample):
    #Based on: %chrY sample = meanY% males * FF + meanY% women with female fetusses * (1 - FF)
    #Taken from: Chiu et al, Non-invasive prenatal assessment of trisomy 21 by multiplexed maternal plasma DNA sequencing: large scale validity study, 2011
    return (percYSample - percYFemales) / (percYMales - percYFemales)
    #return (percYSample - percYFemales) / (percYMales)
            
default_fig = "./DEFRAG_out"
print(default_fig, file=sys.stderr)
#print >> sys.stderr, default_fig

parser = argparse.ArgumentParser(description='DEFRAG \
    (DEtection of fetal FRaction And Gender): \
    Determine fetal gender and fraction in a maternal plasma sample. \
    Can be used with or without a pool of male reference samples. \
    It is recommended to use a male reference set that is processed in the normal labflow to get the best results. \
    \nThis tool can be used in addition to WISECONDOR, as it uses two types of WISECONDOR output as input.\n\n \
    Please set up your reference sets as follows:\n \
    \tCreate two/three directories and place the corresponding .gcc and .pickle files in these directories. You should provide:\n \
    \t- Directory with normal pregnancy samples with male fetus\n \
    \t- Directory with normal pregnancy samples with female fetusses\n \
    \t- Optional directory with male reference samples',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('boydir', type=str,
                    help='Directory containing fetal boy samples to be used as reference (.gcc and .pickle)')
parser.add_argument('girldir', type=str,
                    help='Directory containing fetal girl samples to be used as reference (.gcc and .pickle)')
parser.add_argument('--maledir', type=str,
                    help='Directory containing full male samples to be used as reference (.ggc and .pickle)')	
parser.add_argument('--scalingFactor', type=str, help='Factor that is used for correcting the calculated fetal fraction')	
parser.add_argument('--percYonMales', type=str, help='Percentage of reads that is mapped on Y in males')
parser.add_argument('testdir', type=str,
                    help='Directory containing test samples (gcc and pickle)')
parser.add_argument('outputfig', type=str, default=default_fig, help='prefix of output figure (extension is added by script)')


args = parser.parse_args()


print ('# Script information:')
print ('\n# Settings used:')
argsDict = args.__dict__
argsKeys = sorted(argsDict.keys())
for arg in argsKeys:
    print (('\t').join([arg,str(argsDict[arg])]))


## Load the reference data

girlSamples	= dict()
girlSamplesPickle = dict()
girlFiles = glob.glob(args.girldir + '/*.gcc')
for girlFile in girlFiles:
    print ( sys.stderr, '\tLoading girl gcc:\t' + girlFile )
    curFile = pickle.load(open(girlFile,'rb'))
    girlSamples[girlFile] = curFile
    pic = os.path.splitext(girlFile)[0] + ".pickle"
    print ( sys.stderr, '\tLoading girl pickle:\t' + pic )
    curFile = pickle.load(open(pic,'rb'))
    girlSamplesPickle[pic] = curFile

# if args.maledir:	
#     print (sys.stderr, 'Found directory with male reference samples.')	
#     maleSamples	= dict()
#     maleSamplesPickle = dict()
#     maleFiles = glob.glob(args.maledir + '/*.gcc')
#     for maleFile in maleFiles:
#         print (sys.stderr, '\tLoading man gcc:\t' + maleFile)
#         curFile = pickle.load(open(maleFile,'rb'))
#         maleSamples[maleFile] = curFile
#         pic = os.path.splitext(maleFile)[0] + ".pickle"
#         print (sys.stderr, '\tLoading man pickle:\t' + pic)
#         curFile = pickle.load(open(pic,'rb'))
#         maleSamplesPickle[pic] = curFile

testChrom = 'Y'

# Load the test data

print (sys.stderr, 'Loading test samples')
testSamples	= dict()
testSamplesPickle = dict()
testFiles = glob.glob(args.testdir + '/*.gcc')
for testFile in testFiles:
    print (sys.stderr, '\tLoading test gcc:\t' + testFile)
    samplename = os.path.splitext(testFile)[0]
    curFile = pickle.load(open(testFile,'rb'))
    testSamples[samplename] = curFile
    pic = samplename + ".pickle"
    print (sys.stderr, '\tLoading test pickle:\t' + pic)
    curFile = pickle.load(open(pic,'rb'))
    testSamplesPickle[samplename] = curFile

    
## Determine the backgroud values used for correction of the whole chrY fetal fraction determination

percYGirls = getYPercMean(girlSamplesPickle)

if args.maledir:
    percYMales = getYPercMean(maleSamplesPickle)
else:
    percYMales= 0.00278246251169
    if args.percYonMales:
        percYMales = float(args.percYonMales)

sortedList = sorted(testSamples.keys())

file_ff = open("ff_bam.txt", "w") 

for index,testSample in enumerate(sortedList):
    print(testSample.split('/')[-1])
    
    #Based on: %chrY sample = meanY% males * FF + meanY% women with female fetusses * (1 - FF)

    daphGender = solveFetalFraction(percYMales, percYGirls, getYPerc(testSamplesPickle[testSample]))
    print("DEFRAG whole ChrY: ", daphGender)
    new_line = str(testSample.split('/')[-1]) + " " + str(daphGender * 100) + "\n"
    file_ff.write(new_line)

file_ff.close() 
exit()