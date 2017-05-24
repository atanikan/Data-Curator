from __future__ import print_function
from datetime import datetime, date, time
from dateutil import parser
import json
import sys
### MongoDB
#from pymongo import MongoClient
### Authentication 
import ssl
### Graph 
import networkx as nx
import matplotlib.pyplot as plt

##############
# Descriptor #
##############

class Descriptor(object) :
    #
    # constructor
    #
    def __init__(self, mandatoryFields = [], optionalFields = [] ):
       #
       self.desc = {} # dictionary of descriptors
       self.mandatoryFields = [] # list of mandatory fields
       self.optionalFields = [] # list of optional fields
       #
       # check that mandatory fields are strings, then stash them
       #
       for field in mandatoryFields :
          if( isinstance(field, str) ) :
             self.mandatoryFields.append(field)
          else :
             print("Cannot add field, you must provide mandatoryFields as list of strings.")
       #
       # check that optional fields are strings, then stash them
       #
       for field in optionalFields :
          if( isinstance(field, str) ) :
             self.optionalFields.append(field)
          else :
             print("Cannot add field, you must provide optionalFields as list of strings.")
    #
    # showFields
    #
    def showFields(self):
       #
       print("List of Fields")
       for field in self.mandatoryFields :
          print("MandatoryField :", field)
       for field in self.optionalFields :
          print("OptionalField :", field)
    #
    # showContent
    #
    def showContent(self):
       #
       print("Content: [x] Inserted, [-] Missing, [ ] Optional")
       for field in self.mandatoryFields :
          if( field in self.desc ) :
             print("[x]", field, ":", self.desc[field])
          else :
             print("[-]", field, ":")
       for field in self.optionalFields :
          if( field in self.desc ) :
             print("[x]", field, ":", self.desc[field])
          else :
             print("[ ]", field, ":")
       if( self.isValid(False) ) :
          print("Valid... YES!")
       else :
          print("Valid... NO!")
    #
    # validator
    #
    def isValid(self, verbose = True ):
       #
       missingMandatoryFields = self.__getMissingMandatoryFields()
       notMatchingMandatoryOrOptionalFields = self.__getNotMatchingMandatoryOrOptionalFields()
       #
       isValid = ( len(missingMandatoryFields)==0 and len(notMatchingMandatoryOrOptionalFields)==0 )
       #
       if( ( not isValid ) and verbose ) :
          for field in missingMandatoryFields :
             print("Missing mandatory field: ", field)
          for field in notMatchingMandatoryOrOptionalFields :
             print("Not matching mandatory or optional field: ", field)
          print("Cannot validate the descriptor")
       #
       return isValid
    #
    # getMissingMandatoryFields
    #
    def __getMissingMandatoryFields(self):
       #
       missingMandatoryFields = [] # list of missing mandatory fields
       #
       for field in self.mandatoryFields :
           if ( not field in self.desc ) :
              missingMandatoryFields.append( field )
       #
       return missingMandatoryFields
    #
    # getNotMatchingMandatoryOrOptionalFields
    #
    def __getNotMatchingMandatoryOrOptionalFields(self):
       #
       notMatchingMandatoryOrOptionalFields = [] # list of missing mandatory fields
       #
       for field in self.desc :
           if ( not any( [field in self.mandatoryFields, field in self.optionalFields] ) ) :
              notMatchingMandatoryOrOptionalFields.append( field )
       #
       return notMatchingMandatoryOrOptionalFields
    #
    # dump Json
    #
    def dumpJSON(self, filename) :
       if( self.isValid() ) :
          with open(filename,"w") as outfile:
             json.dump(self.desc,outfile,default=lambda o: o.__dict__, separators=(',',':'), sort_keys=True,indent=3)
          print('CONGRATS! Generated correctly file:',filename)
       else :
          print("JSON could not be returned. Fields are missing or not matching.")
    #
    # return Json
    #
    def returnJSON(self) :
       if( self.isValid() ) :
          return json.dumps( self.desc, default=lambda o: o.__dict__, separators=(',',':'), sort_keys=True,indent=3)
       else :
          print("JSON could not be returned. Fields are missing or not matching.")
          return {}
    #
    # getDesc
    #
    def getDesc(self) :
       if( self.isValid() ) :
          return self.desc
       else :
          print("Data could not be returned. Fields are missing or not matching.")
          return {}
    #
    # add Tag
    #
    def addTag(self, tag) :
       if not "tags" in self.desc :
          self.desc["tags"] = []
       if( isinstance(tag, str) ) :
          self.desc["tags"].append( tag )
       else :
          print("Cannot add tag, you must provide tag as string.")

