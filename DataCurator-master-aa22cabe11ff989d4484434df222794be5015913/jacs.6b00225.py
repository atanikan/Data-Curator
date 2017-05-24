from flask_api import FlaskAPI
import redis
from flask.json import JSONEncoder
from flask import request,jsonify,session,render_template
import time
import paramiko 
from flask_cors import CORS
from json import dumps as jsonstring
from src.DataCurator import *
import os
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from simplekv import TimeToLiveMixin

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



if not os.path.exists(dirname):
   os.makedirs(dirname)

#################
# Define People #
#################
pid = ""
@app.route('/',methods = ['GET'])
def newUser():
	global pid
	pid = pid + 1
	print("here")
	return jsonify({'pid':pid})
	
	
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
	return jsonify({'pdetails':person.__dict__})	
	
@app.route('/getServerDetails',methods=['POST'])
def getServerDetails():
	serverDetails = request.json
	server = Server()
	ServerName = ""
	UserName = ""
	Password = ""
	Path = ""
	serverkey = 'ServerName'+str( pid)
	userkey = 'UserName'+str( pid)
	passkey = 'Password'+str( pid)
	pathkey = 'Path'+str( pid)
	if("GET" in serverDetails[0]):
		print(serverDetails)
		if serverkey in store and store.get(serverkey) is not None:
			ServerName = str(store.get(serverkey))[2:len(str(store.get(serverkey)))-1]
		if userkey in store and store.get(userkey) is not None:
			UserName = str(store.get(userkey))[2:len(str(store.get(userkey)))-1]
		if passkey in store and store.get(passkey) is not None:
			print("here1")
			Password = str(store.get(passkey))[2:len(str(store.get(passkey)))-1]
		if pathkey in store and store.get(pathkey) is not None:
			print("here1")
			Path = str(store.get(pathkey))[2:len(str(store.get(pathkey)))-1]
	else:
		ServerName = str(serverDetails[1])
		UserName = str(serverDetails[2])
		Password = str(serverDetails[3])
		Path = str(serverDetails[4])
	if(ServerName is not None):
		server.addServerName(str(ServerName))
		store.put(serverkey, ServerName, ttl_secs=14400)
	if(UserName is not None):
		server.addUsername(str(UserName))
		store.put(userkey,UserName, ttl_secs=14400)
	if(Password is not None):
		server.addPassword(str(Password))
		store.put(passkey,Password, ttl_secs=14400)
	if(Path is not None):
		server.addPath(str(Path))
		store.put(pathkey,Path, ttl_secs=14400)
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
	
@app.route('/getTreeInfo',methods=['POST'])
def getTreeInfo():
	if(request is not None):
		pathDetails = request.json
	print("here")
	ssh = paramiko.SSHClient()
	# automatically add keys without requiring human intervention
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	serverkey = 'ServerName'+str( pid)
	userkey = 'UserName'+str( pid)
	passkey = 'Password'+str( pid)
	pathkey = 'Path'+str( pid)
	content_hostName = str(store.get(serverkey))[2:len(str(store.get(serverkey)))-1]
	content_path = ''
	if(pathDetails is not None):
		if(len(pathDetails) > 0):
			content_path = str(pathDetails[0])
		else:
			content_path= str(store.get(pathkey))[2:len(str(store.get(pathkey)))-1]
	print(content_path)
	content_username = str(store.get(userkey))[2:len(str(store.get(userkey)))-1]
	content_password = str(store.get(passkey))[2:len(str(store.get(passkey)))-1]
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
	type = str(projectPath[0])
	path = ""
	pathkey = 'Path'+str( pid)
	projkey = 'ProjectName'+str( pid)
	if("GET" in type):
		path = str(store.get(pathkey))[2:len(str(store.get(pathkey)))-1]
	else:
		store.put(pathkey,str(projectPath[1]), ttl_secs=14400)
		path = str(projectPath[1])
	parent = path.split("/")
	parentName = parent[len(parent)-1]
	print("here")
	print(parentName)
	projPath.projectName = parentName
	projPath.Path = path
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
	type = iDetails[0]
	infosaveas = iDetails[1]
	print(iDetails)
	if "INIT" in type:
		for key in infoMap:
			if str(key).split('*')[0] not in infoList:
				infoList.append(str(key).split('*')[0])
	if "GET" in type:
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
		for fname in eval(str(iDetails[2])):
			pifnamelist.append(str(fname))
		for mname in eval(str(iDetails[3])):
			if "N/A" in mname: 
				pimnamelist.append("")
			else:
				pimnamelist.append(mname)
		for lname in eval(str(iDetails[4])):
			pilnamelist.append(str(lname))
		collections = str(iDetails[5])
		tags = str(iDetails[6])
		mainnotebookfile = str(iDetails[7])
		globusid = str(iDetails[8])
		for lab in list(iDetails[9]):
			if "N/A" not in lab:
				infolabels.append(str(lab))
		for val in list(iDetails[10]):
			if "N/A" not in val:
				infovalues.append(str(val))
	if "INIT" not in type:
		if len(pifnamelist)>0 and len(pimnamelist)>0 and len(pilnamelist)>0:
			info.addPiFirstName(pifnamelist)
			info.addPiMiddleName(pimnamelist)
			info.addPiLastName(pilnamelist)
			store.put(str('pifname'+infosaveas+str( pid)), pifnamelist, ttl_secs=14400)
			store.put(str('pimname'+infosaveas+str( pid)), pimnamelist, ttl_secs=14400)
			store.put(str('pilname'+infosaveas+str( pid)), pilnamelist, ttl_secs=14400)
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
			#session['pfirstName'] = fname
			if str('globusid'+infosaveas+str( pid)) not in store:
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
		print(info)
		print(infoList)
	return jsonify({'infoDetails':info.__dict__,'infoList':infoList})
	
