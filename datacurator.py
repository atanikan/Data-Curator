from flask_api import FlaskAPI
import redis
from flask.json import JSONEncoder
from flask import request,jsonify,session,render_template
import time
import paramiko 
from flask_cors import CORS
from json import dumps as jsonstring
from DataCuratorClass import *
import os
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from simplekv import TimeToLiveMixin
from copy import copy
import ast

############################################
# Create a folder that contains the output #
############################################
app = FlaskAPI(__name__)
store = RedisStore(redis.StrictRedis())
KVSessionExtension(store, app)

dirname = "jacs.6b00225"
infoMap = {}
chartMap = {}
toolsMap = {}
datasetsMap = {}
scriptsMap = {}
referenceMap = {}
projNameMap = {}
personMap = {}
workflowMap = {}



class WorkflowCreator(object):
	def __init__(self):
		self.desc = {}
		self.desc["charts"] = []
		self.desc["datasets"] = []
		self.desc["scripts"] = []
		self.desc["tools"] = []
	def addChart(self,chartsaveas):
		self.desc["charts"].append(chartsaveas)
			
	def addDataset(self,datasetsaveas):
		self.desc["datasets"].append(datasetsaveas)
			
	def addScript(self,scriptsaveas):
		self.desc["scripts"].append(scriptsaveas)
	
	def addTool(self,toolssaveas):
		self.desc["tools"].append(toolssaveas)
	
	
			


if not os.path.exists(dirname):
   os.makedirs(dirname)

#################
# Define People #
#################
pid = ""
	
@app.route('/DeleteAll',methods = ['POST'])
def DeleteAll():
	global pid
	for key in store.keys():
		if str(pid) in str(key):
			store.delete(key)

@app.route('/getPersonalDetails',methods=['POST'])
def getPersonalDetails():
	pDetails = request.json
	person = Person()
	fname = ""
	middleName = ""
	lastName = ""
	global pid
	print(pDetails)
	#print(store)
	#if("GET" in pDetails[0]):
	#	print(pDetails)
	#	if pfnamekey in store and store.get(pfnamekey) is not None:
	#		print("here")
	#		fname = str(store.get(pfnamekey))[2:len(str(store.get(pfnamekey)))-1]
	#	if pmnamekey in store and store.get(pmnamekey) is not None:
	#		middleName = str(store.get(pmnamekey))[2:len(str(store.get(pmnamekey)))-1]
	#	if plnamekey in store and store.get(plnamekey) is not None:
	#		print("here1")
	#		lastName = str(store.get(plnamekey))[2:len(str(store.get(plnamekey)))-1]
	#else:
	type = str(pDetails[0])
	if("N/A" not in str(pDetails[1])):
		fname = str(pDetails[1])
	if("N/A" not in str(pDetails[2])):
		middleName = str(pDetails[2])
	if("N/A" not in str(pDetails[3])):
		lastName = str(pDetails[3])
	if(fname is not None):
		person.addFirstName(str(fname))
		#session['pfirstName'] = fname
		#if pfnamekey not in store:
		#	store.put(pfnamekey, fname)
	if(middleName is not None):
		person.addMiddleName(str(middleName))
		#session['pmiddleName'] = middleName
		#if pmnamekey not in store:
		#	store.put(pmnamekey,middleName)
	if(lastName is not None):
		person.addLastName(str(lastName))
		#session['plastName'] = lastName
		#if plnamekey not in store:
		#	store.put(plnamekey,lastName)
	print(store)
	pid=fname+middleName+lastName
	pKey = 'person'+str(pid)
	personMap[pKey] = person
	return jsonify({'pdetails':person.__dict__,'pid':pid})	
	
@app.route('/getServerDetails',methods=['POST'])
def getServerDetails():
	serverDetails = request.json
	server = Server()
	ServerName = ""
	UserName = ""
	Password = ""
	Path = ""
	pid = serverDetails[0]
	serverkey = 'ServerName'+str( pid)
	userkey = 'UserName'+str( pid)
	passkey = 'Password'+str( pid)
	pathkey = 'Path'+str( pid)
	if("GET" in serverDetails[1]):
		print(serverDetails)
		if serverkey in store and store.get(serverkey) is not None:
			ServerName = str(store.get(serverkey))[2:len(str(store.get(serverkey)))-1]
		if userkey in store and store.get(userkey) is not None:
			UserName = str(store.get(userkey))[2:len(str(store.get(userkey)))-1]
		if passkey in store and store.get(passkey) is not None:
			Password = str(store.get(passkey))[2:len(str(store.get(passkey)))-1]
		if pathkey in store and store.get(pathkey) is not None:
			Path = str(store.get(pathkey))[2:len(str(store.get(pathkey)))-1]
	else:
		ServerName = str(serverDetails[2])
		UserName = str(serverDetails[3])
		Password = str(serverDetails[4])
		try:
			Path = str(serverDetails[5])
		except IndexError:
			Path = ""
	if(ServerName is not None):
		server.addServerName(str(ServerName))
		store.put(serverkey, ServerName, ttl_secs=14400)
	if(UserName is not None):
		server.addUsername(str(UserName))
		store.put(userkey,UserName, ttl_secs=14400)
	if(Password is not None):
		server.addPassword(str(Password))
		store.put(passkey,Password, ttl_secs=14400)
	if Path and not Path.isspace():
		server.addPath(str(Path))
		store.put(pathkey,Path, ttl_secs=14400)
	else:
		server.addPath("/cds")
		store.put(pathkey,"/cds", ttl_secs=14400)
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
	
@app.route('/getTreeInfo',methods=['POST'])
def getTreeInfo():
	if(request is not None):
		pathDetails = request.json
	ssh = paramiko.SSHClient()
	# automatically add keys without requiring human intervention
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	pid = pathDetails[0]
	serverkey = 'ServerName'+str( pid)
	userkey = 'UserName'+str( pid)
	passkey = 'Password'+str( pid)
	pathkey = 'Path'+str( pid)
	content_hostName = str(store.get(serverkey))[2:len(str(store.get(serverkey)))-1]
	content_path = ''
	if(pathDetails is not None):
		if(len(pathDetails) > 1):
			content_path = str(pathDetails[1])
		else:
			content_path= str(store.get(pathkey))[2:len(str(store.get(pathkey)))-1]
	content_username = str(store.get(userkey))[2:len(str(store.get(userkey)))-1]
	content_password = str(store.get(passkey))[2:len(str(store.get(passkey)))-1]
	if(content_hostName.strip() == ""):
		hostName = 'midway001.rcc.uchicago.edu'
	else:
		hostName = content_hostName
	ssh.connect(hostName, username=content_username, password=content_password)
	ftp = ssh.open_sftp()
	#path = ' /cds/gagalli/DATA_COLLECTIONS/public/' + content_project
	path = content_path
	listObjects = []
	print(path)
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
		relPath = str(path + "/" + file).split(parentName,1)[1]
		dataFile.parent = parentName + "/" + relPath
		if 'd' in lstatout:
			prev = file
			dataFile.folder = "true"
			dataFile.lazy = 'true'
		listObjects.append(dataFile.__dict__)
	return jsonify({'listObjects':listObjects})	


class ProjectPath:
	projectName = ""
	Path=""

	
@app.route('/setPath',methods=['POST'])
def setPath():
	projPath = ProjectPath()
	projectPath = request.json
	pid = projectPath[0]
	type = str(projectPath[1])
	path = ""
	pathkey = 'Path'+str( pid)
	projkey = 'ProjectName'+str( pid)
	if("GET" in type):
		path = str(store.get(pathkey))[2:len(str(store.get(pathkey)))-1]
	else:
		store.put(pathkey,str(projectPath[2]), ttl_secs=14400)
		path = str(projectPath[2])
	parent = path.split("/")
	parentName = parent[len(parent)-1]
	print("here")
	print(parentName)
	projPath.projectName = parentName
	projPath.Path = path
	projNameMap['projName'+str(pid)] = parentName
	store.put(projkey,parentName, ttl_secs=14400)
	return jsonify({'projectPath':projPath.__dict__})	

