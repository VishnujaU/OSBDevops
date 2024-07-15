import wlstModule
import jarray
from java.io import File
from java.io import FileInputStream
from java.io import BufferedInputStream
from java.util import Collections
from java.util import LinkedList
from java.util import Properties
from com.bea.wli.sb.management.configuration import SessionManagementMBean
from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
from com.bea.wli.config.env import EnvValueQuery
from com.bea.wli.config.env import QualifiedEnvValue
from com.bea.wli.config.resource import ResourceQuery
from com.bea.wli.config.resource import BaseQuery
from com.bea.wli.config.customization import FindAndReplaceCustomization
from com.bea.wli.sb.util import EnvValueTypes
from com.bea.wli.sb.util import Refs
from com.bea.wli.config import Ref
import datetime

CONFIG_JAR = None
CUSTOMIZATION_FILE = None
SESSION_NAME = "auto_deploy"
alsbSession = None

# Function to load properties from a configuration file
def load_properties(properties_file):
    properties = Properties()
    try:
        input_stream = FileInputStream(properties_file)
        properties.load(input_stream)
        input_stream.close()
    except Exception, e:
        print "Failed to load properties file %s: %s" % (properties_file, e)
        sys.exit(1)
    return properties
# Load configuration properties
CONFIG_FILE = os.environ.get('CONFIG_FILE', sys.argv[3])
config = load_properties(CONFIG_FILE)
# Extract properties from the configuration file
ADMIN_USER = config.getProperty('admin.user')
ADMIN_PASS = config.getProperty('admin.password')
ADMIN_SERVER_URL = config.getProperty('admin.url')
OSB_LOG_PATH = config.getProperty('logfile.path')
OSB_LOG_COMMENT = config.getProperty('logfile.comment')

def readFileBytes(filename):
  file = File(filename)
  bis = BufferedInputStream(FileInputStream(file))
  length = int(file.length())

  bytes = jarray.zeros(length, 'b')
  offset = 0
  numRead = 0
  while (numRead >= 0 and offset < length):
    numRead=bis.read(bytes, offset, length-offset)
    offset += numRead

  bis.close()
  return bytes
def getCustomizationList(filename):
  list = LinkedList()                                                   #store list of customizations
  file = open(filename)                                                 #open customization file
  line = file.readline()                                                #waste header-row
  line = file.readline().strip()                                        #skip to first real line
  linenum = 2                                                           #we are now on the second line
  try:
    while(line):                                                        #line is not null or zero-length
      if (line.startswith("#") == false):
        customization = getLineCustomization(line)                      #get a list of customizations triggered by this line
        if(customization == None):                                      #if line had no matches could be due to typo, raise exception and fail build
          raise "No elements match customization fields. Check line fields and values for typos. If no matches are expected, comment-out line with an # and try again"
        else:
          list.add(customization)                                      #add customization to list of customizations
      line = file.readline().strip()                                  #read the next line
      linenum = linenum + 1
  except:
    raise "ERROR parsing customization file, line " + str(linenum) + ": " + str(sys.exc_info()[0])
  
  # no exceptions, return list of customizations
  return list                               

# get a customization object for the given line
def getLineCustomization(line):
  fields = line.split(',')
  
  # verify correct number of fields
  if (len(fields) != 5):
    raise "Incorrect number of fields. Expected 5. Got " + len(fields) + "."
  
  #PARSE RESOURCE TYPE
  val = fields[0].strip()
  if (len(val) == 0):
    resourceType = None                   #treat empty string as None (null), paradoxically None means all in various search APIs below
  else:
    try:
      resourceType = getattr(Refs, val)   #otherwise resourceType must be a valid field name from the Refs class (determined reflectively) 
    except:
      raise "Invalid ResourceType. Expected either '' (for any) or a static String field name from com.bea.wli.sb.util.Refs. Got '" + val + "'."
  
  #PARSE resource name
  val = fields[1].strip()
  if (len(val) == 0):
    resourceName = None
  else:
    resourceName = val
    
  #PARSE EnvValueType
  val = fields[2].strip()
  if (len(val) == 0):
    envValueType = None
  else:
    try:
      envValueType = Collections.singleton(getattr(EnvValueTypes, val))
    except:
      raise "Invalid EnvValueType. Expected either '' (any) or a static String field from com.bea.wli.sb.util.EnvValueTypes. Got '" + val + "'."  
  
  #PARSE search string
  val = fields[3].strip()
  if (len(val) == 0):
    searchString = None
  else:
    searchString = val
  
  #PARSE replace string
  val = fields[4].strip()
  replaceString = val

  query = ResourceQuery(resourceType)         #initiate a query to find matching resources based on resourceType and resourceName
  query.setLocalName(resourceName)            #local name is the short name of a resource, e.g. 'FMISO_001_SIEBEL_CANCEL_ORDER_BS'
  refs = alsbSession.getRefs(query)           #get a Set of Ref objects that uniquely identify all matching resources
  if(refs == None or refs.size() == 0):
    return None;
    
  evquery = EnvValueQuery(                    #find a list of environment variables of given EnvValueType and containing an optional search string within above Ref resource Set
         Collections.singleton(resourceType), # resources already filtered in ResourceQuery above, setting this to None will ignore this parameter in the EnvValueQuery search
         envValueType,        # search across given environment value types
         refs,                # the resource Ref Set found above
         true,                # only search across resources that are actually modified/imported in this session 
         searchString,        # the string we want to replace, if None, then the entire property is matched and replaced
         false                # if search string not None, match any part of value if it contains searchString, i.e. value.contains(searchString), otherwise it would be value.equals(searchString)
         )
  
  #create a customization object for finding and replacing an environment value
  return FindAndReplaceCustomization("Find and Replace Customization",evquery, replaceString)