##########
# Person #
##########

class Person(Descriptor) :
    #
    # constructor
    #
    def __init__(self):
       #
       Descriptor.__init__(self,["firstName","lastName"],["middleName","tags"])
    #
    # add firstName
    #
    def addFirstName(self, firstName) :
       if( isinstance(firstName, str) ) :
          self.desc["firstName"] = firstName
       else :
          print("Cannot add firstName, you must provide firstName as strings.")
    #
    # add lastName
    #
    def addLastName(self, lastName) :
       if( isinstance(lastName, str) ) :
          self.desc["lastName"] = lastName
       else :
          print("Cannot add lastName, you must provide lastName as strings.")
    #
    # add middleName
    #
    def addMiddleName(self, middleName) :
       if( isinstance(middleName, str) ) :
          self.desc["middleName"] = middleName
       else :
          print("Cannot add middleName, you must provide middleName strings.")
    #
    # add Tag
    #
    def addTag(self, tag) :
       Descriptor.addTag(self,tag)
	 
	 
	 
##########
# Server #
##########

class Server(Descriptor) :
    #
    # constructor
    #
    def __init__(self):
       #
       Descriptor.__init__(self,["serverName","Username","Password","Path"],[])
    #
    # add firstName
    #
    def addServerName(self, serverName) :
       if( isinstance(serverName, str) ) :
          self.desc["serverName"] = serverName
       else :
          print("Cannot add Servername, you must provide firstName as strings.")
    #
    # add lastName
    #
    def addUsername(self, Username) :
       if( isinstance(Username, str) ) :
          self.desc["Username"] = Username
       else :
          print("Cannot add Username, you must provide lastName as strings.")
    #
    # add middleName
    #
    def addPassword(self, Password) :
       if( isinstance(Password, str) ) :
          self.desc["Password"] = Password
       else :
          print("Cannot add Password, you must provide Password strings.")
		  
	#
    # add middleName
    #
    def addPath(self, Path) :
       if( isinstance(Path, str) ) :
          self.desc["Path"] = Path
       else :
          print("Cannot add Path, you must provide Password strings.")
    #
    # add Tag
    #
    def addTag(self, tag) :
       Descriptor.addTag(self,tag)

########
# Tool #
########

