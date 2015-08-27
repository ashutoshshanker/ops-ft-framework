import argparse
import os
import sys
import time
import datetime
import common
#import headers
import json
from lib import *
from common import *
import inspect
import lib.gbldata

class testEnviron ():
    def __init__(self, **kwargs):
        self.topoDict = kwargs.get('topoDict')
        
        self.rsvnId = None
        self.topoObj = None
        self.libDirs = ['common', 'console', 'host', 'switch', 'switch/OVS', 'switch/CLI', 'topology']
        self.ResultsDirectory = dict()
        self.envSetup()
        # Here is where we will stub in the provisionng logic.  We should have a topoObj by now 
        self.topoObj.CreateDeviceObjects()
        if self.rsvnId != "virtual":
            common.LogOutput('info', "Enabling all logical links")
            self.topoObj.LinkModifyStatus(enable=1, allLogical=1)
        
        
    def envSetup(self):
        # Command line argument parser
        parser = argparse.ArgumentParser(description='OpenHalon environment test shell')
        #parser.add_argument('--testCase', help="testcase name to run", required=True, dest='testCaseName')
        parser.add_argument('--physicalTopology', help="physical topology filename", required=False, dest='phystopo', default=None)
        parser.add_argument('--targetBuild', help="List of logical DUTs and coorsponding builds to provision", required=False, dest='targetBuild', default=None)
        parser.add_argument('--resultDir', help="Result directory for the test case to put results in", required=False, dest='resultDir', default=None)
        parser.add_argument('-s', help="pytest option", required=False, dest='ptest', default=None)
        args = parser.parse_args()
        self.rsvnId = 'virtual'
        self.targetBuild = args.targetBuild
        self.resultDir = args.resultDir
        
        
        pythonPathString = ""
        fwbase = os.environ['FT_FRAMEWORK_BASE']
        sys.path.append(fwbase)
        appendDir = fwbase + "/lib"
        sys.path.append(appendDir)
        
        for curDir in self.libDirs:
            appendDir = fwbase + "/lib/" + curDir
            sys.path.append(appendDir)
            if pythonPathString != "":
                pythonPathString += ":" + appendDir
            else:
                pythonPathString += appendDir

        entftbase = os.environ['FT_FRAMEWORK_ENT']
        if entftbase != "":
            appendDir = entftbase
            sys.path.append(appendDir)
            if pythonPathString != "":
                pythonPathString += ":" + appendDir
            else:
                pythonPathString += appendDir
            appendDir = entftbase + "/lib"
            sys.path.append(appendDir)
            if pythonPathString != "":
                pythonPathString += ":" + appendDir
            else:
                pythonPathString += appendDir
                
            appendDir = entftbase + "/lib/RTL"
            sys.path.append(appendDir)
            if pythonPathString != "":
                pythonPathString += ":" + appendDir
            else:
                pythonPathString += appendDir
        
        #masterImport = fwbase + "/include/masterImport.py"
        #with open(masterImport) as f:
        #    code = compile(f.read(), masterImport, 'exec')
        #    exec(code)
        
        if args.resultDir is None:
            # Means we need to create the results structure
            currentDir = GetCurrentDirectory()
            ts = time.time()
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%b-%d_%H:%M:%S')
            baseResultsDir = os.environ['FT_FRAMEWORK_BASE'] + "/results"
            self.ResultsDirectory['resultsDir'] = baseResultsDir + "/" + timeStamp + "/"
            # HEADERS PULLBACK
            #headers.ResultsDirectory['resultsDir'] = baseResultsDir + "/" + timeStamp + "/"
            gbldata.ResultsDirectory = baseResultsDir + "/" + timeStamp + "/"
            self.ResultsDirectory['rtlDir'] = baseResultsDir + "/" + timeStamp + "/RTL/."
            #headers.ResultsDirectory['rtlDir'] = baseResultsDir + "/" + timeStamp + "/RTL/."
        else:
            baseResultsDir = args.resultDir
            self.ResultsDirectory['resultsDir'] = baseResultsDir + "/"
            gbldata.ResultsDirectory = baseResultsDir + "/"
            # HEADERS PULLBACK
            #headers.ResultsDirectory['resultsDir'] = baseResultsDir + "/"
            self.ResultsDirectory['rtlDir'] = baseResultsDir + "/" + "/RTL/"
            #headers.ResultsDirectory['rtlDir'] = baseResultsDir + "/" + "/RTL/"
        
        self.ResultsDirectory['summaryLog'] = self.ResultsDirectory['resultsDir'] + "summary.log"
        #headers.ResultsDirectory['summaryLog'] = self.ResultsDirectory['resultsDir'] + "summary.log"
        self.ResultsDirectory['detailLog'] = self.ResultsDirectory['resultsDir'] + "detail.log"
        #headers.ResultsDirectory['detailLog'] = self.ResultsDirectory['resultsDir'] + "detail.log"
        #self.ResultsDirectory['testcaseName'] = testCaseName
        
        retCode = ChangeDirectory(baseResultsDir)
        if retCode['returnCode'] == 0 :
            #if args.resultDir is None:
            #time.sleep(1)
            retCode = CreateDirectory(self.ResultsDirectory['resultsDir'])

        # Now settle on topology
        if args.phystopo is None:
            # Check to see if we have an RSVNID variable
            envKeys = os.environ.keys()
            for curKey in envKeys:
                if curKey == "RSVNID":
                    tmpRsvn = os.environ['RSVNID']
                    if str.isdigit(tmpRsvn):
                        common.LogOutput('info', "Detected RSVNID in environment")
                        self.rsvnId = tmpRsvn
                    break
        else:
            self.rsvnId = args.phystopo
            
        
        if retCode['returnCode'] == 0:
            # Create RTL directory
            if self.rsvnId != "virtual":
                ChangeDirectory(self.ResultsDirectory['resultsDir'])
                retCode = CreateDirectory("RTL/.")
            # Create Files under the result directory structure(summary file)
            retCode = FileCreate(self.ResultsDirectory['resultsDir'], "summary.log")
            if retCode['returnCode'] <> 0 :
                common.LogOutput('error', "File summary.log not created in the directory structure")
                exit(1)
            # Create Files under the result directory structure(detail.log)
            retCode = FileCreate(self.ResultsDirectory['resultsDir'], "detail.log")
            if retCode['returnCode'] <> 0 :
                common.LogOutput('error', "File detail.log not created in the directory structure")
                exit(1)
            # Copy topology.xml and the testcase file to results directory for reference
            #try :
            #    shutil.copy(args.testCaseName, self.ResultsDirectory['resultsDir'])
            #except :
            #    common.LogOutput('error', "Testcase file not copied to destination -> " + self.ResultsDirectory['resultsDir'])
            #    exit(1)
        else :
            common.LogOutput('error', "Result Directory structure not created . Exiting")
            exit(1)
        
        # Header printblock
        common.LogOutput('info', "", datastamp=True)
        #common.LogOutput('info' , "Test Case is: " + args.testCaseName)
        common.LogOutput('info' , "Physical Topology is: " + self.rsvnId)
        
        # Read in the Topology
        if self.rsvnId == "virtual":
            self.topoType = "virtual"
            common.LogOutput('info', "Topology is virtual - creating environment specified in the test case topoDict structure")
            # Create a topology object
            #self.topoObj = lib.Topology(topoDict=self.topoDict, runEnv=self)
            self.topoObj = Topology(topoDict=self.topoDict, runEnv=self)
        elif str.isdigit(self.rsvnId) is True:
            self.topoType = "physical"
            try:
                import RTL
            except ImportError:
                common.LogOutput('debug', "RTL environment not available")

            # This means we have passed a reservation in
            common.LogOutput('info', "Topology reservation ID was passed in.  ID = " + str(self.rsvnId) + " querying the topology")
            # Create Topology Object
            self.topoObj = RTL.RTL_Topology(topoDict=self.topoDict, topoType="physical", rsvnId=self.rsvnId, runEnv=self)
    
    def topoObjGet(self):
        return(self.topoObj)

    
    
    
