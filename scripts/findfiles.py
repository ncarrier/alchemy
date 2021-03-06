#!/usr/bin/env python

import sys, os
import optparse

#===============================================================================
# Process a directory.
#===============================================================================
def processDir(resultList, topDir, fileName, options):
	sys.stderr.write("Scanning %s for makefiles...\n" % topDir)
	for dirPath, dirNames, fileNames in os.walk(topDir, followlinks=options.followLinks):
		# Remove directories to skip from list
		i = 0
		while i < len(dirNames):
			if dirNames[i] in options.pruneList \
				or os.path.join(dirPath, dirNames[i]) in options.pruneList:
				del dirNames[i]
			else:
				i += 1

		# Once a match have been found in a directory, don't go deeper unless
		# told otherwise
		if fileName in fileNames:
			resultList.append(os.path.join(dirPath, fileName))
			if not options.deep:
				del dirNames[:]

#===============================================================================
# Main function.
#===============================================================================
def main():
	(options, args) = parseArgs()

	# Extract arguments
	topDir = os.path.realpath(args[0])
	fileName = args[1]

	# Get real paths (because we will compare them)
	# Simple names are kept as is for prune dirs
	newpruneList = []
	for pruneDir in options.pruneList:
		if "/" in pruneDir:
			newpruneList.append(os.path.realpath(pruneDir))
		else:
			newpruneList.append(pruneDir)
	options.pruneList = newpruneList

	# Real paths of add dirs
	options.addList = [os.path.realpath(addDir) \
			for addDir in options.addList]

	# Go
	resultList = []
	# Check that the directory is not in the prune list
	if topDir not in options.pruneList:
		processDir(resultList, topDir, fileName, options)
	for topDir in options.addList:
		processDir(resultList, topDir, fileName, options)

	# Write results to stdout
	resultList.sort()
	printList = []
	for result in resultList:
		if result in printList:
			sys.stderr.write("warning: %s already found\n" %  result)
		else:
			sys.stdout.write(result + "\n")
			printList.append(result)

#===============================================================================
# Setup option parser and parse command line.
#===============================================================================
def parseArgs():
	# Setup parser
	usage = "usage: %prog [options] <topdir> <filename>"
	parser = optparse.OptionParser(usage=usage)

	# Main options
	parser.add_option("--prune",
		dest="pruneList",
		action="append",
		default=[],
		metavar="DIR",
		help="Skip this directory during search. May be used multiple times.")
	parser.add_option("--add",
		dest="addList",
		action="append",
		default=[],
		metavar="DIR",
		help="Add this directory during search. May be used multiple times.")
	parser.add_option("--deep",
		dest="deep",
		action="store_true",
		default=False,
		help="Do not stop scanning a directory if a match has been found.")
	parser.add_option("--follow-links",
		dest="followLinks",
		action="store_true",
		default=False,
		help="Follow symbolic links.")

	# Parse arguments and check validity
	(options, args) = parser.parse_args()
	if len(args) < 1:
		parser.error("Missing topdir argument")
	elif len(args) < 2:
		parser.error("Missing filename argument")
	return (options, args)

#===============================================================================
# Entry point.
#===============================================================================
if __name__ == "__main__":
	main()
