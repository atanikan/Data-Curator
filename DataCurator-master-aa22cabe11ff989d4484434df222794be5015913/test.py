from src.DataCurator import *
import os

############################################
# Create a folder that contains the output #
############################################

dirname = "test"
if not os.path.exists(dirname):
   os.makedirs(dirname)

#################
# Define people #
#################

giulia = Person()
giulia.addFirstName("Giulia")
giulia.addLastName("Galli")

marco = Person()
marco.addFirstName("Marco")
marco.addLastName("Govoni")

##################
# Define Project #
##################

project = Project("natcomm13.35235000",marco,True,"http://midway001.rcc.uchicago.edu:8888/dataportal/","https://www.globus.org/app/transfer?origin_id=72277ed4-1ad3-11e7-bbe1-22000b9a448b&origin_path=%2F") # name of folder, who creates the project, isPublic, serverPath, globusPath
project.addPI(giulia)
project.addTag("MBPT")
project.addTag("DFT24")
project.addTag("Benchmark")

################
# Define tools #
################

west = Tool("software") # can be software or experiment
west.addPackageName("West")
west.addProgramName("wstat.x")
west.addVersion("2.0.0")
west.addURL("http://www.west-code.org")
project.addNode(west)

qbox = Tool("software")
qbox.addPackageName("Qbox")
qbox.addProgramName("qbox")
qbox.addVersion("1.0.0")
qbox.addURL("http://qboxcode.org")
project.addNode(qbox)

xps = Tool("experiment")
xps.addFacilityName("ANL-APS")
xps.addMeasurement("XPS")
xps.addURL("https://www1.aps.anl.gov")
project.addNode(xps)

####################
# Define reference #
####################

ref = Reference("article") # can be article (in future book, to be parsed from RIS or BibteX)
ref.addDOI("10.1039/c6sm00810k")
ref.addTitle("Title of the paper goes here")
ref.addPublishedAbstract("This paper is the coolest paper about...")
ref.addAuthor(marco)
ref.addAuthor(giulia)
ref.addJournal("Journal of Chemical Theory and Computation","J. Chem. Theory Comput.")
ref.addPage("55")
ref.addVolume("11")
ref.addYear(2015)
ref.addURL("http://jctc.com")
ref.addReceivedDate("04/11/2017")
ref.addPublishedDate("04/11/2017")
project.addReference(ref)

###################
# Curate dataSets #
###################

dat1 = Dataset()
dat1.addReadme("Cool data representing... ")
dat1.addFile("data/dat1.out")
dat1.addFile("data/dat2.out")
dat1.addURL("http://data.com")
project.addNode(dat1)

##################
# curate scripts #
##################

script1 = Script()
script1.addReadme("Cool script... ")
script1.addFile("script/doit.C")
script1.addURL("http://script.com")
project.addNode(script1)

################
# curate chart #
################

chart1 = Chart("figure") # figure or table
chart1.addNumber("1")
chart1.addCaption("Cool figure... ")
chart1.addProperty("Volume")
chart1.addProperty("Pression")
chart1.addFile("chart/image1-panel-a.csv")
chart1.addFile("chart/image1-panel-b.csv")
chart1.addNotebookFile("chart/notebook1.ipynb")
chart1.addImageFile("chart/image1.jpeg")
project.addNode(chart1)

############
# workflow #
############

head1 = Head()
head1.addReadme("Configuration downloaded from the web")
head1.addURL("Configuration downloaded from the web")
project.addNode(head1)

project.connectNodes([head1,west,dat1,script1,chart1])
project.connectNodes([head1,qbox,dat1])
project.connectNodes([head1,xps])

################################
# Create a folder for the output  
################################

project.drawGraph(dirname + "/graph.pdf")
project.drawSubGraph(dirname + "/subgraph.pdf",chart1)

############################
# Generate Notebook file ! #
############################

#project.generateNotebook(dirname + "/Main.ipynb")   #### TO BE DONE
project.addNotebookFile("Main.ipynb")

########################
# Dump the JSON file ! #
########################

project.dumpJSON(dirname + "/desc.json")

######################
# MongoDB operations #
######################

#pid = project.sendDescriptor(dirname + '/desc.json','mongodb.rcc.uchicago.edu','mgovoni','mgmongo') # ip, username, password
#project.fetchDescriptor(pid,'mongodb.rcc.uchicago.edu','mgovoni','mgmongo')