class returnStruct():
    def __init__(self,**kwargs):
        self.retCode = kwargs.get('returnCode', None)
        self.return_buffer = kwargs.get('buffer', "")
        self.data = kwargs.get('data', None)
        self.jsonCreate()

    def returnCode(self):
        return self.retCode
    
    def buffer(self):
        return self.return_buffer
    
    def returnJson(self):
        return self.jsonData
    
    def dataKeys(self):
        return self.data.keys()
    
    def valueGet(self, **kwargs):
        key = kwargs.get('key', None)
        if key is None:
            return self.data
        return self.data[key]
    
    def retValueString(self):
        return self.jsonData
    
    def printValueString(self):
        localString = self.retValueString()
        LogOutput('info', localString)
        
    def jsonCreate(self):
        #localDict = self.data
        localDict = dict()
        localDict['returnCode'] = self.retCode
        localDict['buffer'] = self.return_buffer
        localDict['data'] = self.data
        self.jsonData = json.dumps(localDict,indent=3)


class DeviceLogger(object):
    # This function overrides the pexpect logger write function to add timestamps to device logs
    def __init__(self, file):
        self.file = file

    def write(self, data):
        # .. filter data however you like
        ts = time.time()
        ts = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        data = data.strip()

        # Do not log blank spaces
        if data in [' ', '', '\n', '\r', '\r\n']:
            return
        if data:  # non-blank
            # Inspect the stacktrace to get the called module
            # Module trace needs to be dumped to logging module
            # This code will not log unnecessary internal modules (so that log looks clean)
            stackTrace = inspect.stack()
            module = inspect.getmodule(stackTrace[4][0])
            if module <> None :
                modulename = module.__name__
                if modulename == "pexpect" :
                    modulename = None
                else :
                    self.file.write("++++" + ts + "  " + "Module:" + "(" + modulename + ")" + "  " + "\n")
        return self.file.write(data + "\n")
       
    # return self.file.write("%s %s" % (ts, data))  # write to original file
    def flush(self):
        self.file.flush()

    # OpenExpectLog function opens a new file to log the expect buffer output
    # Return 1 in case of error (expect logfile not created) , expect file handle in case of success
    def OpenExpectLog(self, ExpectFileName) :
        #retCode = FileCreate(headers.ResultsDirectory['resultsDir'], ExpectFileName)
        retCode = FileCreate(gbldata.ResultsDirectory, ExpectFileName)
        if retCode['returnCode'] == 0:
            # HEADERS PULLBACK
            #headers.ResultsDirectory['ExpectFileName'] = headers.ResultsDirectory['resultsDir'] + "/" + ExpectFileName
            myExpectFileName = gbldata.ResultsDirectory + "/" + ExpectFileName
            expectLogfile = open(myExpectFileName, 'w')
            return expectLogfile
        else :
            returnCode = 1
        return returnCode