class Tool(Descriptor) :
    #
    # constructor
    #
    def __init__(self,kind = "software"):
       #
       if( isinstance(kind, str) ) :
          if( not kind in ["experiment","software"] ) :
             print("Cannot create an instance of Reference, you must provide kind : experiment, software.")
          if( kind in ["experiment"] ) :
             Descriptor.__init__(self,["kind","facilityName","measurement"],["URLs","tags","extras"])
             self.desc["kind"] = kind
          if( kind in ["software"] ) :
             Descriptor.__init__(self,["kind","packageName","programName","version"],["URLs","tags","extras"])
             self.desc["kind"] = kind
       else :
          print("Cannot create an instance of Tool, you must provide kind as string.")
    #
    # add facilityName
    #
    def addFacilityName(self, facilityName) :
       if( isinstance(facilityName, str) ) :
          self.desc["facilityName"] = facilityName
       else :
          print("Cannot add facilityName, you must provide facilityName as strings.")
	#
    # add measurement
    #
    def addMeasurement(self, measurement) :
       if( isinstance(measurement, str) ) :
          self.desc["measurement"] = measurement
       else :
          print("Cannot add measurement, you must provide measurement as strings.")
	#
    # add packageName
    #
    def addPackageName(self, packageName) :
       if( isinstance(packageName, str) ) :
          self.desc["packageName"] = packageName
       else :
          print("Cannot add packageName, you must provide packageName as strings.")
    #
    # add programName
    #
    def addProgramName(self, programName) :
       if( isinstance(programName, str) ) :
          self.desc["programName"] = programName
       else :
          print("Cannot add programName, you must provide programName as strings.")
    #
    # add version
    #
    def addVersion(self, version) :
       if( isinstance(version, str) ) :
          self.desc["version"] = version
       else :
          print("Cannot add version, you must provide version as strings.")
    #
    # add URL
    #
    def addURL(self, url) :
       if not "URLs" in self.desc :
          self.desc["URLs"] = []
       self.desc["URLs"].append( url )
	
	#
    # add URL
    #
    def addExpURL(self, url) :
       if not "ExpURLs" in self.desc :
          self.desc["ExpURLs"] = []
       self.desc["ExpURLs"].append( url )
    #
    # add Tag
    #
    def addTag(self, tag) :
       Descriptor.addTag(self,tag)
	   
	#
    # add Saveas
    #
    def addSaveAs(self, saveas) :
       self.desc["saveas"] = saveas
    #
    # add Extra
    #
    def addExtra(self, field, value ) :
       if not "extras" in self.desc :
          self.desc["extras"] = {}
       if( isinstance(field, str) and isinstance(value, str) ) :
          if not field in self.desc["extras"] :
             self.desc["extras"][field] = []
          self.desc["extras"][field].append( value )
       else :
          print("Cannot add field and value, you must provide field and value as string.")

#############
# Reference #
#############

class Reference(Descriptor) :
    #
    # constructor
    #
    def __init__(self,kind = "article"):
       #
       if( isinstance(kind, str) ) :
          if( not kind in ["article"] ) :
             print("Cannot create an instance of Reference, you must provide kind : article.")
          if( kind in ["article"] ) :
             Descriptor.__init__(self,["kind","DOI","title","authors","journal","page","volume","year"],["URLs","publishedAbstract","receivedDate","publishedDate","tags","extras"])
             self.desc["kind"] = kind
       else :
          print("Cannot create an instance of Reference, you must provide kind as string.")
	#
    # add DOI
    #
    def addDOI(self, doi) :
       if( isinstance(doi, str) ) :
          self.desc["DOI"] = doi
       else :
          print("Cannot add DOI, you must provide doi as string.")
	#
    # add title
    #
    def addTitle(self, title) :
       if( isinstance(title, str) ) :
          self.desc["title"] = title
       else :
          print("Cannot add title, you must provide title as string.")
    #
    # add abstract
    #
    def addPublishedAbstract(self, abstract) :
       if( isinstance(abstract, str) ) :
          self.desc["publishedAbstract"] = abstract
       else :
          print("Cannot add abstract, you must provide abstract as string.")
	#
    # add author
    #
    def addAuthor(self, person) :
       if not "authors" in self.desc :
          self.desc["authors"] = []
       if( isinstance(person, Person) ) :
          if( person.isValid() ) :
             self.desc["authors"].append( person.getDesc() )
          else :
             print("Cannot add person, person is not valid.")
       else :
          print("Cannot add author, you must provide person as Person.")
    #
    # add journal
    #
    def addJournal(self, journalFull, journalAbbrev) :
       if( isinstance(journalFull, str) and isinstance(journalAbbrev, str) ) :
          self.desc["journal"] = { "fullName" : journalFull, "abbrevName" : journalAbbrev }
       else :
          print("Cannot add journal, you must provide journalFull and journalAbbrev as strings.")
	#
    # add page
    #
    def addPage(self, page) :
       if( isinstance(page, str) ) :
          self.desc["page"] = page
       else :
          print("Cannot add page, you must provide page as string.")
    #
    # add volume
    #
    def addVolume(self, volume) :
       if( isinstance(volume, str) ) :
          self.desc["volume"] = volume
       else :
          print("Cannot add volume, you must provide volume as string.")
    #
    # add year
    #
    def addYear(self, year) :
       if( isinstance(year, int) ) :
          self.desc["year"] = year
       else :
          print("Cannot add year, you must provide year as integer.")
    #
    # add URL
    #
    def addURL(self, url) :
       if not "URLs" in self.desc :
          self.desc["URLs"] = []
       self.desc["URLs"].append( url )
    #
    # add received date
    #
    def addReceivedDate (self, receivedDate) :
        #self.desc["receivedDate"] = receivedDate.strftime('%Y-%m-%d %H:%M:%S')
       if( isinstance(receivedDate, str) ) :
         self.desc["receivedDate"] = str(parser.parse(receivedDate))
       else :
          print("Cannot add receivedDate, you must provide receivedDate as str.")
    #
    # add published date
    #
    def addPublishedDate(self, publishedDate) :
       # self.desc["publishedDate"] = publishedDate.strftime('%Y-%m-%d %H:%M:%S')
       if( isinstance(publishedDate, str) ) :
         self.desc["publishedDate"] = str(parser.parse(publishedDate))
       else :
          print("Cannot add publishedDate, you must provide publishedDate as str.")
    
	#
    # add Saveas
    #
    def addSaveAs(self, saveas) :
       self.desc["saveas"] = saveas
	
	
	#
    # add Tag
    #
    def addTag(self, tag) :
       Descriptor.addTag(self,tag)
    #
    # add Extra
    #
    def addExtra(self, field, value ) :
       if not "extras" in self.desc :
          self.desc["extras"] = {}
       if( isinstance(field, str) and isinstance(value, str) ) :
          if not field in self.desc["extras"] :
             self.desc["extras"][field] = []
          self.desc["extras"][field].append( value )
       else :
          print("Cannot add field and value, you must provide field and value as string.")

