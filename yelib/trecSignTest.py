#!/usr/bin/env python

import subprocess
import os
import sys
import signtest
from sh import Command 
from optparse import OptionParser
from optparse import OptionGroup
import numpy as np

base="/home/benhe/jeff/lucene2.4.1/lib"
tbase="/home/benhe/jeff/temp/"
rel_file = "/home/zheng/workspace/terrier-3.5/867/08.qrels.opinion.all-topics.id"
rel_file = "/home/zheng/workspace/java/lucene2.4/TopicQrel/qrels.51-100.disk1.disk2.AP.id"
rel_map = {
	'blog08': "/home/zheng/workspace/terrier-3.5/867/08.qrels.opinion.all-topics.id", 
	'ap8889': "/home/zheng/workspace/java/lucene2.4/TopicQrel/qrels.51-100.disk1.disk2.AP.id", 
	'trec8' : "/home/zheng/workspace/java/lucene2.4/TopicQrel/qrels.trec8.adhoc.parts1-5.id",
	'wt2g': "/home/zheng/workspace/java/lucene2.4/TopicQrel/qrel.trec8.small_web.qrels.id",
	"wt10g": "/home/zheng/workspace/java/lucene2.4/TopicQrel/wt10g.qrels.id",
}
des="""
default (no para) is to scp the jar lib from Haze.
"""

#This function takes Bash commands and returns them
def bash(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read().strip()
    return out  #This is the stdout from the shell command

##############################
def getAPs(file, base='.'):
    #file = base+ "/" + file
    cmdtext= "sed -n '38,$p' " + file + " |awk '{ printf $2 \" \\n\"}'"
    out = bash(cmdtext)
    x = [float(value) for value in out.split()]
    return x
#############################

trec_eval = Command("trec_eval")
truc_tag = True

def truncate_start_save(file, c='0'):
	with open(file) as f:
		content = f.readlines()
		tag = False
		for line in content:
			if line.startswith('0'):
				tag = True
				break
		if not tag:
			return 
	with open(file, 'w') as f:
		f.write('\n'.join([line.lstrip('0') for line in content])) 


def getAPs1(rel_file, efile, base='.', measure="map"):
	"""
	input the raw res file, and use trec_eval 
	todo: make it more efficient
	"""
	#file = base+ "/" + file
	if truc_tag:
		truncate_start_save(efile)
	result = trec_eval(["-q", rel_file, efile])
	eval_out = filter( lambda a: a.startswith(measure) and not a[len(measure)].isdigit(), result.stdout.splitlines() )
	#print result.ran
	#print result.stdout, eval_out
	scores = [float(a.split()[2]) for a in eval_out]
	return (scores[:len(eval_out)], scores[len(scores)-1] )
	#return (scores[:len(eval_out)-1], np.sum( scores[:len(eval_out)-1] )/49. )


def main():
	parser = OptionParser(usage="usage: %prog [options] filename1 filename2", version="%prog 1.0", epilog="post") 
	parser.add_option("-m", action="store", dest="measure", default="all", help='specify the eval measure to test, default is all: map, P_5, P_20')
	parser.add_option("-r", action="store", dest="r", default="ap8889", help='specify the collection name')
	parser.add_option("-t", action="store_true", dest="t", default=False, help='truncate 0 at the beginning of the topic id')


	'''
	parser.add_option("-t", "--trans",
			  action="store_true", dest="trans", default=False,
			  help="transfer a local file to the Haze server")
	parser.add_option("-g", "--gets",
			  action="store_true", dest="gets", default=False,
			  help="get a file from the Haze Server") 
	'''
	parser.set_description(des)
	(options, args) = parser.parse_args()
	alen = len(args)
	print "options:", options
	print "args:", args
	##########################################################
	rel_file = rel_map[options.r]
	truc_tag = options.t
	if alen == 2:
		if options.measure == 'all':
			for c_measure in ['map', 'P_5', 'P_20']:
				print 'handle', c_measure
				x, perfx = getAPs1(rel_file, args[0], measure=c_measure)
				y, perfy = getAPs1(rel_file, args[1], measure=c_measure)
				signtest.signtest_pvalue(x, y, sided = 0, verbose =1, html=False)
				print 'improvement: ',len(x), perfx, perfy, (perfy - perfx)/perfx 
		else:
				print 'handle', options.measure
				x, perfx = getAPs1(rel_file, args[0], measure=options.measure)
				y, perfy = getAPs1(rel_file, args[1], measure=options.measure)
				print len(x), len(y)
				signtest.signtest_pvalue(x, y, sided = 0, verbose =1, html=False)
				
				print 'improvement: ',len(x), perfx, perfy, (perfy - perfx)/perfx 			
	elif alen ==1:
		print getAPs(args[0])
	else:
		parser.print_help()
		exit

if __name__ == '__main__':
    main()
