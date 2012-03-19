'''
Created on 11 Mar 2012

@author: abednarski
'''
from controller.Configuration import Configuration, Button, Action
from controller.Processor import Processor
import time
import unittest



class ProcessorTest(unittest.TestCase):
        

    def setUp(self):
        print "Setup processor"
        gapDuration = 0.5
        # button - PLUS
        plusAction = Action("plus-action", isCancelable = False)
        self.plusButton = Button("PLUS-BUTTON", plusAction, plusAction, plusAction)                
        # button - MENU
        globalModeAction = Action("global-menu", fireDelay = gapDuration)
        currentMenuAction = Action ("current-menu-action", minimalRepeatTrigger = 1)
        self.menuButton = Button("MENU-BUTTON", globalModeAction, globalModeAction, currentMenuAction)
        # button - FORWARD
        nextSongAction = Action("next-song-action", fireDelay = gapDuration)
        nextAlbumAction = Action("next-album-action", fireDelay = gapDuration)
        nextPlaylistAction = Action("next-playlist-action", minimalRepeatTrigger = 1)
        self.forwardButton = Button("FORWARD-BUTTON", nextSongAction, nextAlbumAction, nextPlaylistAction)
        # button - PLAY
        playPauseAction = Action("play-pause-action", fireDelay = gapDuration)
        powerOffAction = Action("power-off", minimalRepeatTrigger = 5)
        self.playButton = Button("PLAY-BUTTON", playPauseAction , playPauseAction, powerOffAction)
        # configuration
        buttons = (self.plusButton, self.menuButton, self.forwardButton, self.playButton)        
        self.configuration = Configuration(gapDuration, buttons)
        # processor        
        self.processor = Processor(self.configuration)


    def tearDown(self):
        self.processor= None
        self.configuration = None


    def clickButton(self, button, repeat):
        self.processor.preProcess(button.key, repeat)
        print "Sleeping for %s before finishing current click ..." % (self.configuration.gapDuration)
        time.sleep(self.configuration.gapDuration)
        print "Done"
            
    def XtestPlusButtonClick(self):
        currentActionList = []
        self.clickButton(self.plusButton, 0)
        currentActionList.append(self.plusButton.click.action)
        self.assertEqual(self.processor.executionQueue, currentActionList);
                             
    def XtestPlusButtonDoubleClick(self):
        currentActionList = []
        self.clickButton(self.plusButton, 0)
        currentActionList.append(self.plusButton.click.action)
        self.clickButton(self.plusButton, 0)
        currentActionList.append(self.plusButton.doubleClick.action)
        self.assertEqual(self.processor.executionQueue, currentActionList);        
    
    def XtestPlusButtonLongClick(self):
        currentActionList = []
        self.clickButton(self.plusButton, 0)
        currentActionList.append(self.plusButton.click.action)
        self.clickButton(self.plusButton, 1)
        currentActionList.append(self.plusButton.hold.action)
        self.clickButton(self.plusButton, 2)
        currentActionList.append(self.plusButton.hold.action)
        self.assertEqual(self.processor.executionQueue, currentActionList);  
            
    def testForwardButtonClick(self):
        currentActionList = []
        self.clickButton(self.forwardButton, 0)
        currentActionList.append(self.forwardButton.click.action)
        self.assertEqual(self.processor.executionQueue, currentActionList);
    
    def XtestForwardButtonDoubleClick(self):
        currentActionList = []
        self.clickButton(self.forwardButton, 0)        
        self.clickButton(self.forwardButton, 0)
        currentActionList.append(self.forwardButton.doubleClick.action)        
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only next album action");

    def XtestForwardButtonLongClick(self):
        currentActionList = []
        self.clickButton(self.forwardButton, 0)        
        self.clickButton(self.forwardButton, 1)
        currentActionList.append(self.forwardButton.hold.action)        
        self.assertEqual(self.processor.executionQueue, currentActionList, "Should contain only next playlist action");


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test1ClickCommand']
    unittest.main()