@app.route('/getInfo',methods=['POST'])
def getInfo():
	iDetails = request.json
	print(iDetails)
	collections = ""
	tags = ""
	mainnotebookfile = ""
	globusid = ""
	infolabels = []
	infovalues = []
	infoList =[]
	pifnamelist = []
	pimnamelist = []
	pilnamelist = []
	info = Info()
	
	pid = iDetails[0]
	type = iDetails[1]
	infosaveas = iDetails[2]
	if "N/A" in infosaveas:
		for key in infoMap:
			if str(key).split('*')[0] not in infoList:
				if pid in str(key).split('*')[1]:
					infosaveas = str(key).split('*')[0]
	print(iDetails)
	if "GET" in type and "N/A" not in infosaveas:
		if str('pifname'+infosaveas+str( pid)) in store and store.get(str('pifname'+infosaveas+str( pid))) is not None:
			pifnamelist.append(str(store.get(str('pifname'+infosaveas+str( pid))))[2:len(str(store.get(str('pifname'+infosaveas+str( pid)))))-1])
		if str('pimname'+infosaveas+str( pid)) in store and store.get(str('pimname'+infosaveas+str( pid))) is not None:
			pimnamelist.append(str(store.get(str('pimname'+infosaveas+str( pid))))[2:len(str(store.get(str('pimname'+infosaveas+str( pid)))))-1])
		if str('pilname'+infosaveas+str( pid)) in store and store.get(str('pilname'+infosaveas+str( pid))) is not None:
			pilnamelist.append(str(store.get(str('pilname'+infosaveas+str( pid))))[2:len(str(store.get(str('pilname'+infosaveas+str( pid)))))-1])
		if str('collections'+infosaveas+str( pid)) in store and store.get(str('collections'+infosaveas+str( pid))) is not None:
			collections = str(store.get(str('collections'+infosaveas+str( pid))))[2:len(str(store.get(str('collections'+infosaveas+str( pid)))))-1]
		if str('tags'+infosaveas+str( pid)) in store and store.get(str('tags'+infosaveas+str( pid))) is not None:
			tags = str(store.get(str('tags'+infosaveas+str( pid))))[2:len(str(store.get(str('tags'+infosaveas+str( pid)))))-1]
		if str('mainnotebookfile'+infosaveas+str( pid)) in store and store.get(str('mainnotebookfile'+infosaveas+str( pid))) is not None:
			mainnotebookfile = str(store.get(str('mainnotebookfile'+infosaveas+str( pid))))[2:len(str(store.get(str('mainnotebookfile'+infosaveas+str( pid)))))-1]
		if str('globusid'+infosaveas+str( pid)) in store and store.get(str('globusid'+infosaveas+str( pid))) is not None:
			globusid = str(store.get(str('globusid'+infosaveas+str( pid))))[2:len(str(store.get(str('globusid'+infosaveas+str( pid)))))-1]
		if str('infolabels'+infosaveas+str( pid)) in store and store.get(str('infolabels'+infosaveas+str( pid))) is not None:
			infolabels.append(str(store.get(str('infolabels'+infosaveas+str( pid))))[2:len(str(store.get(str('infolabels'+infosaveas+str( pid)))))-1])
		if str('infovalues'+infosaveas+str( pid)) in store and store.get(str('infovalues'+infosaveas+str( pid))) is not None:
			infovalues.append(str(store.get(str('infovalues'+infosaveas+str( pid))))[2:len(str(store.get(str('infovalues'+infosaveas+str( pid)))))-1])
	if "POST" in type:
		for fname in eval(str(iDetails[3])):
			pifnamelist.append(str(fname))
		for mname in eval(str(iDetails[4])):
			pimnamelist.append(str(mname))
		for lname in eval(str(iDetails[5])):
			pilnamelist.append(str(lname))
		collections = str(iDetails[6])
		tags = str(iDetails[7])
		mainnotebookfile = str(iDetails[8])
		globusid = str(iDetails[9])
		for lab in eval(str(iDetails[10])):
			if "N/A" not in lab:
				infolabels.append(str(lab))
			else:
				infolabels.append("")
		for val in eval(str(iDetails[11])):
			if "N/A" not in val:
				infovalues.append(str(val))
			else:
				infovalues.append("")
	if "INIT" not in type and "N/A" not in infosaveas:
		length = max(len(pifnamelist),len(pimnamelist),len(pilnamelist))
		if length>0:
			for i in range(0,length):
				person = Person()
				try:
					person.addFirstName(pifnamelist[i])
				except IndexError:
					person.addFirstName("")
				try:
					if pimnamelist[i] and not pimnamelist[i].isspace() and "N/A" not in pimnamelist[i]:
						person.addMiddleName(pimnamelist[i])
					else:
						person.addMiddleName("")
				except IndexError:
					person.addMiddleName("")
				try:
					person.addLastName(pilnamelist[i])
				except IndexError:
					person.addLastName("")
				info.addName(person)
			store.put(str('pifname'+infosaveas+str( pid)), pifnamelist, ttl_secs=14400)
			store.put(str('pimname'+infosaveas+str( pid)), pimnamelist, ttl_secs=14400)
			store.put(str('pilname'+infosaveas+str( pid)), pilnamelist, ttl_secs=14400)
		#if len(pifnamelist)>0 and len(pimnamelist)>0 and len(pilnamelist)>0:
		#	info.addPiFirstName(pifnamelist)
		#	info.addPiMiddleName(pimnamelist)
		#	info.addPiLastName(pilnamelist)
		#	store.put(str('pifname'+infosaveas+str( pid)), pifnamelist, ttl_secs=14400)
		#	store.put(str('pimname'+infosaveas+str( pid)), pimnamelist, ttl_secs=14400)
		#	store.put(str('pilname'+infosaveas+str( pid)), pilnamelist, ttl_secs=14400)
		if collections and not collections.isspace():
			info.addCollection(collections)
			#session['pfirstName'] = fname
			store.put(str('collections'+infosaveas+str( pid)), collections, ttl_secs=14400)
		if tags and not tags.isspace():
			info.addTag(tags)
			#session['pfirstName'] = fname
			store.put(str('tags'+infosaveas+str( pid)), tags, ttl_secs=14400)
				
		if mainnotebookfile and not mainnotebookfile.isspace():
			if "N/A" not in mainnotebookfile:
				info.addNotebookFile(mainnotebookfile)
				store.put(str('mainnotebookfile'+infosaveas+str( pid)), mainnotebookfile, ttl_secs=14400)
				
		if globusid and not globusid.isspace():
			info.addGlobusId(globusid)
			store.put(str('globusid'+infosaveas+str( pid)), globusid, ttl_secs=14400)

		if len(infolabels)>0 and len(infovalues)>0:
			for f, b in zip(infolabels, infovalues):
				if "N/A" not in f and "N/A" not in b:
					info.addExtra(f,b)
					store.put(str('infolabels'+infosaveas+str(pid)), infolabels, ttl_secs=14400)
					store.put(str('infovalues'+infosaveas+str(pid)), infovalues, ttl_secs=14400)
		if "N/A" not in infosaveas:
			infoMap[str(infosaveas) +"*"+str(pid)] = info
			infoList.append(str(infosaveas))
			info.addSaveAs(infosaveas)
		print(info.__dict__)
		print(infoList)
	return jsonify({'infoDetails':info.__dict__,'infoList':infoList})
	