###########
# Dataset #
###########

class Dataset(Descriptor) :
    #
    # constructor
    #
    def __init__(self):
       Descriptor.__init__(self,["readme","files"],["URLs","tags","extras"])
    #
    # add readme
    #
    def addReadme(self, readme) :
       if( isinstance(readme, str) ) :
          self.desc["readme"] = readme
       else :
          print("Cannot add readme, you must provide readme as string.")
    #
    # add File
    #
    def addFile(self, File) :
       if not "files" in self.desc :
          self.desc["files"] = []
       if( isinstance(File, str) ) :
          self.desc["files"].append( File )
       else :
          print("Cannot add File, you must provide File as string.")
	#
    # add URL
    #
    def addURL(self, url) :
       if not "URLs" in self.desc :
          self.desc["URLs"] = []
       self.desc["URLs"].append( url )
    #
    # add Tag
    #
    def addTag(self, tag) :
       Descriptor.addTag(self,tag)
    
	
	#
    # add Saveas
    #
    def addSaveAs(self, saveas) :
       self.desc["saveas"] = saveas
	
	
	
	#
    # add Extra
    #
    def addExtra(self, field, value ) :
       if not "extras" in self.desc :
          self.desc["extras"] = {}
       if( isinstance(field, str) and isinstance(value, str) ) :
          if not field in self.desc["extras"] :
             self.desc["extras"][field] = []
          self.desc["extras"][field].append( value )
       else :
          print("Cannot add field and value, you must provide field and value as string.")

##########
# Script #
##########

class Script(Descriptor) :
    #
    # constructor
    #
    def __init__(self):
       Descriptor.__init__(self,["readme","files"],["URLs","tags","extras"])
    #
    # add readme
    #
    def addReadme(self, readme) :
       if( isinstance(readme, str) ) :
          self.desc["readme"] = readme
       else :
          print("Cannot add readme, you must provide readme as string.")
    #
    # add File
    #
    def addFile(self, File) :
       if not "files" in self.desc :
          self.desc["files"] = []
       if( isinstance(File, str) ) :
          self.desc["files"].append( File )
       else :
          print("Cannot add File, you must provide File as string.")
	#
    # add URL
    #
    def addURL(self, url) :
       if not "URLs" in self.desc :
          self.desc["URLs"] = []
       self.desc["URLs"].append( url )
    #
    # add Tag
    #
    def addTag(self, tag) :
       Descriptor.addTag(self,tag)
    
	#
    # add Saveas
    #
    def addSaveAs(self, saveas) :
       self.desc["saveas"] = saveas
	
	#
    # add Extra
    #
    def addExtra(self, field, value ) :
       if not "extras" in self.desc :
          self.desc["extras"] = {}
       if( isinstance(field, str) and isinstance(value, str) ) :
          if not field in self.desc["extras"] :
             self.desc["extras"][field] = []
          self.desc["extras"][field].append( value )
       else :
          print("Cannot add field and value, you must provide field and value as string.")
		  
		  
