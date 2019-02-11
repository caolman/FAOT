
import numpy
import datetime
import os
import glob
import pyglet
pyglet.options['shadow_window'] = False
from psychopy import event, core, gui, monitors

nowTime=datetime.datetime.now()

###################### Size info ########################
#Our images have to be either 384 or 768 pixels tall ...
# if viewing distance is large, use 768 ... if not, use 384
stimSize = 768
#stimSize = 384

############## If you want to change from left/right arrow #################
responseKeys = ['left', 'right']

###################### Number of images ########################
numImages = 100 # if you want to do fewer than all 100, lower this

################### Timing info ####################
stimDuration=1 #seconds
fixationBaseTime=0.5 #seconds
fixationDelta=0.7 #seconds
responseTimeout=7 #seconds

################### Monitor setup ######################
localMonitors=monitors.getAllMonitors()

################## Subject setup #################
runInfo={'Subject': 'test', 'Run number': 1}
infoDlg=gui.DlgFromDict(dictionary=runInfo,order=['Subject', 'Run number'])
if infoDlg.OK:
    print runInfo
else:
    print 'User cancelled'
    
#file for storing subject responses
if not os.path.exists('response_data'):
    os.makedirs('response_data')
outputFile=os.path.join('response_data', 'FAOT_%s_run%02d_%04d%02d%02d_%02d%02d.txt'%(runInfo['Subject'],runInfo['Run number'],nowTime.year,nowTime.month,nowTime.day,nowTime.hour,nowTime.minute))
subMonitor=monitors.Monitor('testMonitor') # ideally, this is changed to a local, calibrated monitor
screenSize=subMonitor.getSizePix()

################### image files ##########################
#get the list of allimage names
myPath=os.path.dirname(os.path.realpath(__file__))
inputImageFiles=glob.glob(os.path.join(myPath, 'stimuli', '*.png'))
if len(inputImageFiles)==0:
    print('No image files found')
    core.quit()
# pick out 100 to work with 
imageFiles = numpy.random.choice(inputImageFiles, numImages, 0) # random sample without replacement

#################### response recording #####################
#array with 3 columns for image number, response, and response time (reaction time)
responseKeys=['left', 'right']
subjectResponses=numpy.zeros((numImages,3))
quitKeys=['q', 'escape']

################### open a stimulus window #####################
from psychopy import visual #do this here or else it breaks the guidlg
winSub=visual.Window(screenSize,
                     monitor=subMonitor,
                     units='pix',
                     screen=1,
                     color=[0,0,0],
                     colorSpace='rgb',
                     allowGUI=False)

################### create the fixation mark ####################
fixSize=7
fixSquare=visual.Rect(winSub,width=fixSize, height=fixSize,fillColor=[1,1,1],fillColorSpace='rgb',lineColor=[1,1,1],lineColorSpace='rgb',units='pix')

#################### create the image stimulus #####################
imageStim=visual.ImageStim(winSub,image=imageFiles[0],pos=[0,0],size=stimSize,units='pix')

#################### create a gray screen for after stimulus ####################
blankGray=visual.Rect(winSub,width=1024,height=768,fillColor=[0,0,0],fillColorSpace='rgb',lineColor=[0,0,0],lineColorSpace='rgb',units='pix')

##################### Instructions ###############################
instructionMsg=visual.TextStim(winSub,pos=[0,0],text='For each image, decide if you can see a known object. \n\nRespond with Left Arrow for yes and Right Arrow for no. \n\nPress any key to begin.')
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

################ set up task timers ############################
scanTimer=core.Clock()
startTime=scanTimer.getTime()
trialTimer=core.Clock()
trialTime=trialTimer.getTime()
imageTimer=core.Clock()
responseTimer=core.Clock()

################# loop through the images #######################
subjectResponses=[]
for iIm in range(numImages):
    trialStartTime=scanTimer.getTime()-startTime
    trialTimer.reset()
    trialTime=trialTimer.getTime()
    # show the fixation mark
    fixSquare.draw()
    winSub.flip()
    # load the next image
    thisImage=imageFiles[iIm]
    # create the subject response dictionary for this trialDuration
    subjectResponses.append({'image':imageFiles[iIm],'response':None,'time':-9999})
    imageStim.setImage(thisImage)
    # wait to flip until the fixation mark time is done...
    fixJitter=numpy.float(numpy.random.randint(0,fixationDelta*10,1))/10.0
    fixationTime=fixationBaseTime+fixJitter
    while trialTime < fixationTime:
        fixSquare.draw()
        winSub.flip()
        trialTime=trialTimer.getTime()
        for key in event.getKeys():
            if key in quitKeys:
                #save responses
                with open(outputFile,'w') as f:
                    f.write('Image\tResponse\tReactionTime\n')
                    for trial in subjectResponses:
                        f.write('%s\t%s\t%5.3f\n' %(trial['image'],trial['response'],trial['time']))
                core.quit()
    #show the image
    blankGray.draw()
    imageStim.draw()
    #fixSquare.draw()
    winSub.flip()
    event.clearEvents() #clear the keyboard buffer
    imageTimer.reset()
    imageTimer.reset()
    imageTime=imageTimer.getTime()
    responseTimer.reset()
    responseTime=responseTimer.getTime()
    gotResponse=0
    # go to gray screen after 500ms
    while (imageTime<stimDuration) & (gotResponse==0):
        imageStim.draw()
        #fixSquare.draw()
        winSub.flip()
        imageTime=imageTimer.getTime()
        #check for responses until timeout time
        while (responseTime<responseTimeout) & (gotResponse==0):
            responseTime=responseTimer.getTime()
            for key in event.getKeys():
                print key
                if key in quitKeys:
                    #save responses
                    with open(outputFile,'w') as f:
                        f.write('Image\tResponse\tReactionTime\n')
                        for trial in subjectResponses:
                            f.write('%s\t%s\t%5.3f\n' %(trial['image'],trial['response'],trial['time']))
                    core.quit()
                elif key in responseKeys:
                    gotResponse=1
                    subjectResponses[iIm]['image']=imageFiles[iIm]
                    print type(key)
                    if key == responseKeys[0]:
                        subjectResponses[iIm]['response']=1
                    elif key == responseKeys[1]:
                        subjectResponses[iIm]['response']=0
                    subjectResponses[iIm]['time']=imageTimer.getTime()
                    #terminate the trial
                    responseTime=responseTimeout+1
        #if no response, put that in the array
        if gotResponse==0:
            subjectResponses[iIm]['image']=inputImageFiles[iIm]
            subjectResponses[iIm]['response'] = ''
            subjectResponses[iIm]['time']=-999
    #flip a gray screen
    blankGray.draw()
    winSub.flip()
        

#record the responses to a file
with open(outputFile,'w') as f:
    f.write('Image\tResponse\tReactionTime\n')
    for trial in subjectResponses:
        f.write('%s\t%s\t%5.3f\n' %(trial['image'],trial['response'],trial['time']))
thanks=visual.TextStim(winSub,text="Thank you!")
thanks.draw()
winSub.flip()
core.wait(1)
winSub.close()