@app.route('/delInfo',methods=['POST'])
def delInfo():
	delsave = request.json
	pid = delsave[0]
	infosaveas = str(delsave[1])
	if infosaveas +"*"+ str(pid) in infoMap:
		infoMap.pop(infosaveas +"*"+ str(pid))
	#if str('pifname'+infosaveas+str( pid)) in store:
	#	store.delete('pifname'+infosaveas+str( pid))
	#if str('pimname'+infosaveas+str( pid)) in store:
	#	store.delete('pimname'+infosaveas+str( pid))
	#if str('pilname'+infosaveas+str( pid)) in store:
	#	store.delete('pilname'+infosaveas+str( pid))
	#if str('collections'+infosaveas+str( pid)) in store:
	#	store.delete('collections'+infosaveas+str( pid))
	#if str('tags'+infosaveas+str( pid)) in store:
	#	store.delete('tags'+infosaveas+str( pid))
	#if str('mainnotebookfile'+infosaveas+str( pid)) in store:
	#	store.delete('mainnotebookfile'+infosaveas+str( pid))
	#if str('globusid'+infosaveas+str( pid)) in store:
	#	store.delete('globusid'+infosaveas+str( pid))
	#if str('infolabels'+infosaveas+str( pid)) in store:
	#	store.delete('infolabels'+infosaveas+str( pid))
	#if str('infovalues'+infosaveas+str( pid)) in store:
	#	store.delete('infovalues'+infosaveas+str( pid))
	return jsonify({'infodetails':infosaveas})

@app.route('/getCharts',methods=['POST'])
def getCharts():
	cDetails = request.json
	pid = str(cDetails[0])
	chart = Chart("figure")
	type = str(cDetails[1])
	csaveas = str(cDetails[2])
	radioVal = ""
	caption = ""
	number = ""
	cfiles = ""
	cimagefiles = ""
	cnotebookfiles = ""
	cproperties = ""
	clabels = []
	cvalues = []
	chartsList = []
	#chart = Chart("")
	print(cDetails)
	if "INIT" in type:
		for key in chartMap:
			if str(pid) in key:
				if str(key).split('*')[0] not in chartsList:
					chartsList.append(str(key).split('*')[0])
	if "GET" in type:
		if str('radioVal'+csaveas+str( pid)) in store and store.get(str('radioVal'+csaveas+str( pid))) is not None:
			radioVal = str(store.get(str('radioVal'+csaveas+str( pid))))[2:len(str(store.get(str('radioVal'+csaveas+str( pid)))))-1]
		if str('caption'+csaveas+str( pid)) in store and store.get(str('caption'+csaveas+str( pid))) is not None:
			caption = str(store.get(str('caption'+csaveas+str( pid))))[2:len(str(store.get(str('caption'+csaveas+str( pid)))))-1]
		if str('number'+csaveas+str( pid)) in store and store.get(str('number'+csaveas+str( pid))) is not None:
			number = str(store.get(str('number'+csaveas+str( pid))))[2:len(str(store.get(str('number'+csaveas+str( pid)))))-1]
		if str('cfiles'+csaveas+str( pid)) in store and store.get(str('cfiles'+csaveas+str( pid))) is not None:
			cfiles = str(store.get(str('cfiles'+csaveas+str( pid))))[2:len(str(store.get(str('cfiles'+csaveas+str( pid)))))-1]
		if str('cimagefiles'+csaveas+str( pid)) in store and store.get(str('cimagefiles'+csaveas+str( pid))) is not None:
			cimagefiles = str(store.get(str('cimagefiles'+csaveas+str( pid))))[2:len(str(store.get(str('cimagefiles'+csaveas+str( pid)))))-1]
		if str('cnotebookfiles'+csaveas+str( pid)) in store and store.get(str('cnotebookfiles'+csaveas+str( pid))) is not None:
			cnotebookfiles = str(store.get(str('cnotebookfiles'+csaveas+str( pid))))[2:len(str(store.get(str('cnotebookfiles'+csaveas+str( pid)))))-1]
		if str('cproperties'+csaveas+str( pid)) in store and store.get(str('cproperties'+csaveas+str( pid))) is not None:
			cproperties = str(store.get(str('cproperties'+csaveas+str( pid))))[2:len(str(store.get(str('cproperties'+csaveas+str( pid)))))-1]
		if str('clabels'+csaveas+str( pid)) in store and store.get(str('clabels'+csaveas+str( pid))) is not None:
			clabels.append(str(store.get(str('clabels'+csaveas+str( pid))))[2:len(str(store.get(str('clabels'+csaveas+str( pid)))))-1])
		if str('cvalues'+csaveas+str( pid)) in store and store.get(str('cvalues'+csaveas+str( pid))) is not None:
			cvalues.append(str(store.get(str('cvalues'+csaveas+str( pid))))[2:len(str(store.get(str('cvalues'+csaveas+str( pid)))))-1])
	if "POST" in type:
		radioVal = str(cDetails[3])
		caption = str(cDetails[4])
		number = str(cDetails[5])
		cfiles = str(cDetails[6])
		cimagefiles = str(cDetails[7])
		cnotebookfiles = str(cDetails[8])
		cproperties = str(cDetails[9])
		if "N/A" not in str(cDetails[10]):
			clabels.append(str(cDetails[10]))
		if "N/A" not in str(cDetails[11]):
			cvalues.append(str(cDetails[11]))
	if "INIT" not in type:
		if radioVal and not radioVal.isspace():
			chart.addKind(radioVal)
			store.put(str('radioVal'+csaveas+str( pid)), radioVal, ttl_secs=14400)
		if caption and not caption.isspace():
			chart.addCaption(caption)
			store.put(str('caption'+csaveas+str( pid)), caption, ttl_secs=14400)
		if number and not number.isspace():
			chart.addNumber(number)
			store.put(str('number'+csaveas+str( pid)), number, ttl_secs=14400)
		if cfiles and not cfiles.isspace():
			chart.addFile(cfiles)
			store.put(str('cfiles'+csaveas+str( pid)), cfiles, ttl_secs=14400)
		if cimagefiles and not cimagefiles.isspace():
			chart.addImageFile(cimagefiles)
			store.put(str('cimagefiles'+csaveas+str( pid)), cimagefiles, ttl_secs=14400)
		if cnotebookfiles and not cnotebookfiles.isspace():
			chart.addNotebookFile(cnotebookfiles)
			store.put(str('cnotebookfiles'+csaveas+str( pid)), cnotebookfiles, ttl_secs=14400)
		if cproperties and not cproperties.isspace():
			chart.addProperty(cproperties)
			store.put(str('cproperties'+csaveas+str(pid)), cproperties, ttl_secs=14400)
		if len(clabels)>0 and len(cvalues)>0:
			for f, b in zip(clabels, cvalues):
				chart.addExtra(f,b)
				store.put(str('clabels'+csaveas+str(pid)), clabels, ttl_secs=14400)
				store.put(str('cvalues'+csaveas+str(pid)), cvalues, ttl_secs=14400)
		if "N/A" not in csaveas:
			chartMap[str(csaveas) + "*" + str(pid)] = chart
			chartsList.append(str(csaveas))
			chart.addSaveAs(csaveas)
	print(chart.__dict__)
	return jsonify({'cdetails':chart.__dict__,'chartList':chartsList})
	