@app.route('/delInfo',methods=['POST'])
def delInfo():
	delsave = request.json
	infosaveas = str(delsave[0])
	if infosaveas +"*"+ str(pid) in infoMap:
		del infoMap[str(infosaveas) + str(pid)]
	if str('pifname'+infosaveas+str( pid)) in store:
		store.delete('pifname'+infosaveas+str( pid))
	if str('pimname'+infosaveas+str( pid)) in store:
		store.delete('pimname'+infosaveas+str( pid))
	if str('pilname'+infosaveas+str( pid)) in store:
		store.delete('pilname'+infosaveas+str( pid))
	if str('collections'+infosaveas+str( pid)) in store:
		store.delete('collections'+infosaveas+str( pid))
	if str('tags'+infosaveas+str( pid)) in store:
		store.delete('tags'+infosaveas+str( pid))
	if str('mainnotebookfile'+infosaveas+str( pid)) in store:
		store.delete('mainnotebookfile'+infosaveas+str( pid))
	if str('globusid'+infosaveas+str( pid)) in store:
		store.delete('globusid'+infosaveas+str( pid))
	if str('infolabels'+infosaveas+str( pid)) in store:
		store.delete('infolabels'+infosaveas+str( pid))
	if str('infovalues'+infosaveas+str( pid)) in store:
		store.delete('infovalues'+infosaveas+str( pid))
	return jsonify({'infodetails':infosaveas})

