from flask_api import FlaskAPI
import redis
from flask.json import JSONEncoder
from flask import request,jsonify,session,render_template
from selenium import webdriver
import time
import paramiko 
from flask_cors import CORS
from json import dumps as jsonstring
from src.DataCurator import *
import os
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore

############################################
# Create a folder that contains the output #
############################################
app = FlaskAPI(__name__)
store = RedisStore(redis.StrictRedis())
KVSessionExtension(store, app)

dirname = "jacs.6b00225"
detailsCounter = []
if not os.path.exists(dirname):
   os.makedirs(dirname)

#################
# Define People #
#################
@app.route('/',methods = ['GET'])
def newUser():
	pid = 0
	print("here")
	return jsonify({'pid':pid})

@app.route('/getPersonalDetails',methods=['POST'])
def getPersonalDetails():
	pDetails = request.json
	person = Person()
	fname = ""
	middleName = ""
	lastName = ""
	print(store)
	if("GET" in pDetails[0]):
		print(pDetails)
		if 'pfirstName' in store and store.get('pfirstName') is not None:
			print("here")
			fname = str(store.get('pfirstName'))[2:len(str(store.get('pfirstName')))-1]
		if 'pmiddleName' in store and store.get('pmiddleName') is not None:
			middleName = str(store.get('pmiddleName'))[2:len(str(store.get('pmiddleName')))-1]
		if 'plastName' in store and store.get('plastName') is not None:
			print("here1")
			lastName = str(store.get('plastName'))[2:len(str(store.get('plastName')))-1]
	else:
		fname = str(pDetails[1])
		if("N/A" not in str(pDetails[2])):
			middleName = str(pDetails[2])
		lastName = str(pDetails[3])
	if(fname is not None):
		person.addFirstName(str(fname))
		#session['pfirstName'] = fname
		store.put('pfirstName', fname)
	if(middleName is not None):
		person.addMiddleName(str(middleName))
		#session['pmiddleName'] = middleName
		store.put('pmiddleName',middleName)
	if(lastName is not None):
		person.addLastName(str(lastName))
		#session['plastName'] = lastName
		store.put('plastName',lastName)
	print(store)
	return jsonify({'pdetails':person.__dict__})	
	
@app.route('/getServerDetails',methods=['POST'])
def getServerDetails():
	serverDetails = request.json
	server = Server()
	ServerName = ""
	UserName = ""
	Password = ""
	Path = ""
	if("GET" in serverDetails[0]):
		print(serverDetails)
		if 'ServerName' in store and store.get('ServerName') is not None:
			ServerName = str(store.get('ServerName'))[2:len(str(store.get('ServerName')))-1]
		if 'UserName' in store and store.get('UserName') is not None:
			UserName = str(store.get('UserName'))[2:len(str(store.get('UserName')))-1]
		if 'Password' in store and store.get('Password') is not None:
			print("here1")
			Password = str(store.get('Password'))[2:len(str(store.get('Password')))-1]
		if 'Path' in store and store.get('Path') is not None:
			print("here1")
			Path = str(store.get('Path'))[2:len(str(store.get('Path')))-1]
	else:
		ServerName = str(serverDetails[1])
		UserName = str(serverDetails[2])
		Password = str(serverDetails[3])
		Path = str(serverDetails[4])
	if(ServerName is not None):
		server.addServerName(str(ServerName))
		store.put('ServerName', ServerName)
	if(UserName is not None):
		server.addUsername(str(UserName))
		store.put('UserName',UserName)
	if(Password is not None):
		server.addPassword(str(Password))
		store.put('Password',Password)
	if(Path is not None):
		server.addPath(str(Path))
		store.put('Path',Path)
	print(store)
	return jsonify({'serverDetails':server.__dict__})	

#server Data	

class DirectoryTree:
	title = ""
	parent = ""
	key = ""
	id = ""
	lazy = ""
	folder= ""
	source=""