##########
# Info #
##########

class Info(Descriptor) :
    #
    # constructor
    #
    def __init__(self):
       Descriptor.__init__(self,["pifname","pilname","collections","tags"],["mainnotebookfile","extras"])
    #
    # add first Name for PI
    #
    def addPiFirstName(self, pifname) :
       if not "pifname" in self.desc :
          self.desc["pifname"] = []
          self.desc["pifname"].append( pifname )
       else :
          print("Cannot add pifname, you must provide pifname as string.")
	   
		  
	#
    # add Middle Name for PI
    #
    def addPiMiddleName(self, pimname) :
       if not "pimname" in self.desc :
          self.desc["pimname"] = []
          self.desc["pimname"].append( pimname )
       else :
          print("Cannot add pimname, you must provide pimname as string.")
	
	#
    # add Last Name for PI
    #
    def addPiLastName(self, pilname) :
       if not "pilname" in self.desc :
          self.desc["pilname"] = []
          self.desc["pilname"].append( pilname )
       else :
          print("Cannot add pilname, you must provide pilname as string.")
		  
		  
	
    #
    # add Collection
    #
    def addCollection(self, collection) :
       if not "collections" in self.desc :
          self.desc["collections"] = []
          self.desc["collections"].append( collection )
       else :
          sys.exit("Error: collection must be <str>.")
    
	#
    # add Collection
    #
    def addTag(self, tag) :
       Descriptor.addTag(self,tag)
	   
	#
    # add notebookFile
    #
    def addNotebookFile(self, notebookFile) :
       if ( isinstance(notebookFile,str)):
          self.desc["info"] =  notebookFile
       else :
          print("Cannot add notebookFile, you must provide notebookFile as string.")
		  
	#
    # add globus id
    #
    def addGlobusId(self, globusid) :
       if( isinstance(globusid, str) ) :
          self.desc["globusid"] = globusid
       else :
          print("Cannot add globus, you must provide globus as string.")
    
	#
    # add Saveas
    #
    def addSaveAs(self, saveas) :
       self.desc["saveas"] = saveas
	
	#
    # add Extra
    #
	#
    # add Collection
    #
    def addExtra(self, field, value) :
       if not "extrasfield" in self.desc :
          self.desc["extrasfield"] = []
          self.desc["extrasfield"].append( field )
       if not "extrasvalue" in self.desc :
          self.desc["extrasvalue"] = []
          self.desc["extrasvalue"].append( value )
    

########
# Head #
########

class Head(Descriptor) :
    #
    # constructor
    #
    def __init__(self):
       Descriptor.__init__(self,["readme"],["files","URLs","tags","extras"])
    #
    # add readme
    #
    def addReadme(self, readme) :
       if( isinstance(readme, str) ) :
          self.desc["readme"] = readme
       else :
          print("Cannot add readme, you must provide readme as string.")
    #
    # add File
    #
    def addFile(self, File) :
       if not "files" in self.desc :
          self.desc["files"] = []
       if( isinstance(File, str) ) :
          self.desc["files"].append( File )
       else :
          print("Cannot add File, you must provide File as string.")
	#
    # add URL
    #
    def addURL(self, url) :
       if not "URLs" in self.desc :
          self.desc["URLs"] = []
       self.desc["URLs"].append( url )
    #
    # add Tag
    #
    def addTag(self, tag) :
       Descriptor.addTag(self,tag)
    #
    # add Extra
    #
    def addExtra(self, field, value ) :
       if not "extras" in self.desc :
          self.desc["extras"] = {}
       if( isinstance(field, str) and isinstance(value, str) ) :
          if not field in self.desc["extras"] :
             self.desc["extras"][field] = []
          self.desc["extras"][field].append( value )
       else :
          print("Cannot add field and value, you must provide field and value as string.")