@app.route('/delCharts',methods=['POST'])
def delCharts():
	delsave = request.json
	pid = str(delsave[0])
	csaveas = str(delsave[1])
	if csaveas+"*"+pid in chartMap:
		chartMap.pop(csaveas+"*"+pid)
	#if str('radioVal'+csaveas+str( pid)) in store:
	#	store.delete('radioVal'+csaveas+str( pid))
	#if str('caption'+csaveas+str( pid)) in store:
	#	store.delete('caption'+csaveas+str( pid))
	#if str('number'+csaveas+str( pid)) in store:
	#	store.delete('number'+csaveas+str( pid))
	#if str('cfiles'+csaveas+str( pid)) in store:
	#	store.delete('cfiles'+csaveas+str( pid))
	#if str('cimagefiles'+csaveas+str( pid)) in store:
	#	store.delete('cimagefiles'+csaveas+str( pid))
	#if str('cnotebookfiles'+csaveas+str( pid)) in store:
	#	store.delete('cnotebookfiles'+csaveas+str( pid))
	#if str('cproperties'+csaveas+str( pid)) in store:
	#	store.delete('cproperties'+csaveas+str( pid))
	return jsonify({'delcdetails':csaveas})
	
@app.route('/getTools',methods=['POST'])
def getTools():
	toolsDetails = request.json
	pid = str(toolsDetails[0])
	type = str(toolsDetails[1])
	toolssaveas = str(toolsDetails[2])
	kind = ""
	packagename = ""
	programname = ""
	version = ""
	toolsurls = ""
	facilityname = ""
	measurement = ""
	toolseurls = ""
	toolslabels = []
	toolsvalues = []
	toolsList = []
	tools = Tool(str(kind))
	print(toolsDetails)
	if "INIT" in type:
		for key in toolsMap:
			if str(pid) in key:
				if str(key).split('*')[0] not in toolsList:
					toolsList.append(str(key).split('*')[0])
	if "GET" in type:
		if str('kind'+toolssaveas+str( pid)) in store and store.get(str('kind'+toolssaveas+str( pid))) is not None:
			kind = str(store.get(str('kind'+toolssaveas+str( pid))))[2:len(str(store.get(str('kind'+toolssaveas+str( pid)))))-1]
		if str('packagename'+toolssaveas+str( pid)) in store and store.get(str('packagename'+toolssaveas+str( pid))) is not None:
			packagename = str(store.get(str('packagename'+toolssaveas+str( pid))))[2:len(str(store.get(str('packagename'+toolssaveas+str( pid)))))-1]
		if str('programname'+toolssaveas+str( pid)) in store and store.get(str('programname'+toolssaveas+str( pid))) is not None:
			programname = str(store.get(str('programname'+toolssaveas+str( pid))))[2:len(str(store.get(str('programname'+toolssaveas+str( pid)))))-1]
		if str('version'+toolssaveas+str( pid)) in store and store.get(str('version'+toolssaveas+str( pid))) is not None:
			version = str(store.get(str('version'+toolssaveas+str( pid))))[2:len(str(store.get(str('version'+toolssaveas+str( pid)))))-1]
		if str('toolsurls'+toolssaveas+str( pid)) in store and store.get(str('toolsurls'+toolssaveas+str( pid))) is not None:
			toolsurls = str(store.get(str('toolsurls'+toolssaveas+str( pid))))[2:len(str(store.get(str('toolsurls'+toolssaveas+str( pid)))))-1]
		if str('facilityname'+toolssaveas+str( pid)) in store and store.get(str('facilityname'+toolssaveas+str( pid))) is not None:
			facilityname = str(store.get(str('facilityname'+toolssaveas+str( pid))))[2:len(str(store.get(str('facilityname'+toolssaveas+str( pid)))))-1]
		if str('measurement'+toolssaveas+str( pid)) in store and store.get(str('measurement'+toolssaveas+str( pid))) is not None:
			measurement = str(store.get(str('measurement'+toolssaveas+str( pid))))[2:len(str(store.get(str('measurement'+toolssaveas+str( pid)))))-1]
		if str('toolseurls'+toolssaveas+str( pid)) in store and store.get(str('toolseurls'+toolssaveas+str( pid))) is not None:
			toolseurls = str(store.get(str('toolseurls'+toolssaveas+str( pid))))[2:len(str(store.get(str('toolseurls'+toolssaveas+str( pid)))))-1]
		if str('toolslabels'+toolssaveas+str( pid)) in store and store.get(str('toolslabels'+toolssaveas+str( pid))) is not None:
			toolslabels.append(str(store.get(str('toolslabels'+toolssaveas+str( pid))))[2:len(str(store.get(str('toolslabels'+toolssaveas+str( pid)))))-1])
		if str('toolsvalues'+toolssaveas+str( pid)	) in store and store.get(str('toolsvalues'+toolssaveas+str( pid))) is not None:
			toolsvalues.append(str(store.get(str('toolsvalues'+toolssaveas+str( pid))))[2:len(str(store.get(str('toolsvalues'+toolssaveas+str( pid)))))-1])
	if "POST" in type:
		kind = str(toolsDetails[3])
		if "Software" in kind:
			packagename = str(toolsDetails[4])
			programname = str(toolsDetails[5])
			version = str(toolsDetails[6])
			toolsurls = str(toolsDetails[7])
			if "N/A" not in str(toolsDetails[8]):
				toolslabels.append(str(toolsDetails[8]))
			if "N/A" not in str(toolsDetails[9]):
				toolsvalues.append(str(toolsDetails[9]))
		else:
			facilityname = str(toolsDetails[3])
			measurement = str(toolsDetails[4])
			toolseurls = str(toolsDetails[5])
			if "N/A" not in str(toolsDetails[6]):
				toolslabels.append(str(toolsDetails[6]))
			if "N/A" not in str(toolsDetails[7]):
				toolsvalues.append(str(toolsDetails[7]))
	if "INIT" not in type:
		tools = Tool(str(kind))
		tools.addKind(str(kind))
		if kind and not kind.isspace():
			store.put(str('kind'+toolssaveas+str( pid)), kind, ttl_secs=14400)
		if "Software" in kind:
			if packagename and not packagename.isspace():
				tools.addPackageName(packagename)
				store.put(str('packagename'+toolssaveas+str( pid)), packagename, ttl_secs=14400)
			if programname and not programname.isspace():
				tools.addProgramName(programname)
				store.put(str('programname'+toolssaveas+str( pid)), programname, ttl_secs=14400)
			if version and not version.isspace():
				tools.addVersion(version)
				store.put(str('version'+toolssaveas+str( pid)), version, ttl_secs=14400)
			if toolsurls and not toolsurls.isspace() and "N/A" not in toolsurls:
				tools.addURL(toolsurls)
				store.put(str('toolsurls'+toolssaveas+str( pid)), toolsurls, ttl_secs=14400)
			if len(toolslabels)>0 and len(toolsvalues)>0:
				for f, b in zip(toolslabels, toolsvalues):
					tools.addExtra(f,b)
					store.put(str('toolslabels'+toolssaveas+str(pid)), toolslabels, ttl_secs=14400)
					store.put(str('toolsvalues'+toolssaveas+str(pid)), toolsvalues, ttl_secs=14400)
		else:
			if facilityname and not facilityname.isspace():
				tools.addFacilityName(facilityname)
				store.put(str('facilityname'+toolssaveas+str( pid)), facilityname, ttl_secs=14400)
					
			if measurement and not measurement.isspace():
				tools.addMeasurement(measurement)
				store.put(str('measurement'+toolssaveas+str( pid)), measurement, ttl_secs=14400)
					
			if toolseurls and not toolseurls.isspace() and "N/A" not in toolseurls:
				tools.addExpURL(toolseurls)
				store.put(str('toolseurls'+toolssaveas+str(pid)), toolseurls, ttl_secs=14400)
			if len(toolslabels)>0 and len(toolsvalues)>0:
				for f, b in zip(toolslabels, toolsvalues):
					tools.addExtra(f,b)
					store.put(str('toolslabels'+toolssaveas+str(pid)), toolslabels, ttl_secs=14400)
					store.put(str('toolsvalues'+toolssaveas+str(pid)), toolsvalues, ttl_secs=14400)
		if "N/A" not in toolssaveas:
			toolsMap[str(toolssaveas) +"*"+str(pid)] = tools
			toolsList.append(str(toolssaveas))
			tools.addSaveAs(toolssaveas)
	return jsonify({'toolsdetails':tools.__dict__,'toolsList':toolsList})
	

