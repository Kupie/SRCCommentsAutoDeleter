#Change this to the Game name on SRC
#Grab this from the URL easily; such as "https://www.speedrun.com/newtone" would be "newtone"
GamePage = 'newtone'

#If username contains these strings, don't delete them
#Recommended to put Moderator username list in this. It is comma separated, quotes around names
#If a comment is made by anyone in this list, it will *not* delete the comment. This is case-insensitive.
userWhiteList = ["kupokraft", "Gordo", "Vapo", "Critch_", "ItsTicker", "Greenbulmers", "djlambton", "Derek", "Spruce37", "PotatoOnCrack", "Greeny0359"]

#How many runs from each leaderboard should we check?
#For example, if this was "25" it would only get the top 25 runs from each category/level leaderboard
#If this is set quite high for leaderboards with many categories and levels, it may take a while to refresh.
maxRunsToCheck = 50

#How many seconds in between refreshing runs + comments. Don't crank this number too low, SRC crashes enough as is
timewait = 60


#Should this run as a dryrun? Basically, if set to "True", script will only print comment information of what it would delete instead of deleting them
#This is so you can test the script before running it
dryRun = True

#NOTE THAT THIS REQUIRES A SUPPORTED BROWSER TO BE LOGGED IN TO SRC TO ACTUALLY DELETE COMMENTS
#That is because this uses cookies from your web browser in order to make the delete request

#Which web browser should the script grab cookies from?
#Supported options are: Firefox, Chrome, Chromium, Opera, Edge, Brave
#Examples:
#Browser = 'Firefox'
#Browser = 'Chrome'
#Browser = 'Chromium'
#Browser = 'Opera'
#Browser = 'Edge'
#Browser = 'Brave'

Browser = 'Chrome'



#END OF USER-CONFIGURABLE PARTS

#Check python version
import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
    sys.exit(1)

#need json formatter
import json

#Make sure browser_cookie3 is installed
try:
    import browser_cookie3
except ImportError:
    print ('--Python module browser_cookie3 not installed, unable to delete comments without using a Speedrun.com cookie. Continuing in Dryrun mode--')
    dryRun = True
    pass

def cookieFailure(x = False):
    if not x:
        print('--Failed to import cookies. Is ' + Browser + ' installed and logged in to speedrun.com?--')
    print('--Continuing in Dryrun mode, as I can\'t delete anything without cookies--')
    global dryRun
    dryRun = True


#Don't need cookies if we're just loading comments
if not dryRun:
    #Import cookies from Firefox for speedrun.com
    if (Browser.lower() == 'firefox'):
        try:
            cookiejar = browser_cookie3.firefox(domain_name='speedrun.com')
        except:
            cookieFailure()
            pass
    elif (Browser.lower() == 'chrome'):
        try:
            cookiejar = browser_cookie3.chrome(domain_name='speedrun.com')
        except:
            cookieFailure()
            pass
    elif (Browser.lower() == 'chromium'):
        try:
            cookiejar = browser_cookie3.chromium(domain_name='speedrun.com')
        except:
            cookieFailure()
            pass
    elif (Browser.lower() == 'opera'):
        try:
            cookiejar = browser_cookie3.opera(domain_name='speedrun.com')
        except:
            cookieFailure()
            pass
    elif (Browser.lower() == 'edge'):
        try:
            cookiejar = browser_cookie3.edge(domain_name='speedrun.com')
        except:
            cookieFailure()
            pass
    elif (Browser.lower() == 'brave'):
        try:
            cookiejar = browser_cookie3.brave(domain_name='speedrun.com')
        except:
            cookieFailure()
            pass
    else:
        print('--Unsupported browser specified, check the "Browser = " section of the script above--')
        cookieFailure(True)
        pass

  
from datetime import datetime
import os
import requests
import time
import ctypes
import urllib3

#sets nice title
ctypes.windll.kernel32.SetConsoleTitleW("SRC Comments Grabber/Deleter v1.0.2")

#disable SSL warnings. SRC requires HTTPS but sometimes their certificate isn't "proper", this makes it connect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Makes a universal cls function to clear screen. Thanks popcnt: https://stackoverflow.com/a/684344
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

#Plz no bully the SRC servers
#If you're bright enough to remove this sleep, you're bright enough to know why we shouldn't send one request after another to SRC instantly
def sleepy():
    time.sleep(0.25)

#Set whitelist to lowercase, so we can do case-insensitive checking later by lowercase-ing the usernames in comments
for i in range(len(userWhiteList)):
    userWhiteList[i] = userWhiteList[i].lower()