#########
# Chart #
#########

class Chart(Descriptor) :
    #
    # constructor
    #
    def __init__(self,kind):
       #
       if( isinstance(kind, str) ) :
          if( not kind in ["figure","table"] ) :
             print("Cannot create an instance of Chart, you must provide kind : figure or table.")
          if( kind in ["figure","table"] ) :
             Descriptor.__init__(self,["kind","number","caption","properties","files","notebookFile","imageFile"],["tags","extras"])
             self.desc["kind"] = kind
       else :
          print("Cannot create an instance of Chart, you must provide kind as string.")
    #
    # add number
    #
    def addNumber(self, number) :
       if( isinstance(number, str) ) :
          self.desc["number"] = number
       else :
          print("Cannot add number, you must provide number as string.")
    #
    # add caption
    #
    def addCaption(self, caption) :
       if( isinstance(caption, str) ) :
          self.desc["caption"] = caption
       else :
          print("Cannot add caption, you must provide caption as string.")
    #
    # add property
    #
    def addProperty(self, prop) :
       if not "properties" in self.desc :
          self.desc["properties"] = []
       if( isinstance(prop, str) ) :
          self.desc["properties"].append( prop )
       else :
          print("Cannot add property, you must provide property as string.")
    #
    # add files
    #
    def addFile(self, file) :
       if not "files" in self.desc :
          self.desc["files"] = []
       if( isinstance(file, str) ) :
          self.desc["files"].append( file )
       else :
          print("Cannot add file, you must provide file as string.")
    #
    # add notebookFile
    #
    def addNotebookFile(self, notebookFile) :
       if( isinstance(notebookFile, str) ) :
          self.desc["notebookFile"] = notebookFile
       else :
          print("Cannot add notebookFile, you must provide notebookFile as string.")
	#
    # add imageFile
    #
    def addImageFile(self, imageFile) :
       if( isinstance(imageFile, str) ) :
          self.desc["imageFile"] = imageFile
       else :
          print("Cannot add imageFile, you must provide imageFile as string.")
    #
    # add Tag
    #
    def addTag(self, tag) :
       Descriptor.addTag(self,tag)
	#
    # add Kind
    #
    def addKind(self, kind) :
       self.desc["kind"] = kind
	#
    # add Saveas
    #
    def addSaveAs(self, saveas) :
       self.desc["saveas"] = saveas
    #
    # add Extra
    #
    def addExtra(self, field, value ) :
       if not "extras" in self.desc :
          self.desc["extras"] = {}
       if( isinstance(field, str) and isinstance(value, str) ) :
          if not field in self.desc["extras"] :
             self.desc["extras"][field] = []
          self.desc["extras"][field].append( value )
       else :
          print("Cannot add field and value, you must provide field and value as string.")

###########
# Project #
###########