@app.route('/getFancyInfo',methods=['POST'])
def getFancyInfo():
	if(request is not None):
		pathDetails = request.json
	print("here")
	ssh = paramiko.SSHClient()
	# automatically add keys without requiring human intervention
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	content_hostName = str(store.get('ServerName'))[2:len(str(store.get('ServerName')))-1]
	content_path = ''
	if(pathDetails is not None):
		if(len(pathDetails) > 0):
			content_path = str(pathDetails[0])
		else:
			content_path= str(store.get('Path'))[2:len(str(store.get('Path')))-1]
	print(content_path)
	content_username = str(store.get('UserName'))[2:len(str(store.get('UserName')))-1]
	content_password = str(store.get('Password'))[2:len(str(store.get('Password')))-1]
	print(content_hostName)
	print(content_path)
	print(content_username)
	print(content_password)
	if(content_hostName.strip() == ""):
		hostName = 'midway001.rcc.uchicago.edu'
	else:
		hostName = content_hostName
	ssh.connect(hostName, username=content_username, password=content_password)
	ftp = ssh.open_sftp()
	#path = ' /cds/gagalli/DATA_COLLECTIONS/public/' + content_project
	if(content_path.strip() == ""):
		path = '/cds/rcc-staff/depablo/DATA_COLLECTIONS/glasses_collection/' + content_project
	else:
		path = content_path
	listObjects = []
	for f in ftp.listdir_attr(path):
		dataFile = DirectoryTree()
		lstatout=str(f).split()[0]
		file = str(f).split()[8]
		dataFile.title = file
		parent = path.split("/")
		parentName = parent[len(parent)-1]
		#if(content_mode == "child"):
			#dataFile.parent = path
		dataFile.key = path + "/" + file
		dataFile.id = path + "/" + file
		if 'd' in lstatout:
			prev = file
			dataFile.folder = "true"
			dataFile.lazy = 'true'
		print(dataFile.parent)
		print(dataFile.title)
		print(dataFile.key)
		listObjects.append(dataFile.__dict__)
	return jsonify({'listObjects':listObjects})	





gaiduk = Person()
gaiduk.addFirstName("Alex")
gaiduk.addLastName("Gaiduk")

govoni = Person()
govoni.addFirstName("Marco")
govoni.addLastName("Govoni")

galli = Person()
galli.addFirstName("Giulia")
galli.addLastName("Galli")

skone = Person()
skone.addFirstName("Jonathan")
skone.addMiddleName("H.")
skone.addLastName("Skone")

winter = Person()
winter.addFirstName("Bernd")
winter.addLastName("Winter")

seidel = Person()
seidel.addFirstName("Robert")
seidel.addLastName("Siedel")

##################
# Define Project #
##################

project = Project("jacs.6b00225",skone,True,"http://midway001.rcc.uchicago.edu:8888/dataportal/","https://www.globus.org/app/transfer?origin_id=72277ed4-1ad3-11e7-bbe1-22000b9a448b&origin_path=%2Fjacs.6b00225%2F") # name of folder, who creates the project, isPublic, serverPath 
project.addPI(galli)
project.addCollection("MICCoM")
project.addTag("DFT")
project.addTag("MBPT")
project.addTag("PES")
project.addTag("photo electron spectra")
project.addTag("band edges")
project.addTag("density of states")
project.addTag("water")
project.addTag("AIMD")

################
# Define Tools #
################

bessy = Tool("experiment")
bessy.addMeasurement("soft X-ray Photoemission")
bessy.addFacilityName("Helmholtz-Zentrum Berlin")
bessy.addURL("https://www.helmholtz-berlin.de/pubbin/igama_output?modus=einzel&sprache=en&gid=1648&typoid")
project.addNode(bessy)

espresso = Tool("software")
espresso.addProgramName("pw.x")
espresso.addVersion("5.2")
espresso.addPackageName("Quantum-Espresso")
espresso.addURL("http://www.quantum-espresso.org/")
project.addNode(espresso)

west = Tool("software") # can be software or experiment 
west.addProgramName("wstat.x")
west.addVersion("2.0.0")
west.addPackageName("West")
west.addURL("http://www.west-code.org")
project.addNode(west)