@app.route('/delTools',methods=['POST'])
def delTools():
	delsave = request.json
	pid = str(delsave[0])
	toolssaveas = str(delsave[1])
	if toolssaveas +"*"+ str(pid) in chartMap:
		chartMap.pop(str(toolssaveas) +"*"+ str(pid))
	#if str('radioVal'+toolssaveas+str( pid)) in store:
	#	store.delete('radioVal'+toolssaveas+str( pid))
	#if str('caption'+toolssaveas+str( pid)) in store:
	#	store.delete('caption'+toolssaveas+str( pid))
	#if str('number'+toolssaveas+str( pid)) in store:
	#	store.delete('number'+toolssaveas+str( pid))
	#if str('cfiles'+toolssaveas+str( pid)) in store:
	#	store.delete('cfiles'+toolssaveas+str( pid))
	#if str('cimagefiles'+toolssaveas+str( pid)) in store:
	#	store.delete('cimagefiles'+toolssaveas+str( pid))
	#if str('cnotebookfiles'+toolssaveas+str( pid)) in store:
	#	store.delete('cnotebookfiles'+toolssaveas+str( pid))
	#if str('cproperties'+toolssaveas+str( pid)) in store:
	#	store.delete('cproperties'+toolssaveas+str( pid))
	return jsonify({'toolsdetails':toolssaveas})
	
	
@app.route('/getDatasets',methods=['POST'])
def getDatasets():
	datasetdetails = request.json
	datasetfiles = ""
	datasetdescriptions = ""
	dataseturls = ""
	datasetsaveas = ""
	datasetlabel = []
	datasetval = []
	datasetList = []
	dataset = Dataset()
	pid = datasetdetails[0]
	type = datasetdetails[1]
	datasetsaveas = datasetdetails[2]
	print(datasetdetails)
	if "INIT" in type:
		for key in datasetsMap:
			if str(pid) in key:
				if str(key).split('*')[0] not in datasetList:
					datasetList.append(str(key).split('*')[0])
	if "GET" in type:
		if str('datasetfiles'+datasetsaveas+str( pid)) in store and store.get(str('datasetfiles'+datasetsaveas+str( pid))) is not None:
			datasetfiles = str(store.get(str('datasetfiles'+datasetsaveas+str( pid))))[2:len(str(store.get(str('datasetfiles'+datasetsaveas+str( pid)))))-1]
		if str('datasetdescriptions'+datasetsaveas+str( pid)) in store and store.get(str('datasetdescriptions'+datasetsaveas+str( pid))) is not None:
			datasetdescriptions = str(store.get(str('datasetdescriptions'+datasetsaveas+str( pid))))[2:len(str(store.get(str('datasetdescriptions'+datasetsaveas+str( pid)))))-1]
		if str('dataseturls'+datasetsaveas+str( pid)) in store and store.get(str('dataseturls'+datasetsaveas+str( pid))) is not None:
			dataseturls = str(store.get(str('dataseturls'+datasetsaveas+str( pid))))[2:len(str(store.get(str('dataseturls'+datasetsaveas+str( pid)))))-1]
		if str('datasetlabel'+datasetsaveas+str( pid)) in store and store.get(str('datasetlabel'+datasetsaveas+str( pid))) is not None:
			datasetlabel.append(str(store.get(str('datasetlabel'+datasetsaveas+str( pid))))[2:len(str(store.get(str('datasetlabel'+datasetsaveas+str( pid)))))-1])
		if str('datasetval'+datasetsaveas+str( pid)) in store and store.get(str('datasetval'+datasetsaveas+str( pid))) is not None:
			datasetval.append(str(store.get(str('datasetval'+datasetsaveas+str( pid))))[2:len(str(store.get(str('datasetval'+datasetsaveas+str( pid)))))-1])
	if "POST" in type:
		datasetfiles = str(datasetdetails[3])
		datasetdescriptions = str(datasetdetails[4])
		dataseturls = str(datasetdetails[5])
		for lab in list(datasetdetails[6]):
			if "N/A" not in lab:
				datasetlabel.append(str(lab))
		for val in list(datasetdetails[7]):
			if "N/A" not in val:
				datasetval.append(str(val))
	if "INIT" not in type:
		if dataseturls and not dataseturls.isspace() and "N/A" not in dataseturls:
			if "N/A" not in dataseturls:
				dataset.addURL(dataseturls)
				store.put(str('dataseturls'+datasetsaveas+str( pid)), dataseturls, ttl_secs=14400)
				
		if datasetdescriptions and not datasetdescriptions.isspace():
			dataset.addReadme(datasetdescriptions)
			#session['pfirstName'] = fname
			if str('datasetdescriptions'+datasetsaveas+str( pid)) not in store:
				store.put(str('datasetdescriptions'+datasetsaveas+str( pid)), datasetdescriptions, ttl_secs=14400)
				
		if datasetfiles and not datasetfiles.isspace():
			dataset.addFile(datasetfiles)
			#session['pfirstName'] = fname
			if str('datasetfiles'+datasetsaveas+str( pid)) not in store:
				store.put(str('datasetfiles'+datasetsaveas+str( pid)), datasetfiles, ttl_secs=14400)

		if len(datasetlabel)>0 and len(datasetval)>0:
			for f, b in zip(datasetlabel, datasetval):
				if "N/A" not in f and "N/A" not in b:
					dataset.addExtra(f,b)
					store.put(str('datasetlabel'+datasetsaveas+str(pid)), datasetlabel, ttl_secs=14400)
					store.put(str('datasetval'+datasetsaveas+str(pid)), datasetval, ttl_secs=14400)
		if "N/A" not in datasetsaveas:
			datasetsMap[str(datasetsaveas) +"*"+str(pid)] = dataset
			datasetList.append(str(datasetsaveas))
			dataset.addSaveAs(datasetsaveas)
		print(dataset)
		print(datasetList)
	return jsonify({'datasetsdetails':dataset.__dict__,'datasetslist':datasetList})
	
@app.route('/delDatasets',methods=['POST'])
def delDatasets():
	delsave = request.json
	pid = str(delsave[0])
	datasetsaveas = str(delsave[1])
	if datasetsaveas +"*"+ str(pid) in datasetsMap:
		datasetsMap.pop(datasetsaveas +"*"+ str(pid))
	#if str('datasetfiles'+datasetsaveas+str( pid)) in store:
	#	store.delete('datasetfiles'+datasetsaveas+str( pid))
	#if str('datasetdescriptions'+datasetsaveas+str( pid)) in store:
	#	store.delete('datasetdescriptions'+datasetsaveas+str( pid))
	#if str('dataseturls'+datasetsaveas+str( pid)) in store:
	#	store.delete('dataseturls'+datasetsaveas+str( pid))
	#if str('datasetlabel'+datasetsaveas+str( pid)) in store:
	#	store.delete('datasetlabel'+datasetsaveas+str( pid))
	#if str('datasetval'+datasetsaveas+str( pid)) in store:
	#	store.delete('datasetval'+datasetsaveas+str( pid))
	return jsonify({'datasetsdetails':datasetsaveas})
	