class Project(Descriptor) :
    #
    # constructor
    #
    def __init__(self,folder,creator,isPublic,serverPath,globusPath):
       #
       Descriptor.__init__(self,["PIs","tags","info","collections"],["reference","charts","datasets","scripts","tools","readme","heads","workflow","extras"])
       self.desc["PIs"] = []
       self.desc["tags"] = []
       self.desc["collections"] = []
       if( isinstance(creator, Person) and isinstance(folder, str) and isinstance(isPublic, bool) and isinstance(serverPath,str)) :
          if( creator.isValid() ) :
             self.desc["info"] = {}
             self.desc["info"]["isPublic"] = isPublic
             self.desc["info"]["serverPath"] = serverPath
             self.desc["info"]["folder"] = folder
             self.desc["info"]["insertedBy"] = creator.getDesc()
             self.desc["info"]["timeStamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #.strftime('%Y-%m-%d %H:%M:%S')
             if( isinstance(globusPath,str) ) :
                 self.desc["info"]["globusPath"] = globusPath

          else :
             sys.exit("Error: creator is not a valid <Person>.")
       else :
           sys.exit("Error: creator must be <Person> and folder must be <str>")
       self.desc["charts"] = []
       self.desc["datasets"] = []
       self.desc["scripts"] = []
       self.desc["tools"] = []
       self.desc["heads"] = []
       self.graph = nx.DiGraph()
    #
    # add PI
    #
    def addPI(self, person) :
       if( isinstance(person, Person) ) :
          if( person.isValid() ) :
             self.desc["PIs"].append( person.getDesc() )
          else :
             sys.exit("Error: PI is not a valid <Person>.")
       else :
          sys.exit("Error: PI must be <Person>.")
    #
    # add Collection
    #
    def addCollection(self, collection) :
       if( isinstance(collection, str) ) :
             self.desc["collections"].append( collection )
       else :
          sys.exit("Error: collection must be <str>.")
    #
    # add notebookFile
    #
    def addNotebookFile(self, notebookFile) :
       if( isinstance(notebookFile, str) ) :
          self.desc["info"]["notebookFile"] = notebookFile
       else :
          print("Cannot add notebookFile, you must provide notebookFile as string.")
	#
    #
    # add Tag
    #
    def addTag(self, tag) :
       Descriptor.addTag(self, tag)
    #
    # add Extra
    #
    def addExtra(self, field, value ) :
       if not "extras" in self.desc :
          self.desc["extras"] = {}
       if( isinstance(field, str) and isinstance(value, str) ) :
          if not field in self.desc["extras"] :
             self.desc["extras"][field] = []
          self.desc["extras"][field].append( value )
       else :
          print("Cannot add field and value, you must provide field and value as string.")
    #
    # addReference
    #
    def addReference(self, item) :
       if( isinstance(item, Reference) ) :
          if( item.isValid() ) :
             self.desc["reference"] = item.getDesc()
          else :
             sys.exit("Error: item is not valid.")
       else : 
          sys.exit("Error: item must be <Reference>.")
    #
    # addNode
    #
    def addNode(self, item) :
       #
       # check what is item 
       # 
       if( (isinstance(item, Chart) or isinstance(item, Dataset) or isinstance(item, Tool) or isinstance(item, Script) or isinstance(item, Head) ) ) : 
          if( isinstance(item, Chart) ) :
             lookup_string = "charts"
             prefix = "c"
          if( isinstance(item, Dataset) ) :
             lookup_string = "datasets"
             prefix = "d"
          if( isinstance(item, Script) ) :
             lookup_string = "scripts"
             prefix = "s"
          if( isinstance(item, Tool) ) :
             lookup_string = "tools"
             prefix = "t"
          if( isinstance(item, Head) ) :
             lookup_string = "heads"
             prefix = "h"
          #
          if( lookup_string in ["charts","datasets","scripts","tools","heads"] ) : 
             if( item.isValid() ) :
                label = self.getId(item)
                if ( label in ["none"] ) : 
                   ind = len( self.desc[lookup_string] )
                   dic = item.getDesc().copy()
                   dic["id"] = prefix+str(ind)
                   self.desc[lookup_string].append(dic)
                   self.graph.add_node(dic["id"])
                else : 
                  print("Warning: cannot insert twice item: ",label) 
             else :
               sys.exit("Error: item is not valid.") 
       else : 
          sys.exit("Error: item must be <Chart>, <Dataset>, <Tool>, <Script>, <Head>.")
    #
    # getNodes
    #
    def getNodes(self) : 
       return self.graph.nodes()
    #
    # getIsolatedNodes
    #
    def getIsolatedNodes(self) : 
       isolis = []
       lis = self.getNodes()
       for i in lis : 
          if( self.graph.degree(i) == 0 ) : 
             isolis.append(i)
       return isolis
    #
    # notifyIsolatedNodes
    #
    def notifyIsolatedNodes(self) : 
       isolis = self.getIsolatedNodes()
       for i in isolis :
          print("Warning: I found an isolated node: ",i)
    #
    # getEdges
    #
    def getEdges(self) : 
       return self.graph.edges()
    #
    # drawGraph
    #
    def drawGraph(self,image) :
      self.notifyIsolatedNodes()
      if( isinstance(image, str) ) : 
         plt.clf()
         nx.draw(self.graph, with_labels=True)
         plt.savefig(image)
         print("Workflow drawn in file:", image)
    #
    # printSubGraph 
    #
    def drawSubGraph(self,image,target) :
      target_id = self.getId(target)
      subnode_list = []
      for node_id in self.graph.nodes() :
         if ( nx.has_path(self.graph,node_id,target_id) ) :
            subnode_list.append( node_id ) 
      if( len( subnode_list ) > 0 ) : 
         subgraph = self.graph.subgraph(subnode_list) 
         if( isinstance(image, str) ) : 
            plt.clf()
            nx.draw(subgraph, with_labels=True)
            plt.savefig(image)
            print("Workflow drawn in file:", image)
      else : 
         print("I could not find nodes connected to " + item_id ) 
    #
    # connectNodes
    #
    def connectNodes(self,lis) :
       if ( len(lis) <=1 ) : 
          sys.exit("List must have at least 2 element.")
       id_lis = []
       for it in lis : 
          label = self.getId(it) 
          if( label in ["none"] ) :
             sys.exit("Error: cannot find item.") 
          else : 
             id_lis.append(label)
       self.graph.add_path(id_lis)
       dic = {}
       dic["nodes"] = self.getNodes()
       dic["edges"] = self.getEdges()
       self.desc["workflow"] = dic
    #
    # get Id
    #
    def getId(self, item) :
       label = "none"
       if( (isinstance(item, Chart) or isinstance(item, Dataset) or isinstance(item, Tool) or isinstance(item, Script) or isinstance(item, Head)) ) : 
          if( isinstance(item, Chart) ) :
             lookup_string = "charts"
          if( isinstance(item, Dataset) ) :
             lookup_string = "datasets"
          if( isinstance(item, Script) ) :
             lookup_string = "scripts"
          if( isinstance(item, Tool) ) :
             lookup_string = "tools"
          if( isinstance(item, Head) ) :
             lookup_string = "heads"
          if( item.isValid(True) ) :
             dsmall = item.getDesc() 
             for dbig in self.desc[lookup_string] : 
                if( dict(dbig, **dsmall) == dbig ) :
                   label = dbig["id"]
          else : 
            sys.exit("Error: item is not valid.") 
       else : 
          sys.exit("Error: item must be <Chart>, <Dataset>, <Tool>, <Script>, <Head>.")
       return label
    #
    # add readme
    #
    def addReadme(self, readme) :
       if( isinstance(readme, str) ) :
          self.desc["readme"] = readme
       else :
          sys.exit("Error: readme must be <str>.")
    #
    # dump Json
    #
    def dumpJSON(self, filename) :
       self.notifyIsolatedNodes()
       Descriptor.dumpJSON(self,filename)
    #
    # send Descriptor
    #
    def sendDescriptor(self,fname,ip,username,password,collection="paper") :
       client=MongoClient(ip,ssl=True,ssl_cert_reqs=ssl.CERT_NONE)
       client.imedb.authenticate(username, password, mechanism='SCRAM-SHA-1')
       # client=MongoClient(ip)
       # client.imedb.authenticate(username, password)
       db=client.imedb
       self.dumpJSON(fname)
       with open(fname,"r") as json_data :
          da=json.load(json_data)
          coll = db[collection]
          paper_id = coll.insert_one(da).inserted_id
          print(fname, "INSERTED! id:", paper_id )
       return paper_id
    #
    # fetch Descriptor
    #
    def fetchDescriptor(self,paper_id,ip,username,password,collection="paper") :
       client=MongoClient(ip,ssl=True,ssl_cert_reqs=ssl.CERT_NONE)
       client.imedb.authenticate(username, password, mechanism='SCRAM-SHA-1')
       # client=MongoClient(ip)
       # client.imedb.authenticate(username, password)
       db=client.imedb
       print("id:",paper_id,"has been FETCHED!")
       coll = db[collection]
       return coll.find_one({"_id": paper_id})