#qbox = Tool("software")
#qbox.addProgramName("qbox")
#qbox.addVersion("1.0.0")
#qbox.addPackageName("Qbox")
#qbox.addURL("http://qboxcode.org")
#project.addNode(qbox)

####################
# Define Reference #
####################

ref = Reference("article") # can be article (in future book, to be parsed from RIS or BibteX)
ref.addAuthor(gaiduk) 
ref.addAuthor(govoni) 
ref.addAuthor(seidel) 
ref.addAuthor(skone) 
ref.addAuthor(winter) 
ref.addAuthor(galli) 
ref.addTitle("Photoelectron spectra of aqueous solutions from first principle")
ref.addDOI("10.1021/jacs.6b00225") 
ref.addJournal("Journal of the American Chemical Society","JACS Comm.") 
ref.addVolume("138") 
ref.addPage("6912") 
ref.addYear(2016) 
ref.addPublishedAbstract("We present a combined computational and experimental study of the photoelectron spectrum of a simple aqueous solution of NaCl. Measurements were conducted on microjets, and first-principles calculations were performed using hybrid functionals and many-body perturbation theory at the G0W0 level, starting with wave functions computed in ab initio molecular dynamics simulations. We show excellent agreement between theory and experiments for the positions of both the solute and solvent excitation energies on an absolute energy scale and for peak intensities. The best comparison was obtained using wave functions obtained with dielectric-dependent self-consistent and range-separated hybrid functionals. Our computational protocol opens the way to accurate, predictive calculations of the electronic properties of electrolytes, of interest to a variety of energy problems.") 
ref.addReceivedDate("2016-01-08")
ref.addPublishedDate("2016-04-22")
project.addReference(ref)

###################
# Curate Datasets #
###################

dat1 = Dataset()
dat1.addReadme("Processed experimental spectrum from Winters and Siedel and orbital image files -- processing of experimental data unknown")
dat1.addFile("charts/figure1")
project.addNode(dat1)

dat2 = Dataset()
dat2.addReadme("Example input files for dft pw.x calculations, MLWF calculations and WEST G0W0 calculations.")
dat2.addFile("data/input")
project.addNode(dat2)

dat3 = Dataset()
dat3.addReadme("electronic structure outputs at various levels of theory (pbe, pbe0, rsh, sc-hybrid, G0W0@pbe, G0W0@pbe0, G0W0@rsh, G0W0@sc-hybrid) along with MLWF outputs at the same levels of theory. Each subfolder geometry in the s10 subfolder contains a geometry obtained as a snapshot sxxxx from a PBE0 MD trajectory of 1M salt water.")
dat3.addFile("data/s10")
project.addNode(dat3)

dat4 = Dataset()
dat4.addReadme("electronic structure outputs at various levels of theory (pbe, pbe0, rsh, sc-hybrid, G0W0@pbe, G0W0@pbe0, G0W0@rsh, G0W0@sc-hybrid) along with MLWF outputs at the same levels of theory. Each subfolder geometry in the s15 subfolder contains a geometry obtained as a snapshot sxxxx from a PBE0 MD trajectory of 1M salt water.")
dat4.addFile("data/s15")
project.addNode(dat4)

##################
# Curate Scripts #
##################

script1 = Script()
script1.addReadme("gnuplot script to generate experimental PES plot of water overlayed with the orbitals for each DOS peak")
script1.addFile("charts/figure1/pes.plt")
project.addNode(script1)

script2 = Script()
script2.addReadme("extract atomic coordinates from Qbox output files")
script2.addFile("scripts/coords.sh")
project.addNode(script2)

script3 = Script()
script3.addReadme("make sample")
script3.addFile("scripts/mksam.sh")
project.addNode(script3)

script4 = Script()
script4.addReadme("evaluate projected-density of states from wannier localized orbitals")
script4.addFile("scripts/pdos.sh")
project.addNode(script4)

script5 = Script()
script5.addReadme("compute average of some quantity")
script5.addFile("scripts/average.sh")
project.addNode(script5)

script6 = Script()
script6.addReadme("projected density of states for GW calculations")
script6.addFile("scripts/pdos-GW.sh")
project.addNode(script6)