@app.route('/getScripts',methods=['POST'])
def getScripts():
	scriptdetails = request.json
	scriptfiles = ""
	scriptdescriptions = ""
	scripturls = ""
	scriptsaveas = ""
	scriptlabel = []
	scriptval = []
	scriptList = []
	script = Script()
	pid = scriptdetails[0]
	type = scriptdetails[1]
	scriptsaveas = scriptdetails[2]
	print(scriptdetails)
	if "INIT" in type:
		for key in scriptsMap:
			if str(pid) in key:
				if str(key).split('*')[0] not in scriptList:
					scriptList.append(str(key).split('*')[0])
	if "GET" in type:
		if str('scriptfiles'+scriptsaveas+str( pid)) in store and store.get(str('scriptfiles'+scriptsaveas+str( pid))) is not None:
			scriptfiles = str(store.get(str('scriptfiles'+scriptsaveas+str( pid))))[2:len(str(store.get(str('scriptfiles'+scriptsaveas+str( pid)))))-1]
		if str('scriptdescriptions'+scriptsaveas+str( pid)) in store and store.get(str('scriptdescriptions'+scriptsaveas+str( pid))) is not None:
			scriptdescriptions = str(store.get(str('scriptdescriptions'+scriptsaveas+str( pid))))[2:len(str(store.get(str('scriptdescriptions'+scriptsaveas+str( pid)))))-1]
		if str('scripturls'+scriptsaveas+str( pid)) in store and store.get(str('scripturls'+scriptsaveas+str( pid))) is not None:
			scripturls = str(store.get(str('scripturls'+scriptsaveas+str( pid))))[2:len(str(store.get(str('scripturls'+scriptsaveas+str( pid)))))-1]
		if str('scriptlabel'+scriptsaveas+str( pid)) in store and store.get(str('scriptlabel'+scriptsaveas+str( pid))) is not None:
			scriptlabel.append(str(store.get(str('scriptlabel'+scriptsaveas+str( pid))))[2:len(str(store.get(str('scriptlabel'+scriptsaveas+str( pid)))))-1])
		if str('scriptval'+scriptsaveas+str( pid)) in store and store.get(str('scriptval'+scriptsaveas+str( pid))) is not None:
			scriptval.append(str(store.get(str('scriptval'+scriptsaveas+str( pid))))[2:len(str(store.get(str('scriptval'+scriptsaveas+str( pid)))))-1])
	if "POST" in type:
		scriptfiles = str(scriptdetails[3])
		scriptdescriptions = str(scriptdetails[4])
		scripturls = str(scriptdetails[5])
		for lab in list(scriptdetails[6]):
			if "N/A" not in lab:
				scriptlabel.append(str(lab))
		for val in list(scriptdetails[7]):
			if "N/A" not in val:
				scriptval.append(str(val))
	if "INIT" not in type:
		if scripturls and not scripturls.isspace():
			if "N/A" not in scripturls:
				script.addURL(scripturls)
				store.put(str('scripturls'+scriptsaveas+str( pid)), scripturls, ttl_secs=14400)
				
		if scriptdescriptions and not scriptdescriptions.isspace():
			script.addReadme(scriptdescriptions)
			store.put(str('scriptdescriptions'+scriptsaveas+str( pid)), scriptdescriptions, ttl_secs=14400)
				
		if scriptfiles and not scriptfiles.isspace():
			script.addFile(scriptfiles)
			store.put(str('scriptfiles'+scriptsaveas+str( pid)), scriptfiles, ttl_secs=14400)

		if len(scriptlabel)>0 and len(scriptval)>0:
			for f, b in zip(scriptlabel, scriptval):
				if "N/A" not in f and "N/A" not in b:
					script.addExtra(f,b)
					store.put(str('scriptlabel'+scriptsaveas+str(pid)), scriptlabel, ttl_secs=14400)
					store.put(str('scriptval'+scriptsaveas+str(pid)), scriptval, ttl_secs=14400)
		if "N/A" not in scriptsaveas:
			scriptList.append(str(scriptsaveas))
			script.addSaveAs(scriptsaveas)
			scriptsMap[str(scriptsaveas) +"*"+str(pid)] = script
		print(script)
		print(scriptList)
	return jsonify({'scriptsdetails':script.__dict__,'scriptlist':scriptList})
	
@app.route('/delScripts',methods=['POST'])
def delScripts():
	delsave = request.json
	pid = delsave[0]
	scriptsaveas = str(delsave[1])
	if scriptsaveas +"*"+ str(pid) in scriptsMap:
		scriptsMap.pop(str(scriptsaveas) +"*"+ str(pid))
	#if str('scriptfiles'+scriptsaveas+str( pid)) in store:
	#	store.delete('scriptfiles'+scriptsaveas+str( pid))
	#if str('scriptdescriptions'+scriptsaveas+str( pid)) in store:
	#	store.delete('scriptdescriptions'+scriptsaveas+str( pid))
	#if str('scripturls'+scriptsaveas+str( pid)) in store:
	#	store.delete('scripturls'+scriptsaveas+str( pid))
	#if str('scriptlabel'+scriptsaveas+str( pid)) in store:
	#	store.delete('scriptlabel'+scriptsaveas+str( pid))
	#if str('scriptval'+scriptsaveas+str( pid)) in store:
	#	store.delete('scriptval'+scriptsaveas+str( pid))
	return jsonify({'scriptdetails':scriptsaveas})
	
	
