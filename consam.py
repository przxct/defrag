##############################################################################
#                                                                            #
#    Convert and filter SAM formatted input stream to a pickled list.        #
#    Copyright(C) 2013  TU Delft & VU University Medical Center Amsterdam    #
#    Author: Roy Straver, r.straver@vumc.nl                                  #
#                                                                            #
#    This file is part of WISECONDOR.                                        #
#                                                                            #
#    WISECONDOR is free software: you can redistribute it and/or modify      #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation, either version 3 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    WISECONDOR is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU General Public License for more details.                            #
#                                                                            #
#    You should have received a copy of the GNU General Public License       #
#    along with WISECONDOR.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                            #
##############################################################################



import sys
import pickle
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import json 

parser = argparse.ArgumentParser(description='Convert any stream of reads to a pickle file for WISECONDOR, defaults are set for the SAM format',
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-outfile', type=str,
					help='reference table output, used for sample testing (pickle)')

parser.add_argument('-keepfile', type=str,
					help='unaltered output of reads used in analysis')
parser.add_argument('-dropfile', type=str,
					help='unaltered output of reads ignored in analysis')
parser.add_argument('-keepprint', action='store_true',
					help='unaltered output of reads used in analysis to stdout')

parser.add_argument('-binsize', type=int, default=1000000,
					help='binsize used for samples')
parser.add_argument('-retdist', type=int, default=4,
					help='maximum amount of base pairs difference between sequential reads to consider them part of the same tower')
parser.add_argument('-retthres', type=int, default=4,
					help='threshold for when a group of reads is considered a tower and will be removed')
parser.add_argument('-colchr', type=int, default=2,
					help='column containing chromosome, default is for sam format')
parser.add_argument('-colpos', type=int, default=3,
					help='column containing read start position, default is for sam format')

args = parser.parse_args()

print("args: ", args)
npz = prefix = os.path.basename(args.outfile).rsplit('.', 1)[0]
npz = "/Users/nguyenngocanh/Desktop/lab/seqff/real_data/npz_negatives/train_seqff/" + npz + ".npz"
print(npz)

binsize		= args.binsize
minShift 	= args.retdist
threshold	= args.retthres
chrColumn	= args.colchr
startColumn	= args.colpos

# Prepare the list of chromosomes
chromosomes = dict()
for chromosome in range(1,23):
	chromosomes[str(chromosome)] = []
chromosomes['X'] = []
chromosomes['Y'] = []


def list_bincount():
	z = np.load(npz, allow_pickle=True, mmap_mode='r', encoding='latin1')

	reads = 0
	for item in z.files:
		if (item == "sample"):
			list_chr = z[item].tolist()
			for chr in list_chr:
				chrom = chr
				if (chrom == "23"):
					chrom = "X"
				if (chrom == "24"):
					chrom = "Y"
				if (chrom not in chromosomes):
					continue
				for bin in range(0, len(list_chr[chr])):
					bin_count = list_chr[chr][bin]
					while len(chromosomes[chrom]) < bin:
						chromosomes[chrom].append(0.)
					chromosomes[chrom].append(float(bin_count))

						
list_bincount()

# print("------")
# print("chromosomes")
# print(chromosomes['1'])
# print(type(chromosomes))
# with open('log_chr.txt', 'w') as convert_file: 
#      convert_file.write(json.dumps(chromosomes))

# Dump converted data to a file
if args.outfile:
	print("out file: ", args.outfile)
	pickle.dump(chromosomes,open(args.outfile,'wb'))