@app.route('/getCharts',methods=['POST'])
def getCharts():
	cDetails = request.json
	chart = Chart("figure")
	type = str(cDetails[0])
	csaveas = str(cDetails[1])
	if("N/A" not in str(cDetails[1])):
		chart.addSaveAs(csaveas)
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
		if "chartsaveaslist" in store:
			print(store.get('chartsaveaslist'))
			print(">>",str(store.get('chartsaveaslist'))[2:len(str(store.get('chartsaveaslist')))-1])
			for key in eval(str(store.get('chartsaveaslist'))[2:len(str(store.get('chartsaveaslist')))-1]):
				print(key)
				#print(str(key)[1:len(str(key))-1])
				chartsList.append(key)
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
		radioVal = str(cDetails[2])
		caption = str(cDetails[3])
		number = str(cDetails[4])
		cfiles = str(cDetails[5])
		cimagefiles = str(cDetails[6])
		cnotebookfiles = str(cDetails[7])
		cproperties = str(cDetails[8])
		if "N/A" not in str(cDetails[9]):
			clabels.append(str(cDetails[9]))
		if "N/A" not in str(cDetails[10]):
			cvalues.append(str(cDetails[10]))
	if "POST" in type or "GET" in type:
		print("why not")
		if radioVal and not radioVal.isspace():
			print("here>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			chart.addKind(radioVal)
			#session['pfirstName'] = fname
			if str('radioVal'+csaveas+str( pid)) not in store:
				store.put(str('radioVal'+csaveas+str( pid)), radioVal, ttl_secs=14400)
		if caption and not caption.isspace():
			print("here2>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			chart.addCaption(caption)
			#session['pfirstName'] = fname
			if str('caption'+csaveas+str( pid)) not in store:
				store.put(str('caption'+csaveas+str( pid)), caption, ttl_secs=14400)
		if number and not number.isspace():
			chart.addNumber(number)
			#session['pfirstName'] = fname
			if str('number'+csaveas+str( pid)) not in store:
				store.put(str('number'+csaveas+str( pid)), number, ttl_secs=14400)
				
		if cfiles and not cfiles.isspace():
			chart.addFile(cfiles)
			#session['pfirstName'] = fname
			if str('cfiles'+csaveas+str( pid)) not in store:
				store.put(str('cfiles'+csaveas+str( pid)), cfiles, ttl_secs=14400)
				
		if cimagefiles and not cimagefiles.isspace():
			chart.addImageFile(cimagefiles)
			#session['pfirstName'] = fname
			if str('cimagefiles'+csaveas+str( pid)) not in store:
				store.put(str('cimagefiles'+csaveas+str( pid)), cimagefiles, ttl_secs=14400)
				
		if cnotebookfiles and not cnotebookfiles.isspace():
			chart.addNotebookFile(cnotebookfiles)
			#session['pfirstName'] = fname
			if str('cnotebookfiles'+csaveas+str( pid)) not in store:
				store.put(str('cnotebookfiles'+csaveas+str( pid)), cnotebookfiles, ttl_secs=14400)
				
		if cproperties and not cproperties.isspace():
			chart.addProperty(cproperties)
			#session['pfirstName'] = fname
			if str('cproperties'+csaveas+str( pid)) not in store:
				store.put(str('cproperties'+csaveas+str(pid)), cproperties, ttl_secs=14400)
		if len(clabels)>0 and len(cvalues)>0:
			for f, b in zip(clabels, cvalues):
				chart.addExtra(f,b)
				store.put(str('clabels'+csaveas+str(pid)), clabels, ttl_secs=14400)
				store.put(str('cvalues'+csaveas+str(pid)), cvalues, ttl_secs=14400)
		if "N/A" not in csaveas:
			chartMap[str(csaveas)] = chart
			chartsaveaslist.append(str(csaveas))
			store.put("chartsaveaslist",chartsaveaslist, ttl_secs=14400)
	print(chart.__dict__)
	return jsonify({'cdetails':chart.__dict__,'chartList':chartsList})
	

@app.route('/delCharts',methods=['POST'])
def delCharts():
	delsave = request.json
	csaveas = str(delsave[0])
	if csaveas in chartMap:
		del chartMap[str(csaveas)]
	if str('radioVal'+csaveas+str( pid)) in store:
		store.delete('radioVal'+csaveas+str( pid))
	if str('caption'+csaveas+str( pid)) in store:
		store.delete('caption'+csaveas+str( pid))
	if str('number'+csaveas+str( pid)) in store:
		store.delete('number'+csaveas+str( pid))
	if str('cfiles'+csaveas+str( pid)) in store:
		store.delete('cfiles'+csaveas+str( pid))
	if str('cimagefiles'+csaveas+str( pid)) in store:
		store.delete('cimagefiles'+csaveas+str( pid))
	if str('cnotebookfiles'+csaveas+str( pid)) in store:
		store.delete('cnotebookfiles'+csaveas+str( pid))
	if str('cproperties'+csaveas+str( pid)) in store:
		store.delete('cproperties'+csaveas+str( pid))
	return jsonify({'delcdetails':csaveas})
	
@app.route('/getTools',methods=['POST'])
def getTools():
	toolsDetails = request.json
	tools = Tools()
	type = str(toolsDetails[0])
	toolssaveas = str(toolsDetails[1])
	if("N/A" not in str(toolsDetails[1])):
		tools.addSaveAs(toolssaveas)
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
	print(toolsDetails)
	if "INIT" in type:
		if "toolssaveaslist" in store:
			print(store.get('toolssaveaslist'))
			print(">>",str(store.get('toolssaveaslist'))[2:len(str(store.get('toolssaveaslist')))-1])
			for key in eval(str(store.get('toolssaveaslist'))[3:len(str(store.get('toolssaveaslist')))-2]):
				print(key)
				#print(str(key)[1:len(str(key))-1])
				toolsList.append(key)
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
		kind = str(toolsDetails[2])
		if "Software" in kind:
			packagename = str(toolsDetails[3])
			programname = str(toolsDetails[4])
			version = str(toolsDetails[5])
			toolsurls = str(toolsDetails[6])
			if "N/A" not in str(toolsDetails[7]):
				toolslabels.append(str(toolsDetails[7]))
			if "N/A" not in str(toolsDetails[8]):
				toolsvalues.append(str(toolsDetails[8]))
		else:
			facilityname = str(toolsDetails[2])
			measurement = str(toolsDetails[3])
			toolseurls = str(toolsDetails[4])
			if "N/A" not in str(toolsDetails[5]):
				toolslabels.append(str(toolsDetails[5]))
			if "N/A" not in str(toolsDetails[6]):
				toolsvalues.append(str(toolsDetails[6]))
	if "POST" in type or "GET" in type:
		tools = Tool(str(kind))
		if kind and not kind.isspace():
			#session['pfirstName'] = fname
			if str('kind'+toolssaveas+str( pid)) not in store:
				store.put(str('kind'+toolssaveas+str( pid)), kind, ttl_secs=14400)
		if "Software" in kind:
			if packagename and not packagename.isspace():
				tools.addPackageName(packagename)
				if str('packagename'+toolssaveas+str( pid)) not in store:
					store.put(str('packagename'+toolssaveas+str( pid)), packagename, ttl_secs=14400)
			if programname and not programname.isspace():
				tools.addProgramName(programname)
				if str('programname'+toolssaveas+str( pid)) not in store:
					store.put(str('programname'+toolssaveas+str( pid)), programname, ttl_secs=14400)
			if version and not version.isspace():
				tools.addVersion(version)
				#session['pfirstName'] = fname
				if str('version'+toolssaveas+str( pid)) not in store:
					store.put(str('version'+toolssaveas+str( pid)), version, ttl_secs=14400)
			if toolsurls and not toolsurls.isspace() and "N/A" not in toolsurls:
				tools.addURL(toolsurls)
				#session['pfirstName'] = fname
				if str('toolsurls'+toolssaveas+str( pid)) not in store:
					store.put(str('toolsurls'+toolssaveas+str( pid)), toolsurls, ttl_secs=14400)
			if len(toolslabels)>0 and len(toolsvalues)>0:
				for f, b in zip(toolslabels, toolsvalues):
					tools.addExtra(f,b)
					store.put(str('toolslabels'+toolssaveas+str(pid)), clabels, ttl_secs=14400)
					store.put(str('toolsvalues'+toolssaveas+str(pid)), cvalues, ttl_secs=14400)
		else:
			if facilityname and not facilityname.isspace():
				tools.addFacilityName(facilityname)
				if str('facilityname'+toolssaveas+str( pid)) not in store:
					store.put(str('facilityname'+toolssaveas+str( pid)), facilityname, ttl_secs=14400)
					
			if measurement and not measurement.isspace():
				tools.addMeasurement(measurement)
				#session['pfirstName'] = fname
				if str('measurement'+toolssaveas+str( pid)) not in store:
					store.put(str('measurement'+toolssaveas+str( pid)), measurement, ttl_secs=14400)
					
			if toolseurls and not toolseurls.isspace():
				tools.addExpURL(toolseurls)
				#session['pfirstName'] = fname
				if str('toolseurls'+toolssaveas+str( pid)) not in store:
					store.put(str('toolseurls'+toolssaveas+str(pid)), toolseurls, ttl_secs=14400)
			if len(toolslabels)>0 and len(cvalues)>0:
				for f, b in zip(toolslabels, toolsvalues):
					tools.addExtra(f,b)
					store.put(str('toolslabels'+toolssaveas+str(pid)), toolslabels, ttl_secs=14400)
					store.put(str('toolsvalues'+toolssaveas+str(pid)), toolsvalues, ttl_secs=14400)
		if "N/A" not in toolssaveas:
			chartMap[str(toolssaveas)] = chart
			chartsaveaslist.append(str(toolssaveas))
			store.put("chartsaveaslist",chartsaveaslist, ttl_secs=14400)
	print(chart.__dict__)
	return jsonify({'toolsdetails':chart.__dict__,'chartList':chartsList})
	

@app.route('/delTools',methods=['POST'])
def delTools():
	delsave = request.json
	toolssaveas = str(delsave[0])
	if toolssaveas in chartMap:
		del chartMap[str(toolssaveas)]
	if str('radioVal'+toolssaveas+str( pid)) in store:
		store.delete('radioVal'+toolssaveas+str( pid))
	if str('caption'+toolssaveas+str( pid)) in store:
		store.delete('caption'+toolssaveas+str( pid))
	if str('number'+toolssaveas+str( pid)) in store:
		store.delete('number'+toolssaveas+str( pid))
	if str('cfiles'+toolssaveas+str( pid)) in store:
		store.delete('cfiles'+toolssaveas+str( pid))
	if str('cimagefiles'+toolssaveas+str( pid)) in store:
		store.delete('cimagefiles'+toolssaveas+str( pid))
	if str('cnotebookfiles'+toolssaveas+str( pid)) in store:
		store.delete('cnotebookfiles'+toolssaveas+str( pid))
	if str('cproperties'+toolssaveas+str( pid)) in store:
		store.delete('cproperties'+toolssaveas+str( pid))
	return jsonify({'deltoolsDetails':toolssaveas})
	
	
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
	type = datasetdetails[0]
	datasetsaveas = datasetdetails[1]
	print(datasetdetails)
	if "INIT" in type:
		for key in datasetsMap:
			if str(key).split('*')[0] not in datasetList:
				datasetList.append(str(key).split('*')[0])
	if "GET" in type:
		if str('datasetfiles'+datasetsaveas+str( pid)) in store and store.get(str('datasetfiles'+datasetsaveas+str( pid))) is not None:
			datasetfiles = str(store.get(str('datasetfiles'+datasetsaveas+str( pid))))[2:len(str(store.get(str('datasetfiles'+datasetsaveas+str( pid)))))-1]
		if str('datasetdescriptions'+datasetsaveas+str( pid)) in store and store.get(str('datasetdescriptions'+datasetsaveas+str( pid))) is not None:
			datasetdescriptions = str(store.get(str('datasetdescriptions'+datasetsaveas+str( pid))))[2:len(str(store.get(str('datasetdescriptions'+datasetsaveas+str( pid)))))-1]
		if str('dataseturls'+datasetsaveas+str( pid)) in store and store.get(str('dataseturls'+datasetsaveas+str( pid))) is not None:
			dataseturls = str(store.get(str('dataseturls'+datasetsaveas+str( pid))))[2:len(str(store.get(str('dataseturls'+datasetsaveas+str( pid)))))-1]
		if str('globusid'+datasetsaveas+str( pid)) in store and store.get(str('globusid'+datasetsaveas+str( pid))) is not None:
			globusid = str(store.get(str('globusid'+datasetsaveas+str( pid))))[2:len(str(store.get(str('globusid'+datasetsaveas+str( pid)))))-1]
		if str('datasetlabel'+datasetsaveas+str( pid)) in store and store.get(str('datasetlabel'+datasetsaveas+str( pid))) is not None:
			datasetlabel.append(str(store.get(str('datasetlabel'+datasetsaveas+str( pid))))[2:len(str(store.get(str('datasetlabel'+datasetsaveas+str( pid)))))-1])
		if str('datasetval'+datasetsaveas+str( pid)) in store and store.get(str('datasetval'+datasetsaveas+str( pid))) is not None:
			datasetval.append(str(store.get(str('datasetval'+datasetsaveas+str( pid))))[2:len(str(store.get(str('datasetval'+datasetsaveas+str( pid)))))-1])
	if "POST" in type:
		datasetfiles = str(iDetails[5])
		datasetdescriptions = str(iDetails[6])
		dataseturls = str(iDetails[7])
		globusid = str(iDetails[8])
		for lab in list(iDetails[9]):
			if "N/A" not in lab:
				datasetlabel.append(str(lab))
		for val in list(iDetails[10]):
			if "N/A" not in val:
				datasetval.append(str(val))
	if "INIT" not in type:
		if len(pifnamelist)>0 and len(pimnamelist)>0 and len(pilnamelist)>0:
			info.addPiFirstName(pifnamelist)
			info.addPiMiddleName(pimnamelist)
			info.addPiLastName(pilnamelist)
			store.put(str('pifname'+datasetsaveas+str( pid)), pifnamelist, ttl_secs=14400)
			store.put(str('pimname'+datasetsaveas+str( pid)), pimnamelist, ttl_secs=14400)
			store.put(str('pilname'+datasetsaveas+str( pid)), pilnamelist, ttl_secs=14400)
		if datasetfiles and not datasetfiles.isspace():
			info.addCollection(datasetfiles)
			#session['pfirstName'] = fname
			store.put(str('datasetfiles'+datasetsaveas+str( pid)), datasetfiles, ttl_secs=14400)
		if datasetdescriptions and not datasetdescriptions.isspace():
			info.addTag(datasetdescriptions)
			#session['pfirstName'] = fname
			store.put(str('datasetdescriptions'+datasetsaveas+str( pid)), datasetdescriptions, ttl_secs=14400)
				
		if dataseturls and not dataseturls.isspace():
			if "N/A" not in dataseturls:
				info.addNotebookFile(dataseturls)
				store.put(str('dataseturls'+datasetsaveas+str( pid)), dataseturls, ttl_secs=14400)
				
		if globusid and not globusid.isspace():
			info.addGlobusId(globusid)
			#session['pfirstName'] = fname
			if str('globusid'+datasetsaveas+str( pid)) not in store:
				store.put(str('globusid'+datasetsaveas+str( pid)), globusid, ttl_secs=14400)

		if len(datasetlabel)>0 and len(datasetval)>0:
			for f, b in zip(datasetlabel, datasetval):
				if "N/A" not in f and "N/A" not in b:
					info.addExtra(f,b)
					store.put(str('datasetlabel'+datasetsaveas+str(pid)), datasetlabel, ttl_secs=14400)
					store.put(str('datasetval'+datasetsaveas+str(pid)), datasetval, ttl_secs=14400)
		if "N/A" not in datasetsaveas:
			infoMap[str(datasetsaveas) +"*"+str(pid)] = info
			infoList.append(str(datasetsaveas))
			info.addSaveAs(datasetsaveas)
		print(info)
		print(infoList)
	return jsonify({'infoDetails':info.__dict__,'infoList':infoList})
	
@app.route('/delInfo',methods=['POST'])
def delInfo():
	delsave = request.json
	datasetsaveas = str(delsave[0])
	if datasetsaveas +"*"+ str(pid) in infoMap:
		del infoMap[str(datasetsaveas) + str(pid)]
	if str('pifname'+datasetsaveas+str( pid)) in store:
		store.delete('pifname'+datasetsaveas+str( pid))
	if str('pimname'+datasetsaveas+str( pid)) in store:
		store.delete('pimname'+datasetsaveas+str( pid))
	if str('pilname'+datasetsaveas+str( pid)) in store:
		store.delete('pilname'+datasetsaveas+str( pid))
	if str('datasetfiles'+datasetsaveas+str( pid)) in store:
		store.delete('datasetfiles'+datasetsaveas+str( pid))
	if str('datasetdescriptions'+datasetsaveas+str( pid)) in store:
		store.delete('datasetdescriptions'+datasetsaveas+str( pid))
	if str('dataseturls'+datasetsaveas+str( pid)) in store:
		store.delete('dataseturls'+datasetsaveas+str( pid))
	if str('globusid'+datasetsaveas+str( pid)) in store:
		store.delete('globusid'+datasetsaveas+str( pid))
	if str('datasetlabel'+datasetsaveas+str( pid)) in store:
		store.delete('datasetlabel'+datasetsaveas+str( pid))
	if str('datasetval'+datasetsaveas+str( pid)) in store:
		store.delete('datasetval'+datasetsaveas+str( pid))
	return jsonify({'infodetails':datasetsaveas})

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
ref.addDOI("14400.1021/jacs.6b00225") 
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

# pid = project.sendDescriptor(dirname + '/desc.json','mongodb.rcc.uchicago.edu','imedb_client','IMEdbClientPWD') # ip, username, password
#project.fetchDescriptor( pid,'mongodb.rcc.uchicago.edu','imedb_client','IMEdbClientPWD')

if __name__=="__main__":
	app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
	CORS(app)
	app.run(debug=True)
