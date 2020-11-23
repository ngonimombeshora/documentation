# RealEstateCore Documentation Build Instructions

## Table of Contents

* [Overview](#overview)
    * [Prerequisites](#prerequisites)
    * [Install OWL2VOWL](#install-owl2vowl)
    * [Install PyLODE](#install-pylode)
* [Building Module Documentations](#building-module-documentations)
    * [Preparations](#preparations)
    * [Building PyLODE module documentation](#building-pylode-module-documentation)
    * [Generating VOWL module visualizations](#generating-vowl-module-visualizations)
    * [Grafting VOWL visualizations onto the PyLODE documentation](#grafting-vowl-visualizations-onto-the-pylode-documentation)
* [Building REC Full Documentation](#building-rec-full-documentation)
    * [Generating a merged REC Full RDF file](#generating-a-merged-rec-full-rdf-file)
    * [Generating REC Full HTML and VOWL](#generating-rec-full-html-and-vowl)
* [Adding Index files](#adding-index-files)

## Overview

The RealEstateCore documentation uses the PyLODE ontology documentation 
generator, which generates HTML output based on the content of the ontology. 
We augment this generated documentation using the WebVOWL ontology visualizer, 
which provides the nice graphs displayed early in each documentation page. 
The WebVOWL visualization is added into the HTML document as an embedded 
iframe, and this is done manually for each ontology module. The WebVOWL HTML, 
CSS, and JavaScript are however shared across all modules for a given release 
of the ontology.

WebVOWL uses a custom JSON format to represent the ontology visualization. 
The initial JSON file for each ontology module is generated using the OWL2VOWL 
program linked below. This file can then be uploaded into a WebVOWL instance 
(either your own, or the public one provided by its developers, hosted at 
http://visualdataweb.de/webvowl), where it can be manipulated as needed (i.e., 
the options for which constructs are displayed and how can be changed), and 
then downloaded again.

### Prerequisites

* [PyLODE](https://github.com/RDFLib/pyLODE)
* [OWL2VOWL](https://github.com/VisualDataWeb/OWL2VOWL)
* [Apache Maven](https://maven.apache.org/download.cgi) (needed if building 
OWL2VOWL)
* [WebVOWL](https://github.com/VisualDataWeb/WebVOWL) (optional, required if 
you wish to build WebVOWL from scratch, see below)

### Install OWL2VOWL

If you have a known-good binary version of `owl2vowl.jar`, place it in a 
directory of your choosing.

Otherwise, ensure that you have a working Maven installation: 

`mvn --version`

Download a release of OWL2VOWL, step into it, and build:

`git clone https://github.com/VisualDataWeb/OWL2VOWL`

`cd OWL2VOWL`

`mvn package -Denv=standalone -DskipTests`

Note that tests are skipped because the OWL2VOWL repository seems to contain 
broken tests -- not my fault. The resulting binary will be found in 
`target/OWL2VOWL-0.3.7-shaded.jar`. Copy into a path of your choosing as 
owl2vowl.jar and proceed with this guide.

### Install PyLODE

Download a PyLODE archive to an appropriate path and step into it:

`cd Downloads/pyLODE-1.7/`

Install the prerequisite Python packages:

`sudo pip3 install -r requirements.txt`

Step into the binary directory:

`cd src/pylode/bin/`

## Building Module Documentations

### Preparations 

1. Create a new subdirectory beneath this one, named per the REC version that 
you are documenting, e.g., "3.1.2", or "4.0". 
2. Either copy the 'webvowl' directory from an earlier version, or build 
WebVOWL from scratch into a new 'webvowl' subdirectory of your version 
directory (building WebVOWL is non-trivial and out-of-scope for this 
documentation). E.g., `3.1.2/webvowl/`. 
3. Remove any pre-existing files from the `webvowl/data` subdirectory.
4. Copy the RDF files for the ontology version that you are documenting into 
your version directory, e.g., `3.1.2/full.rdf`, `3.1.2/core.rdf`, etc.

### Building PyLODE module documentation

For each module, execute PyLODE to generate the HTML documentation:

`./pylode -i /TARGET_DIRECTORY/MODULE_NAME.rdf -o MODULE_NAME.html`

Replace "TARGET_DIRECTORY" by the path to your new version subdirectory, 
created earlier, and "MODULE_NAME" by the name of the ontology module (e.g., 
"core" or "metadata").

### Generating VOWL module visualizations

For each module, execute OWL2VOWL to generate the JSON-format visualizations.

Note that the OWl2VOWL generator will resolve imported ontologies automatically 
from the internet. Since we in fact do _not_ want each generated visualization 
to include the entirety of the REC ontology, you, prior to running the below,
need to make sure that these imports do not resolve. This can achieved in one 
of two ways:

1. You are documenting a new and never before published version, ontology, 
i.e., the target version directory with the RDF files in it has not yet 
been pushed to GitHub.
2. You unplug your Ethernet cable.

Then run, for each module:

`java -jar owl2vowl.jar -file /TARGET_DIRECTORY/MODULE_NAME.rdf  -output  TARGET_DIRECTORY/webvowl/data/MODULE_NAME.json`

You can however skip the metadata module, which only contains annotation 
properties, and thus does not provide a graphical rendering.

At this point, reconnect to the Internet, launch a WebVOWL instance (local 
or [hosted](http://visualdataweb.de/webvowl/)) and upload your JSON files to 
take a first look. If needed for clarity, modify the visualization and filters 
as needed, and export the JSON from WebVOWL and back to the same path on disk 
as you started with. 

### Grafting VOWL visualizations onto the PyLODE documentation

For each module (except the metadata module which has no graphical 
representation), replace the following documentation:

`<div style="width:500px; height:500px; background-color: black;">&nbsp;</div>`

by the following:

`<iframe src="webvowl/index.html#MODULE_NAME" width="100%" height="800"></iframe>`

Replace MODULE_NAME by the name of the module.

## Building REC Full Documentation

Documentation for the REC full ontology (including all the modules) is crafted 
in much the same way as described above, but with two very crucial differences:

1. The pyLODE documentation generator, which does not resolve imports, needs 
to operate on an RDF file that contains the entirety of the REC ontology suite.
Such an RDF file can be generated using Protégé, as described below.
2. Unlike for the modules, for the Full ontology we actually want the OWL2VOWL 
visualization generator to resolve all the imports; so we need to ensure that 
the RDF files are accessible on the web before running it. The easiest way 
to achieve this is to simply push the documentaion repo (including the RDF 
files there were copied into it in the [preparations](#preparations) step, and 
which you have been working with) up to GitHub prior to proceeding.

### Generating a merged REC Full RDF file

In the Protégé tool, load the REC Full ontology, making sure that all the 
imports resolve and are loaded. Then use the menu option `Refactor/Merge ontologies..`.
On the first screen of the wizard, select to merge all of the loaded 
ontologies _except_ Full. In the second step of the wizard select to merge 
into an _existing_ ontology. In the third step, select Full as the target 
ontology for the merge. Now use the menu option `File/Save as..` to save 
the merged file into a suitable temporary path on disk, NOT inside the target
documentation directory (e.g., your desktop folder). Use the RDF/XML 
serialization format. 

### Generating REC Full HTML and VOWL

You can now use the temporary merged Full file to generate pyLODE documentation 
as follows: 

`./pylode -i /TEMPORARY_PATH/full.rdf -o full.html`

Copy the full.html file into the documentation target directory alongside 
the other HTML documentation; then generate VOWL visualization using OWL2VOWL 
as you did for the modules:

`java -jar owl2vowl.jar -file /TARGET_DIRECTORY/full.rdf  -output  TARGET_DIRECTORY/webvowl/data/full.json`

Finally, graft on the VOWL visualization for the Full ontology documentation, 
just as [described above](#grafting-vowl-visualizations-onto-the-pylode-documentation).

## Adding Index files

For final touches, create a README.md file in your target directory, which 
provides navigation links to the ontology modules and Full ontology. For 
convencience, start by copying this file from an earlier version.

Don't forget to update the parent-level README.md-file, so that users 
navigating directly via https://doc.realestatecore.io can traverse the entire 
documentation structure.