# General library routines
#Params ::  Directory Path to be created
def CreateDirectory(dirName):
    dir = os.path.dirname(dirName)
    retDataStruct = dict()
    if not os.path.exists(dirName):
        os.makedirs(dir)
        if os.path.exists(dir) :
            retDataStruct['DirPath'] = os.getcwd()+dirName
            retDataStruct['returnCode'] = 0
        else :
            common.LogOutput('error',"Result Directory"+dir ,"not created")
            retDataStruct['returnCode'] = 1
    else :
        retDataStruct['returnCode'] = 1
    return retDataStruct

#Function to change directory path
# Params  :: Destination Path
def ChangeDirectory(path):
    retDataStruct = dict()
    try :
        os.chdir(path)
        retDataStruct['returnCode'] = 0
    except :
        retDataStruct['returnCode'] = 1
    return retDataStruct

#Function to Get directory
# Returns the current dir path on success
def GetCurrentDirectory():
    currentDir = os.getcwd()
    if currentDir is None:
        retStruct = dict()
        retStruct['returnCode'] = 1
        return retStruct
    else :
        return currentDir
    
#Creating new files
#Params :: Filename , Directory path where file should exists. (Dir must exist)
def FileCreate(DirPath,fileName):
    filePath = os.path.join(DirPath,fileName)
    retDataStruct = dict()
    try :
        if not os.path.exists(fileName):
            #pdb.set_trace()
            file = open(filePath,'w')   # Trying to create a new file or open one
            #file.close()
            retDataStruct['returnCode'] = 0
        else :
            print "File already exists in this path" + DirPath
            #do nothing
    except Exception as Err:
        print Err
        raise Exception("FILE NOT CREATED:: "+fileName)
        retDataStruct['returnCode'] = 1
    return retDataStruct