#hasLevels boolean; if a game has individual levels we need to handle getting runs a bit extra methody
hasLevels = False

#Time to get a list of every single leaderboard, category and level for the game. I only do this once instead of every time we check for comments
try:
    #Get list of Categories
    categories = requests.get('https://www.speedrun.com/api/v1/games/' + GamePage + '/categories', verify=False)
except Exception as e:
    #If it fails, URL is invalid... or SRC is down. That's always an option
    print ("Exception: " + str(e))
    print ("Invalid URL connection to SRC failed. Open this python script and check that 2nd line! Exiting...")
    sys.exit(1)

jsonOut = json.loads(categories.content)
categoryList = []
for i in jsonOut['data']:
    #print(i['id'])
    #print(jsonOut['data'][0]['id'])
    if (i['type'] == 'per-game'):
        categoryList.append(i['id'])
    if (i['type'] == 'per-level'):
        hasLevels = True

#Get List of Levels
levelList = []
if hasLevels:
    try:
        levels = requests.get('https://www.speedrun.com/api/v1/games/' + GamePage + '/levels', verify=False)
    except Exception as e:
        #If it fails, URL is invalid... or SRC is down. That's always an option
        print ("Exception: " + str(e))
        print ("Connection to SRC failed. SRC could be down! Exiting...")
    pass
    
    jsonOut = json.loads(levels.content)
    for i in jsonOut['data']:
        levelList.append(i['id'])