@app.route('/getReference',methods=['POST'])
def getReference():
	refdetails = request.json
	kind = ""
	title = ""
	journalFull = ""
	journalAbbr = ""
	volume = ""
	page = ""
	year = ""
	DOI = ""
	publishedDate = ""
	receivedDate = ""
	publishedAbstract = ""
	urls = ""
	refsaveas = ""
	reflabel = []
	refval = []
	refList = []
	authorfnamelist = []
	authormnamelist = []
	authorlnamelist = []
	pid = refdetails[0]
	type = refdetails[1]
	refsaveas = refdetails[2]
	kind = str(refdetails[3])
	kind = "article"
	ref = Reference(kind)
	print(refdetails)
	if "N/A" in refsaveas:
		for key in referenceMap:
			if pid in str(key).split('*')[1]:
				refsaveas = str(key).split('*')[0]
	if "GET" in type and "N/A" not in refsaveas:
		if str('kind'+refsaveas+str( pid)) in store and store.get(str('kind'+refsaveas+str( pid))) is not None:
			kind = str(store.get(str('kind'+refsaveas+str( pid))))[2:len(str(store.get(str('kind'+refsaveas+str( pid)))))-1]
		if str('authorfname'+refsaveas+str( pid)) in store and store.get(str('authorfname'+refsaveas+str( pid))) is not None:
			authorfnamelist.append(str(store.get(str('authorfname'+refsaveas+str( pid))))[2:len(str(store.get(str('authorfname'+refsaveas+str( pid)))))-1])
		if str('authormname'+refsaveas+str( pid)) in store and store.get(str('authormname'+refsaveas+str( pid))) is not None:
			authormnamelist.append(str(store.get(str('authormname'+refsaveas+str( pid))))[2:len(str(store.get(str('authormname'+refsaveas+str( pid)))))-1])
		if str('authorlname'+refsaveas+str( pid)) in store and store.get(str('authorlname'+refsaveas+str( pid))) is not None:
			authorlnamelist.append(str(store.get(str('authorlname'+refsaveas+str( pid))))[2:len(str(store.get(str('authorlname'+refsaveas+str( pid)))))-1])
		if str('title'+refsaveas+str( pid)) in store and store.get(str('title'+refsaveas+str( pid))) is not None:
			title = str(store.get(str('title'+refsaveas+str( pid))))[2:len(str(store.get(str('title'+refsaveas+str( pid)))))-1]
		if str('journalFull'+refsaveas+str( pid)) in store and store.get(str('journalFull'+refsaveas+str( pid))) is not None:
			journalFull = str(store.get(str('journalFull'+refsaveas+str( pid))))[2:len(str(store.get(str('journalFull'+refsaveas+str( pid)))))-1]
		if str('journalAbbr'+refsaveas+str( pid)) in store and store.get(str('journalAbbr'+refsaveas+str( pid))) is not None:
			journalAbbr = str(store.get(str('journalAbbr'+refsaveas+str( pid))))[2:len(str(store.get(str('journalAbbr'+refsaveas+str( pid)))))-1]
		if str('volume'+refsaveas+str( pid)) in store and store.get(str('volume'+refsaveas+str( pid))) is not None:
			volume = str(store.get(str('volume'+refsaveas+str( pid))))[2:len(str(store.get(str('volume'+refsaveas+str( pid)))))-1]
		if str('page'+refsaveas+str( pid)) in store and store.get(str('page'+refsaveas+str( pid))) is not None:
			page = str(store.get(str('page'+refsaveas+str( pid))))[2:len(str(store.get(str('page'+refsaveas+str( pid)))))-1]
		if str('year'+refsaveas+str( pid)) in store and store.get(str('year'+refsaveas+str( pid))) is not None:
			year = str(store.get(str('year'+refsaveas+str( pid))))[2:len(str(store.get(str('year'+refsaveas+str( pid)))))-1]
		if str('publishedDate'+refsaveas+str( pid)) in store and store.get(str('publishedDate'+refsaveas+str( pid))) is not None:
			publishedDate = str(store.get(str('publishedDate'+refsaveas+str( pid))))[2:len(str(store.get(str('publishedDate'+refsaveas+str( pid)))))-1]
		if str('receivedDate'+refsaveas+str( pid)) in store and store.get(str('receivedDate'+refsaveas+str( pid))) is not None:
			receivedDate = str(store.get(str('receivedDate'+refsaveas+str( pid))))[2:len(str(store.get(str('receivedDate'+refsaveas+str( pid)))))-1]
		if str('DOI'+refsaveas+str( pid)) in store and store.get(str('DOI'+refsaveas+str( pid))) is not None:
			DOI = str(store.get(str('DOI'+refsaveas+str( pid))))[2:len(str(store.get(str('DOI'+refsaveas+str( pid)))))-1]
		if str('publishedAbstract'+refsaveas+str( pid)) in store and store.get(str('publishedAbstract'+refsaveas+str( pid))) is not None:
			publishedAbstract = str(store.get(str('publishedAbstract'+refsaveas+str( pid))))[2:len(str(store.get(str('publishedAbstract'+refsaveas+str( pid)))))-1]
		if str('urls'+refsaveas+str( pid)) in store and store.get(str('urls'+refsaveas+str( pid))) is not None:
			urls = str(store.get(str('urls'+refsaveas+str( pid))))[2:len(str(store.get(str('urls'+refsaveas+str( pid)))))-1]
		if str('reflabel'+refsaveas+str( pid)) in store and store.get(str('reflabel'+refsaveas+str( pid))) is not None:
			reflabel.append(str(store.get(str('reflabel'+refsaveas+str( pid))))[2:len(str(store.get(str('reflabel'+refsaveas+str( pid)))))-1])
		if str('refval'+refsaveas+str( pid)) in store and store.get(str('refval'+refsaveas+str( pid))) is not None:
			refval.append(str(store.get(str('refval'+refsaveas+str( pid))))[2:len(str(store.get(str('refval'+refsaveas+str( pid)))))-1])
	if "POST" in type:
		for fname in eval(str(refdetails[4])):
			authorfnamelist.append(str(fname))
		for mname in eval(str(refdetails[5])):
			authormnamelist.append(str(mname))
		for lname in eval(str(refdetails[6])):
			authorlnamelist.append(str(lname))
		title = str(refdetails[7])
		journalFull = str(refdetails[8])
		journalAbbr = str(refdetails[9])
		volume = str(refdetails[10])
		page = str(refdetails[11])
		year = str(refdetails[12])
		publishedDate = str(refdetails[13])
		receivedDate = str(refdetails[14])
		DOI = str(refdetails[15])
		publishedAbstract = str(refdetails[16])
		urls = str(refdetails[17])
		for lab in list(refdetails[18]):
			if "N/A" not in lab:
				reflabel.append(str(lab))
		for val in list(refdetails[19]):
			if "N/A" not in val:
				refval.append(str(val))
	if "INIT" not in type and "N/A" not in refsaveas:
		if kind and not kind.isspace():
			if "N/A" not in kind:
				store.put(str('kind'+refsaveas+str( pid)), kind, ttl_secs=14400)
		
		length = max(len(authorfnamelist),len(authormnamelist),len(authorlnamelist))
		if length>0:
			for i in range(0,length):
				person = Person()
				try:
					person.addFirstName(authorfnamelist[i])
				except IndexError:
					person.addFirstName("")
				try:
					if authormnamelist[i] and not authormnamelist[i].isspace() and "N/A" not in authormnamelist[i]:
						person.addMiddleName(authormnamelist[i])
					else:
						person.addMiddleName("")
				except IndexError:
					person.addMiddleName("")
				try:
					person.addLastName(authorlnamelist[i])
				except IndexError:
					person.addLastName("")
				ref.addAuthor(person)
			store.put(str('authorfname'+refsaveas+str( pid)), authorfnamelist, ttl_secs=14400)
			store.put(str('authormname'+refsaveas+str( pid)), authormnamelist, ttl_secs=14400)
			store.put(str('authorlname'+refsaveas+str( pid)), authorlnamelist, ttl_secs=14400)		
		if title and not title.isspace():
			if "N/A" not in title:
				ref.addTitle(title)
				store.put(str('title'+refsaveas+str( pid)), title, ttl_secs=14400)
		if journalFull and not journalFull.isspace():
			if "N/A" not in journalFull:
				store.put(str('journalFull'+refsaveas+str( pid)), journalFull, ttl_secs=14400)
				
		if journalAbbr and not journalAbbr.isspace():
			#session['pfirstName'] = fname
			ref.addJournal(journalFull,journalAbbr)
			if str('journalAbbr'+refsaveas+str( pid)) not in store:
				store.put(str('journalAbbr'+refsaveas+str( pid)), journalAbbr, ttl_secs=14400)
				
		if volume and not volume.isspace():
			ref.addVolume(volume)
			store.put(str('volume'+refsaveas+str( pid)), volume, ttl_secs=14400)
		
		if page and not page.isspace():
			if "N/A" not in page:
				ref.addPage(page)
				store.put(str('page'+refsaveas+str( pid)), page, ttl_secs=14400)
				
		if year and not year.isspace():
			ref.addYear(int(year))
			store.put(str('year'+refsaveas+str( pid)), year, ttl_secs=14400)
			
		if publishedDate and not publishedDate.isspace():
			if "N/A" not in publishedDate:
				ref.addPublishedDate(publishedDate)
				store.put(str('publishedDate'+refsaveas+str( pid)), publishedDate, ttl_secs=14400)
			
		if receivedDate and not receivedDate.isspace():
			if "N/A" not in receivedDate:
				ref.addReceivedDate(receivedDate)
				store.put(str('receivedDate'+refsaveas+str( pid)), receivedDate, ttl_secs=14400)
				
		if DOI and not DOI.isspace():
			if "N/A" not in DOI:
				ref.addDOI(DOI)
				store.put(str('DOI'+refsaveas+str( pid)), DOI, ttl_secs=14400)
				
		if publishedAbstract and not publishedAbstract.isspace():
			if "N/A" not in publishedAbstract:
				ref.addPublishedAbstract(publishedAbstract)
				store.put(str('publishedAbstract'+refsaveas+str( pid)), publishedAbstract, ttl_secs=14400)
				
		if urls and not urls.isspace():
			if "N/A" not in urls:
				ref.addURL(urls)
				store.put(str('urls'+refsaveas+str( pid)), urls, ttl_secs=14400)
				
		if len(reflabel)>0 and len(refval)>0:
			for f, b in zip(reflabel, refval):
				if "N/A" not in f and "N/A" not in b:
					ref.addExtra(f,b)
					store.put(str('reflabel'+refsaveas+str(pid)), reflabel, ttl_secs=14400)
					store.put(str('refval'+refsaveas+str(pid)), refval, ttl_secs=14400)
					
		if "N/A" not in refsaveas:
			refList.append(str(refsaveas))
			ref.addSaveAs(refsaveas)
			referenceMap[str(refsaveas) +"*"+str(pid)] = ref
		print(ref)
		print(refList)
	return jsonify({'referencedetails':ref.__dict__,'refList':refList})
	
