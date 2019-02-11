import numpy
import datetime
import os
import glob
import pyglet
pyglet.options['shadow_window'] = False
from psychopy import event, core, gui, monitors
import csv

# info for timestamp in savefile name
nowTime=datetime.datetime.now()

###################### Size info ########################
#Our images have to be either 384 or 768 pixels tall ...
# if viewing distance is large, use 768 ... if not, use 384
stimSize = 768
#stimSize = 384

################### Timing info ####################
stimDuration=3 #seconds
fixationBaseTime=0 #seconds
fixationDelta=0.7 #seconds
responseTimeout=7 #seconds

################### Monitor setup ######################
localMonitors=monitors.getAllMonitors()

################## Subject setup #################
#load previous responses
files=gui.fileOpenDlg(tryFilePath='response_data',allowed='*.txt')

if len(files)==0:
    #user cancelled--abort
    core.quit()
else:
    #get subject number from filename
    (oldFilePath,oldFile)=os.path.split(files[0])
    fileNameParts=oldFile.split('_')
    subject=fileNameParts[1]
    runNum=fileNameParts[2][3:]
    with open(os.path.join('response_data',oldFile),'rt') as fileIn:
        #loop through lines and keep image numbers for which the subject responded "yes"
        inputObject=csv.reader(fileIn)
        keepImageNum=0
        keepImagesList=[]
        for row in inputObject:  
            if row[0].split('\t')[1]=='1':
                keepImagesList.append(row[0].split('\t')[0])
                keepImageNum+=1
    #create an output file name
    outputFile=os.path.join('response_data','FAOT_Naming_%s_run%s_%04d%02d%02d_%02d%02d.txt'%(subject,runNum,nowTime.year,nowTime.month,nowTime.day,nowTime.hour,nowTime.minute))

subMonitor=monitors.Monitor('testMonitor')
screenSize=subMonitor.getSizePix()

################### image files ##########################
numImages = keepImageNum
imageFiles = keepImagesList
numpy.random.shuffle(imageFiles)

#################### response recording #####################
#array with 3 columns for image number, response, and response time (reaction time)
subjectResponses=[]
quitKeys=['escape']
doneKeys=['enter','return']
deleteKeys=['backspace']

################### open a stimulus window #####################
from psychopy import visual #do this here or else it breaks the guidlg
winSub=visual.Window(screenSize,monitor=subMonitor,units='pix',screen=1,color=[0,0,0],colorSpace='rgb',allowGUI=False)

################### create the fixation mark ####################
fixSize=7
fixSquare=visual.Rect(winSub,width=fixSize, height=fixSize,fillColor=[1,1,1],fillColorSpace='rgb',lineColor=[1,1,1],lineColorSpace='rgb',units='pix')

#################### create the image stimulus #####################
imageStim=visual.ImageStim(winSub,image=imageFiles[0],pos=[0,0],size=stimSize,units='pix')

#################### create a gray screen for after stimulus ####################
blankGray=visual.Rect(winSub,width=1024,height=768,fillColor=[0,0,0],fillColorSpace='rgb',lineColor=[0,0,0],lineColorSpace='rgb',units='pix')

##################### Instructions ###############################
instructionMsg=visual.TextStim(winSub,pos=[0,0],text='For each image, type the name of the the object then press enter. \n\nIf you can\'t name it, press enter. \n\nPress any key to begin.')

instructionMsg.units = 'deg'
instructionMsg.height = .5
instructionMsg.draw()

winSub.flip()
thisKey=None
while thisKey==None:
    thisKey=event.waitKeys()
if thisKey in quitKeys:
    core.quit()
else:
    event.clearEvents()
thisName=visual.TextStim(winSub,pos=[0,-200],units='pix',height=25)

################ set up task timers ############################
scanTimer=core.Clock()
startTime=scanTimer.getTime()
trialTimer=core.Clock()
trialTime=trialTimer.getTime()
imageTimer=core.Clock()
responseTimer=core.Clock()

################# loop through the images #######################
for iIm in range(numImages):
    trialStartTime=scanTimer.getTime()-startTime
    trialTimer.reset()
    trialTime=trialTimer.getTime()
    #show the fixation mark
    fixSquare.draw()
    winSub.flip()
    #load the next image
    thisImage=imageFiles[iIm]
    imageStim.setImage(thisImage)
    currentName=''
    #wait to flip until the fixation mark time is done...
    fixJitter=numpy.float(numpy.random.randint(0,fixationDelta*10,1))/10.0
    fixationTime=fixationBaseTime+fixJitter
    while trialTime < fixationTime:
        fixSquare.draw()
        winSub.flip()
        trialTime=trialTimer.getTime()
        for key in event.getKeys():
            if key in quitKeys:
                #save responses
                with open(outputFile,'wb') as f:
                    writer=csv.writer(f)
                    writer.writerow(['image number','response','reaction time'])
                    for item in subjectResponses:
                        writer.writerow((item[0],item[1],item[2]))
                core.quit()
    #show the image
    blankGray.draw()
    imageStim.draw()
    winSub.flip()
    event.clearEvents()#clear the keyboard buffer
    imageTimer.reset()
    imageTimer.reset()
    imageTime=imageTimer.getTime()
    responseTimer.reset()
    responseTime=responseTimer.getTime()
    gotResponse=0
    while gotResponse==0:
        imageStim.draw()
        thisName.text=currentName
        thisName.draw()
        winSub.flip()
        imageTime=imageTimer.getTime()
        #check for responses until timeout time
        responseTime=responseTimer.getTime()
        for key in event.getKeys():
            if key in quitKeys:
                #save responses
                with open(outputFile,'wb') as f:
                    writer = csv.writer(f)
                    writer.writerow(['image number','response','reaction time'])
                    for item in subjectResponses:
                        writer.writerow((item[0],item[1],item[2]))
                core.quit()
            elif key in doneKeys:
                gotResponse=1
                responseTime=responseTimeout+1
                reactionTime=imageTimer.getTime()
                newEntry=[imageFiles[iIm],currentName,('%.3f'%reactionTime)]
                subjectResponses.append(newEntry)
            elif key in deleteKeys:
                currentName=currentName[0:-1]
            elif key in ['space']:
                currentName=currentName+' '
            elif key in ['bracketleft','bracketright','tab','quoteleft','capslock','lctrl','rctrl','lalt','ralt','lwindows','rwindows','up','down','left','right','lshift','rshift']:
                #ignore!
                currentName=currentName
            elif key in['semicolon']:
                currentName=currentName+';'
            elif key in['apostrophe']:
                currentName=currentName+'\''
            elif key in['slash']:
                currentName=currentName+'/'
            elif key in['period']:
                currentName=currentName+'.'
            elif key in['comma']:
                currentName=currentName+','
            elif key in['minus']:
                currentName=currentName+'-'
            elif key in['equal']:
                currentName=currentName+'='
            elif key in['backslash']:
                currentName=currentName+'\\'
            else:
                #append the current key to the string
                currentName=currentName+key
#flip a gray screen
    blankGray.draw()
    winSub.flip()

#record the responses to a file
with open(outputFile,'wb') as f:
    writer=csv.writer(f)
    writer.writerow(['image number','response','reaction time'])
    for item in subjectResponses:
        writer.writerow((item[0],item[1],item[2]))

thanks=visual.TextStim(winSub,text="Thank you!")
thanks.draw()
winSub.flip()
core.wait(1)
winSub.close()