# library routine to write the logger message to summary and detail file based on the level
# def LogOutputToFile(path, level, message):
#     intResult = 1
#     strSummaryFileName = path + "summary.log"
#     strDetailedFileName = path + "detail.log"
#     if (os.access(strSummaryFileName, os.W_OK)) :
#         pass
#     else :
#         print("either file not exists for %s or no write permission" % strSummaryFileName)
#         return intResult
# 
#     if (os.access(strDetailedFileName, os.W_OK)) :
#         pass
#     else :
#         print("either file not exists for %s or no write permission" % strDetailedFileName)
#         return intResult
# 
#     if (level == "debug"):
#         writeLogFile(strDetailedFileName, level, message)
#     else :
#         writeLogFile(strSummaryFileName, level, message)
#         writeLogFile(strDetailedFileName, level, message)
#     intResult = 0
#     return intResult
# 
# #internal routine to write the logger message to passed file
# 
# def writeLogFile(logfile, level, message) :
#     logger = logging.getLogger()
#     formatter = logging.Formatter('%(levelname)-5s - %(asctime)-6s - %(message)s','%H:%M:%S')
#     fh = logging.FileHandler(logfile)
#     if (level == "info"):
#         fh.setLevel(logging.INFO)
#         logger.setLevel(logging.INFO)
#         fh.setFormatter(formatter)
#         logger.addHandler(fh)
#         logger.info(message)
#     elif (level == "error"):
#         fh.setLevel(logging.ERROR)
#         logger.setLevel(logging.ERROR)
#         fh.setFormatter(formatter)
#         logger.addHandler(fh)
#         logger.error(message)
#     elif (level == "debug"):
#         fh.setLevel(logging.DEBUG)
#         logger.setLevel(logging.DEBUG)
#         fh.setFormatter(formatter)
#         logger.addHandler(fh)
#         logger.debug(message)
#     logger.removeHandler(fh)
#     
#     def LogOutput(dest, message, **kwargs):
#         datestamp = kwargs.get('datastamp', False)
#         logType = str(dest)
# 
#         if datestamp is True:
#           timestring = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
#         else:
#             timestring = time.strftime("%H:%M:%S", time.localtime())
#         messageSpl = message.split("\n")
#         timestampSent = 0
#         for msgLine in messageSpl:
#             if timestampSent:
#                 #print '\t' + logType + '  ' + msgLine
#                 print('%s'%msgLine)
#             else:
#                 # examine the callstack to print out.
#                 mystack = inspect.stack()
#                 #print mystack
#                 mystacklen = len(mystack)
#             stackstring = ""
#             i = mystacklen - 1
#             while i > 0:
#                 curMod = mystack[i][3]
#                 if curMod == "<module>":
#                     # Need to skip module
#                     i -= 1
#                     continue
#                 stackstring += curMod
#                 i -= 1
#                 if i > 0:
#                     stackstring += "->"
#                     #Inspect the stacktrace to get the called module
#                     #Module trace needs to be dumped to logging module
#                     stackTrace = inspect.stack()
#                     module = inspect.getmodule(stackTrace[1][0])
#                     len1 = len(stackTrace)
#                 if len1 >= 4:
#                     if module <> None :
#                         modulename =  module.__name__
# 
#             # = inspect.stack()[1][3]
#             if logType == 'info' or logType == 'error':
#                 print("%s %-6s\t%s"%(timestring,logType,msgLine))
#             #else:
#             #   print("%s %-5s\t[%s] %s"%(timestring,logType,stackstring,msgLine))
#             #print(timestring, " ", logType, " ", msgLine)
#             #   timestampSent = 1
# 
#     #Logging messages to Log files based on severity
#     try :
#         if modulename <> "common.tcAction":
#             message = "::%-30s\t%s"%(modulename,message)
#     except NameError:
#         #message = message
#         blankString = ""
#         if logType == 'info':
#             message = "%s"%(message)
#         else:
#             message = "::%s"%(message)
#     common.LogLib.LogOutputToFile(headers.ResultsDirectory['resultsDir'], dest, message)