#They have set us up the loop
while True:
    if not dryRun:
        print('WARNING, SCRIPT CONFIGURED TO DELETE COMMENTS. CLOSE WINDOW OR PRESS CTRL+C NOW TO CANCEL.')
    print('SRC page to check: https://speedrun.com/' + GamePage)
    if not dryRun:
        print('Using browser cookies from: ' + Browser)

    print('User Whitelist:')
    for i in range(len(userWhiteList)):
        print(userWhiteList[i],end = ', ')
    print('\n')
    print('Number of categories: ' + str(len(categoryList)))
    if hasLevels:
        print('Number of levels: ' + str(len(levelList)))

    if not dryRun:
        #Get csrftoken from speedrun.com main page. Without beautifulsoup this is 'fun'TM
        try:
            mainPage = requests.get('https://www.speedrun.com/', verify=False, cookies=cookiejar)
            split1 = str(mainPage.content).split('<meta name="csrftoken" content="')
            split2 = split1[1].split('">')
            csrftoken = split2[0]
            #print('csrftoken: ' + csrftoken)
            #Just in-case people don't want this showing on their screen...
            print('csrftoken: ********************************')
        except Exception as e:
            print ("Exception: " + str(e))
            print('\nCould not connect to SRC and get csrftoken. Are you sure you\'re logged in to firefox on SRC? This script uses Firefox\'s cookies')
            sys.exit(0)
    try:
        #Get list of runs from all categories
        runList = []
        print('Getting list of top ' + str(maxRunsToCheck) + ' runs from all categories...')
        for i in categoryList:
            try:
                runs = requests.get('https://www.speedrun.com/api/v1/leaderboards/' + GamePage + '/category/' + i, verify=False)
            except Exception as e:
                #If it fails, URL is invalid... or SRC is down. That's always an option
                print ("Exception: " + str(e))
                print ("Connection to SRC failed. SRC could be down! Exiting...")
            pass
            
            #Give SRC some space to breathe between requests
            sleepy()
            try:
                jsonOut = json.loads(runs.content)
            except Exception as e:
                print ("Exception converting 'runs' to JSON from categories: " + str(e))
                print('runs.content value: ' + runs.content)
                sys.exit(1)
            runsAdded = 0
            for i in jsonOut['data']['runs']:
                if (runsAdded < maxRunsToCheck):
                    runList.append(i['run']['id'])
                    runsAdded += 1
                
        #Get list of runs from all Levels (yes, they're separate from Categories... thanks SRC)
        if hasLevels:
            print('Getting list of top ' + str(maxRunsToCheck) + ' runs from all levels...')
            for i in levelList:
                try:
                    runs = requests.get('https://www.speedrun.com/api/v1/runs?level=' + i, verify=False)
                except Exception as e:
                    #If it fails, URL is invalid... or SRC is down. That's always an option
                    print ("Exception: " + str(e))
                    print ("Connection to SRC failed. SRC could be down!")
                pass
                
                #Give SRC some space to breathe between requests
                sleepy()
                try:
                    jsonOut = json.loads(runs.content)
                except Exception as e:
                    print("Exception converting 'runs' to JSON from levels: " + str(e))
                    print('runs.content value: ' + runs.content)
                    sys.exit(1)
                runsAdded = 0
                for i in jsonOut['data']:
                    if (runsAdded < maxRunsToCheck):
                        runList.append(i['id'])
                        runsAdded += 1
        
        print('Number of runs: ' + str(len(runList)))
        #Finally, we get a list of comments from every run
        print('Getting list of comments from all runs... this may take a while')
        commentList = []
        commentRunDict = {}
        #Why did I name the loop counter this? Don't ask, it was hours past bedtime
        donionRings = 0
        percCompleteNew = 0
        percComplete = 0
        for x in runList:
            try:
                now = str(round(time.time()))
                #for testing deleting comments that don't exist. SRC caches anything gotten with that specific 'now' value
                #now = '0'
                runPage = requests.get('https://www.speedrun.com/_fedata/comments/list?itemType=run&itemId=' + x + '&page=1&now=' + now + '&all=1', verify=False)
            except Exception as e:
                #If it fails, URL is invalid... or SRC is down. That's always an option
                print ("Exception: " + str(e))
                print ("Connection to SRC failed. SRC could be down!")
            donionRings +=1
            #Give SRC some space to breathe between requests
            sleepy()
            percCompleteNew = round(donionRings / len(runList) * 100)
            if (percCompleteNew != percComplete):
                print('Complete: %' + str(percComplete + 1), end='\r', flush=True)
                percComplete = percCompleteNew
                if (percComplete == 100):
                    print()
            
            jsonOut = json.loads(runPage.content)
            for i in jsonOut['comments']:
                commentDict = {'id': i['commentId'],'user': (i['user']['name']),'comment': i['text'],'run':x}
                commentRunDict[i['commentId']] = x
                #print(commentDict)
                #print('--')
                #print('CommentID: \t' + i['commentId'])
                #print('Username: \t' + i['user']['name'])
                #print('Comment: \t' + i['text'])
                commentList.append(commentDict)
                    
        print()
        commentIdsToDelete = []
        #Check if user is in whitelist
        for i in commentList:
            if i['user'].lower() in userWhiteList:
                pass
                #print('not deleting comment by: ' + i['user'])
            else:
                commentIdsToDelete.append(i['id'])
                #print('deleting comment by: ' + i['user'])
        #
        if dryRun:
            print('Dryrun Enabled, printing all comment info: ')
            for commentData in commentList:
                print(commentData)
            print('Dryrun enabled, would delete these comments: ')
            for i in commentIdsToDelete:
                print('Would delete: ' + i)
            if not commentIdsToDelete:
                print('None')
        else:
            for i in commentIdsToDelete:
                print('Deleting CommentID: ' + i)
                #i = 'o4liy'
                deletePost = {"commentId":i,"deleted":"true","block":"false","purge":"false","csrftoken":csrftoken}
                deleteRequest = requests.post('https://www.speedrun.com/_fedata/comments/delete', json = deletePost, verify=False, cookies=cookiejar)
                #print('\n\n\n\n\n\n-----------RESPONSE:--------------\n\n ' + deleteRequest.text + '\n\n\n\n\n\nJSONOUT\n\n\n')
                jsonOut = deleteRequest.json()
                try:
                    deletedResult = str(jsonOut['comment']['deleted'])
                    deletedResult = deletedResult.lower()
                    if (deletedResult == 'true'):
                        print('Successfully Deleted commentID ' + i + ' from run https://speedrun.com/run/' + commentRunDict[i])
                    else:
                        print('Failed to delete for some reason??? This message shouldn\'t even appear anywhere ever. Here\'s the JSON:')
                        print(str(jsonOut))
                        print('Here\'s the json type:')
                        try:
                            print(type(jsonOut['comment']['deleted']))
                        except:
                            pass
                except:
                    print ('Failed to Delete commentID ' + i + ' from runID ' + commentRunDict[i] + '. Error from SRC: ' + str(jsonOut['errors'][0]))
                sleepy()
            if not commentIdsToDelete:
                print('Found nothing to delete')

        print('Refreshing in ' + str(timewait) + ' seconds.')
        #Wait "timewait" amount of seconds before running again
        time.sleep(timewait)
        cls()

    except KeyboardInterrupt:
        # quit
        print('\nKeyboard interrupt received, quitting...')
        sys.exit()