################################################################################################   
# MAIN PROGRAM EXECUTION PATH
################################################################################################
try:
  CONFIG_JAR = sys.argv[1]
  CUSTOMIZATION_FILE = sys.argv[2]
  print("Befor Classpath echo")
  print System.getProperty('java.class.path')
  print("After Classpath echo")
  
  print("ADMIN_USER")
  print(ADMIN_USER)
  
  print("CUSTOMIZATION_FILE")
  print(CUSTOMIZATION_FILE)
  
  print("OSB_LOG_PATH")
  print(OSB_LOG_PATH)
  # connect to server
  connect(ADMIN_USER, ADMIN_PASS, ADMIN_SERVER_URL)
  domainRuntime()

  print("Connected to domain")

  # create a session to work in
  sessionMBean = findService(SessionManagementMBean.NAME,SessionManagementMBean.TYPE)
  print("Create session find service")
  #sessionMBean = findService('SessionManagementMBean', 'com.bea:Name=SessionManagement,Type=SessionManagementMBean')
  if (sessionMBean.sessionExists(SESSION_NAME)):    # discard any active auto_deploy session possibly left over from another build
    sessionMBean.discardSession(SESSION_NAME) 
    print("Discarded previous session if any")
  print("Before createSession")
  sessionMBean.createSession(SESSION_NAME)          # create a new 'auto_deploy' session
  print("After createSession")
  
  print("Before getting MBean to handle created session")
  # get an ALSBConfigurationMBean handle to newly created session 
  alsbSession = findService(ALSBConfigurationMBean.NAME + "." + SESSION_NAME, ALSBConfigurationMBean.TYPE)
  print("After getting MBean to handle created session")
  
  print("Before uploading jar")
  # upload the actual jar file
  alsbSession.uploadJarFile(readFileBytes(CONFIG_JAR))  
  print("After uploading jar")
  

  ### THE PASS PHRASE IMPORT/EXPORT FEATURE SHOULD NOT BE USED! ###################
  # then get the default import plan and modify the plan if required
  #if(len(PASS_PHRASE.strip()) > 0): #pass phrase used to encrypt sensitive Security Service Accounts
  #  jarInfo = alsbSession.getImportJarInfo()
  #  importPlan = jarInfo.getDefaultImportPlan()
  # importPlan.setPassphrase(PASS_PHRASE.strip())
  #else:
  #################################################################################
  importPlan = None
  print("Before importing  import plan")
  # import the jar file and check the import status
  result = alsbSession.importUploaded(importPlan)
  print("After importing  import plan")

  
  

  if (result.getFailed().size() > 0):
    print("Before discarding session1")
    sessionMBean.discardSession(SESSION_NAME)
    print("After discarding session1")
    
    raise "ALSB reported failures whilst importing jar. Deployment reversed and aborted."
  else:
    
    alsbSession.customize(getCustomizationList(CUSTOMIZATION_FILE))
    print("Before Activating session")
    sessionMBean.activateSession(SESSION_NAME, "OSB deployment")
    print("After Activating session")

    # This will create a new file or **overwrite an existing file**.
    f = open(OSB_LOG_PATH, "a")
    try:
        print("Before writing file")
        f.write(OSB_LOG_COMMENT+ " : " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") +"\n") # Write a string to a file
        print("After writing file")
    finally:
        f.close()

except:
  print "UNEXPECTED ERROR: ", sys.exc_info()[0]
  dumpStack()
  try:
    print("Before discarding session end2")
    sessionMBean.discardSession(SESSION_NAME)
    print("After discarding session end2")
  except:
    print ''
  sys.exit(1)