script7 = Script()
script7.addReadme("evaluate the projected density of states intensities")
script7.addFile("scripts/pdos+intensities.sh")
project.addNode(script7)

script8 = Script()
script8.addReadme("determine maximum peak location")
script8.addFile("scripts/detmax.sh")
project.addNode(script8)

script9 = Script()
script9.addReadme("gnuplot script to plot the experimental PES of salt water overlayed with theoretical DOS evaluated at several DFT levels of theory")
script9.addFile("charts/figure2/dft.plt")
project.addNode(script9)

script10 = Script()
script10.addReadme("gnuplot script to plot the experimental PES of salt water overlayed with theoretical DOS evaluated at GW@dft level of theory where dft is several dft levels of theory")
script10.addFile("charts/figure3/gw.plt")
project.addNode(script10)

script11 = Script()
script11.addReadme("gnuplot script to plot the experimental PES of salt water overlayed with theoretical DOS evaluated at GW@sc-hybrid level of theory")
script11.addFile("charts/figure4/sc_intensity_Banna_115eV.plt")
project.addNode(script11)

#################
# Curate Charts #
#################

chart1 = Chart("figure") # figure or table 
chart1.addNumber("1")
chart1.addCaption(" Experimental PE spectrum of a 1 M solution of NaCl and molecular orbitals of a single water molecule corresponding to specific bands in the spectrum. The background due to secondary electrons has been subtracted following ref 11. The sharp peak at 12.6 eV arises from ionization of the 1b1 orbital of gas-phase water.")
chart1.addProperty("electron binding energy")
chart1.addProperty("photo-electron spectrum")
chart1.addImageFile("charts/figure1/fig1.png")
chart1.addFile("charts/figure1/winter_exp.txt")
chart1.addNotebookFile("charts/figure1/plot.ipynb")
project.addNode(chart1)

chart2 = Chart("figure") # figure or table 
chart2.addNumber("2")
chart2.addCaption("PE spectra of a 1 M aqueous NaCl solution computed with density functional approximations compared to the experimental spectrum of Figure 1. The gray area under the spectral features of sodium (2p) and chloride (3p) is the DOS projected on the maximally localized Wannier functions centered on the ionic sites. Theoretical spectra were aligned to the vacuum level (see text and Table SI).")
chart2.addProperty("density of states")
chart2.addProperty("photo-electron spectrum")
chart2.addImageFile("charts/figure2/fig2.png")
chart2.addFile("charts/figure2/winter_exp.txt")
chart2.addFile("charts/figure2/pdos_pbe.txt")
chart2.addFile("charts/figure2/pdos_pbe0.txt")
chart2.addFile("charts/figure2/pdos_rsh.txt")
chart2.addFile("charts/figure2/pdos_sc.txt")
chart2.addNotebookFile("charts/figure2/plot.ipynb")
project.addNode(chart2)

chart3 = Chart("figure") # figure or table 
chart3.addNumber("3")
chart3.addCaption("PE spectra of a 1 M aqueous NaCl solution computed using the G0W0 approximation starting from different sets of eigenfunctions and eigenvalues. Each theoretical spectrum is from a single snapshot representative of the entire trajectory. The spectra were aligned to the vacuum level (see text and SI). The gray area is projected DOS on Na and Cl atoms defined in Figure 2 caption.")
chart3.addProperty("density of states")
chart3.addProperty("photo-electron spectrum")
chart3.addImageFile("charts/figure3/fig3.png")
chart3.addFile("charts/figure3/winter_exp.txt")
chart3.addFile("charts/figure3/pdos_pbe_GW.txt")
chart3.addFile("charts/figure3/pdos_pbe0_GW.txt")
chart3.addFile("charts/figure3/pdos_rsh_GW.txt")
chart3.addFile("charts/figure3/pdos_sc_GW.txt")
chart3.addNotebookFile("charts/figure3/plot.ipynb")
project.addNode(chart3)