@app.route('/delReference',methods=['POST'])
def delReference():
	delsave = request.json
	pid = delsave[0]
	refsaveas = str(delsave[1])
	if refsaveas +"*"+ str(pid) in referenceMap:
		referenceMap.pop(refsaveas +"*"+ str(pid))
	#if str('kind'+refsaveas+str( pid)) in store:
	#	store.delete('kind'+refsaveas+str( pid))
	#if str('authors'+refsaveas+str( pid)) in store:
	#	store.delete('authors'+refsaveas+str( pid))
	#if str('title'+refsaveas+str( pid)) in store:
	#	store.delete('title'+refsaveas+str( pid))
	#if str('journalFull'+refsaveas+str( pid)) in store:
	#	store.delete('journalFull'+refsaveas+str( pid))
	#if str('journalAbbr'+refsaveas+str( pid)) in store:
	#	store.delete('journalAbbr'+refsaveas+str( pid))
	#if str('volume'+refsaveas+str( pid)) in store:
	#	store.delete('volume'+refsaveas+str( pid))
	#if str('page'+refsaveas+str( pid)) in store:
	#	store.delete('page'+refsaveas+str( pid))
	#if str('year'+refsaveas+str( pid)) in store:
	#	store.delete('year'+refsaveas+str( pid))
	#if str('DOI'+refsaveas+str( pid)) in store:
	#	store.delete('DOI'+refsaveas+str( pid))	
	#if str('publishedAbstract'+refsaveas+str( pid)) in store:
	#	store.delete('publishedAbstract'+refsaveas+str( pid))
	#if str('urls'+refsaveas+str( pid)) in store:
	#	store.delete('urls'+refsaveas+str( pid))			
	#if str('reflabel'+refsaveas+str( pid)) in store:
	#	store.delete('reflabel'+refsaveas+str( pid))
	#if str('refval'+refsaveas+str( pid)) in store:
	#	store.delete('refval'+refsaveas+str( pid))
	return jsonify({'refdetails':refsaveas})

	
@app.route('/getWorkflow',methods=['POST'])
def getWorkflow():
	workflowsave = request.json
	pid = str(workflowsave[0])
	type = str(workflowsave[1])
	workflow = WorkflowCreator()
	if "GET" in type:
		for chart in chartMap:
			if pid in chart:
				charts = Chart("figure")
				charts = copy(chartMap[chart])
				charts = charts.__dict__
				workflow.addChart(charts['desc']['saveas'])
		for tool in toolsMap:
			if pid in tool:
				tools = Tool("Experiment")
				tools = copy(toolsMap[tool])
				tools = tools.__dict__
				workflow.addTool(tools['desc']['saveas'])
			
		for dataset in datasetsMap:
			if pid in dataset:
				datasets = Dataset()
				datasets = copy(datasetsMap[dataset])
				datasets = datasets.__dict__
				workflow.addDataset(datasets['desc']['saveas'])
		for script in scriptsMap:
			if pid in script:
				scripts = Script()
				scripts = copy(scriptsMap[script])
				scripts = scripts.__dict__
				workflow.addScript(scripts['desc']['saveas'])
	if "POST" in type:
		listConn = str(workflowsave[2])
		headInfo = str(workflowsave[3])
		workflowMap[str(pid)] = listConn + "**" + headInfo
	print(workflow.__dict__)
	print(workflowMap)
	return jsonify({'workflow':workflow.__dict__})	
	
	
	
	
	
	
	
	
@app.route('/getDownload',methods=['POST'])
def getDownload():
	downloadsave = request.json
	pid = str(downloadsave[0])
	pathkey = 'Path'+str( pid)
	projkey = 'ProjectName'+str( pid)
	pKey = 'person'+str(pid)
	projectName = ""
	pathName = ""
	isPublic = True
	isYesorNo = str(downloadsave[2])
	if isYesorNo and not isYesorNo.isspace():
		if "Yes" in isYesorNo:
			isPublic = True
		else:
			isPublic = False

	globusId = "https://www.globus.org/app/transfer?origin_id=72277ed4-1ad3-11e7-bbe1-22000b9a448b&origin_path=%2Fjacs.6b00225%2F"
	curator = Person()
	info = Info()
	for keys in store:
		if pathkey in keys:
			pathName = store.get(pathkey)[2:len(str(store.get(pathkey)))-1]
		if projkey in keys:
			projectName = store.get(projkey)[2:len(str(store.get(projkey)))-1]
	for curate in personMap:
		if pKey in curate:
			curator = copy(personMap[pKey])
	project = Project(str(projectName),curator,isPublic,str(pathName),globusId)
	print("here")
	for infos in infoMap:
		if pid in infos:
			info = infoMap[infos].__dict__
			print(info)
			print(info['desc']['pi'])
			for p in info['desc']['pi']:
				pis = Person()
				pis.addFirstName(p['firstName'])
				if 'middleName' in p:
					pis.addMiddleName(p['middleName'])
				pis.addLastName(p['lastName'])
				project.addPI(pis)
			for coll in info['desc']['collections'].split(","):
				project.addCollection(coll)
			for tag in info['desc']['tags'].split(","):
				project.addTag(tag)
	
	for chart in chartMap:
		if pid in chart:
			charts = Chart("figure")
			charts = copy(chartMap[chart])
			project.addNode(charts)
			
	for tool in toolsMap:
		if pid in tool:
			tools = Tool("Experiment")
			tools = copy(toolsMap[tool])
			project.addNode(tools)
			
	for dataset in datasetsMap:
		if pid in dataset:
			datasets = Dataset()
			datasets = copy(datasetsMap[dataset])
			project.addNode(datasets)
	
	for script in scriptsMap:
		if pid in script:
			scripts = Script()
			scripts = copy(scriptsMap[script])
			project.addNode(scripts)
	
	for reference in referenceMap:
		if pid in reference:
			references = Reference("article")
			references = copy(referenceMap[reference])
			project.addReference(references)
			
	for workflow in workflowMap:
		if pid in workflow:
			workflows = Workflows()
			works = workflowMap[pid]
			works = works.split("**")
			connect = works[0]
			heads = works[1]
			for conn in ast.literal_eval(connect):
				print("conn", conn)
				workflows.addEdge(conn)
				for nod in conn:
					workflows.addNode(nod)
			for head in ast.literal_eval(heads):
				headers = Head()
				hinfo = head.split("*")
				try:
					if hinfo[1] and not hinfo[1].isspace():
						headers.addReadme(hinfo[1])
				except IndexError:
					print("No readme")
				try:
					if hinfo[2] and not hinfo[2].isspace():
						headers.addURL(hinfo[2])
				except IndexError:	
					print("No Url")
				project.addNode(headers)
			project.addWorkflow(workflows)
	project.dumpJSON(dirname + "/desc.json")
	
	
	return jsonify({'project':project.__dict__})



########################
# Dump the JSON file ! #
########################


######################
# MongoDB operations #
######################

# pid = project.sendDescriptor(dirname + '/desc.json','mongodb.rcc.uchicago.edu','imedb_client','IMEdbClientPWD') # ip, username, password
#project.fetchDescriptor( pid,'mongodb.rcc.uchicago.edu','imedb_client','IMEdbClientPWD')

if __name__=="__main__":
	app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
	CORS(app)
	app.run(debug=True,threaded=True)
