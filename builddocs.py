#!/usr/bin/env python3

import sys
import subprocess
import os
from os import listdir, remove, rename
from os.path import isfile, join, splitext, isdir
from shutil import copytree
from rdflib import Graph
from rdflib.namespace import OWL, RDF

# GitHub Pages blows up if PyLODE is included in the repo, strangely
pylodePath = "Applications/pyLODE-2.8.3/pylode/cli.py"
owl2vowlPath = "bin/owl2vowl.jar"
robotPath = "Applications/robot/robot.sh"

# removed ttl to be converted first with robot
ontologyFileEndings = ["owl", "rdf", "nq"]
FileEndingsToConvert = ["ttl"]

if (len(sys.argv) != 2):
    print("Usage: './build.py OntologyDirectory', e.g., './build.py 3.1.3'")
    sys.exit()

ontologyPath = sys.argv[1]


allFiles = [f for f in listdir(ontologyPath) if isfile(
    join(ontologyPath, f))]  # all files in folder for converting

# use robot to convert turtle file before compiling "ontologoyFiles" below
for inputFile in allFiles:
    print(inputFile)
    if inputFile.endswith("ttl"):
        moduleName, fEnding = splitext(inputFile)
        outputOWLFileName = f"{ontologyPath}/{moduleName}.owl"

        print("converting turtle files...")
        os.system("./" + robotPath + " convert --input " +
                  ontologyPath + "/" + inputFile + " --format owl --output " + outputOWLFileName + " -vv")
        print("...done")

# get all files again--to include the newly converted tutle files
allFiles = [f for f in listdir(ontologyPath) if isfile(
    join(ontologyPath, f))]  # all files in folder for converting to vowl

ontologyFiles = [f for f in allFiles if splitext(
    f)[1].strip('.') in ontologyFileEndings]

# Copy webvowl skeleton   N.B data file for storing json-vowl is not copied...
if not isdir(f"{ontologyPath}/webvowl"):
    copytree("webvowl", f"{ontologyPath}/webvowl")

for inputFile in ontologyFiles:
    inputFilePath = f"{ontologyPath}/{inputFile}"
    # 1. Generate PyLODE docs
    moduleName, fEnding = splitext(inputFile)
    outputHtmlFileName = f"{ontologyPath}/{moduleName}.html"
    subprocess.run([pylodePath, "-i", inputFilePath,
                    "-o", outputHtmlFileName])

    # 2. Merge into temp full graph (
    moduleGraph = Graph()
    moduleGraph.parse(inputFilePath)
    moduleOntologyUris = list(moduleGraph.subjects(RDF.type, OWL.Ontology))

    # This is to prevent the visualization from including the imports closure
    tempOntologyFilePath = inputFilePath + "-TEMP"
    moduleGraph.remove((None, OWL.imports, None))
    moduleGraph.serialize(
        destination=tempOntologyFilePath, format="application/rdf+xml")
    outputJsonFilePath = f"{ontologyPath}/webvowl/data/{moduleName}.json"

    subprocess.run(["java", "-jar", owl2vowlPath, "-file",
                    tempOntologyFilePath, "-output", outputJsonFilePath])
    remove(tempOntologyFilePath)

    # Graft on HTML <iframe>s
    htmlFile = open(outputHtmlFileName, "rt")
    htmlContent = htmlFile.read()
    htmlFile.close()
    htmlContent = htmlContent.replace('<div style="width:500px; height:50px; background-color: lightgrey; border:solid 2px grey; padding:10px;margin-bottom:5px; text-align:center;">Pictures say 1,000 words</div>',
                                      f'<iframe src="webvowl/index.html#{moduleName}" width="100%" height="800"></iframe>')
    htmlFile = open(outputHtmlFileName, "wt")
    htmlFile.write(htmlContent)
    htmlFile.close()