chart4 = Chart("figure") # figure or table 
chart4.addNumber("4")
chart4.addCaption("Experimental (black) and theoretical (blue) PE spectra of a 1 M aqueous solution of NaCl. Theoretical spectrum was computed using G0W0/sc-hybrid line widths and experimental photoionization cross sections as explained in the SI. Both spectra were normalized to the 1b1 peak of water. The gray area is projected DOS on Na and Cl atoms (see Figure 2 caption).")
chart4.addProperty("density of states")
chart4.addProperty("photo-electron spectrum")
chart4.addImageFile("charts/figure4/fig4.png")
chart4.addFile("charts/figure4/winter_exp.txt")
chart4.addFile("charts/figure4/pdos_GW_Banna_115eV+Yeh_ions_200eV.txt")
chart4.addFile("charts/figure4/pdos_pbe0_GW.txt")
chart4.addFile("charts/figure4/pdos_rsh_GW.txt")
chart4.addFile("charts/figure4/pdos_sc_GW.txt")
chart4.addNotebookFile("charts/figure4/plot.ipynb")
project.addNode(chart4)

chart5 = Chart("table") # figure or table 
chart5.addNumber("1")
chart5.addCaption("Electron BE in PE Spectra of a 1 M NaCl Solution Computed Using DFT and Many-Body Perturbation Theory at the G0W0 Level")
chart5.addProperty("electron binding energy")
chart5.addProperty("photo-electron spectrum")
chart5.addImageFile("charts/table1/table1.png")
chart5.addFile("charts/table1/dos.ods")
chart5.addNotebookFile("charts/table1/plot.ipynb")
project.addNode(chart5)

############
# workflow #
############

head1 = Head()
head1.addReadme("Experimental setup info")
head1.addURL("")
project.addNode(head1)

head2 = Head()
head2.addReadme("NACL2016 dataset: NVT s10 simulation data")
head2.addURL("http://www.quantum-simulation.org/reference/nacl/index.htm")
project.addNode(head2)

head3 = Head()
head3.addReadme("NACL2016 dataset: NVT s15 simulation data")
head3.addURL("http://www.quantum-simulation.org/reference/nacl/index.htm")
project.addNode(head3)

# Connect figure1
project.connectNodes([head1,bessy,dat1,script1,chart1])

# Connect figure2
project.connectNodes([head1,bessy,dat1,script9,chart2])
project.connectNodes([head2,script2,script3,dat2,espresso,dat3,script4,script5,script9,chart2])
project.connectNodes([head3,script2,script3,dat2,espresso,dat4,script4,script5,script9,chart2])

# Connect figure3
project.connectNodes([head1,bessy,dat1,script10,chart3])
# note s10 only contains GW@PBE for all snapshots, no GW@hybrid
project.connectNodes([head2,script2,script3,dat2,espresso,dat3,west,script6,script5,script10,chart3])
# note s15 only contains GW@PBE for all snapshots, and GW@hybrid for select snapshots
project.connectNodes([head3,script2,script3,dat2,espresso,dat4,west,script6,script5,script10,chart3])

# Connect figure4
project.connectNodes([head1,bessy,dat1,script11,chart4])
project.connectNodes([head2,script2,script3,dat2,espresso,dat3,west,script6,script5,script7,script11,chart4])

# Connect table1
project.connectNodes([head2,script2,script3,dat2,espresso,dat3,script4,script5,script8,chart5])
project.connectNodes([head3,script2,script3,dat2,espresso,dat4,script4,script5,script8,chart5])
project.connectNodes([head2,script2,script3,dat2,espresso,dat3,west,script6,script5,script8,chart5])
project.connectNodes([head3,script2,script3,dat2,espresso,dat4,west,script6,script5,script8,chart5])

# Plot workflow
#project.drawGraph(dirname + "/graph.pdf")
#project.drawSubGraph(dirname + "/subgraph.pdf",chart4)

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

#pid = project.sendDescriptor(dirname + '/desc.json','mongodb.rcc.uchicago.edu','imedb_client','IMEdbClientPWD') # ip, username, password
#project.fetchDescriptor(pid,'mongodb.rcc.uchicago.edu','imedb_client','IMEdbClientPWD')

if __name__=="__main__":
	app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
	CORS(app)
	app.run(debug=True)
