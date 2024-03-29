#!/usr/bin/python
# -*- coding: utf-8 -*-

#   This file is part of periscope.
#   Copyright (c) 2008-2011 Patrick Dessalle <patrick@dessalle.be>
#
#    periscope is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    periscope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with periscope; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import getopt
import sys, traceback
import os
import shutil
import threading
import logging
from Queue import Queue

import traceback
import ConfigParser

log = logging.getLogger(__name__)

try:
    import xdg.BaseDirectory as bd
    is_local = True
except ImportError:
    is_local = False

import plugins
import version
import locale

SUPPORTED_FORMATS = 'video/x-msvideo', 'video/quicktime', 'video/x-matroska', 'video/mp4'
VERSION = version.VERSION

class Periscope:
    ''' Main Periscope class'''
    
    def __init__(self, cache_folder=None):
        self.config = ConfigParser.SafeConfigParser({"lang": "", "plugins" : "" })        
        self.config_file = os.path.join(cache_folder, "config")
        self.cache_path = cache_folder
        if not os.path.exists(self.config_file):
            folder = os.path.dirname(self.config_file)
            if not os.path.exists(folder):
                log.info("Creating folder %s" %folder)
                os.mkdir(folder)
                log.info("Creating config file")
                configfile = open(self.config_file, "w")
                self.config.write(configfile)
                configfile.close()
        else:
            #Load it
            self.config.read(self.config_file)

        self.pluginNames = self.get_preferedPlugins()
        self._preferedLanguages = None

    def get_preferedLanguages(self):
        ''' Get the prefered language from the config file '''
        configLang = self.config.get("DEFAULT", "lang")
        log.info("lang read from config: " + configLang)
        if configLang == "":
            try :
                l = [locale.getdefaultlocale()[0][:2]]
            except :
                return None
        else:
            return map(lambda x : x.strip(), configLang.split(","))

    def set_preferedLanguages(self, langs):
        ''' Update the config file to set the prefered language '''
        self.config.set("DEFAULT", "lang", ",".join(langs))
        configfile = open(self.config_file, "w")
        self.config.write(configfile)
        configfile.close()

    def get_preferedPlugins(self):
        ''' Get the prefered plugins from the config file '''
        configPlugins = self.config.get("DEFAULT", "plugins")
        if not configPlugins or configPlugins.strip() == "":
            return self.listExistingPlugins()
        else :
            log.info("plugins read from config : " + configPlugins)
            return map(lambda x : x.strip(), configPlugins.split(","))
            
    def set_preferedPlugins(self, newPlugins):
        ''' Update the config file to set the prefered plugins) '''
        self.config.set("DEFAULT", "plugins", ",".join(newPlugins))
        configfile = open(self.config_file, "w")
        self.config.write(configfile)
        configfile.close()
        

    # Getter/setter for the property preferedLanguages
    preferedLanguages = property(get_preferedLanguages, set_preferedLanguages)
    preferedPlugins = property(get_preferedPlugins, set_preferedPlugins)
    
    def deactivatePlugin(self, pluginName):
        ''' Remove a plugin from the list '''
        self.pluginNames -= pluginName
        self.set_preferedPlugins(self.pluginNames)
        
    def activatePlugin(self, pluginName):
        ''' Activate a plugin '''
        if pluginName not in self.listExistingPlugins():
            raise ImportError("No plugin with the name %s exists" %pluginName)
        self.pluginNames += pluginName
        self.set_preferedPlugins(self.pluginNames)
        
    def listActivePlugins(self):
        ''' Return all active plugins '''
        return self.pluginNames
        
    def listExistingPlugins(self):
        ''' List all possible plugins from the plugin folder '''
        return map(lambda x : x.__name__, plugins.SubtitleDatabase.SubtitleDB.__subclasses__())
    
    def listSubtitles(self, filename, langs=None):
        '''Searches subtitles within the active plugins and returns all found matching subtitles ordered by language then by plugin.'''
        #if not os.path.isfile(filename):
            #raise InvalidFileException(filename, "does not exist")
    
        log.info("Searching subtitles for %s with langs %s" %(filename, langs))
        subtitles = []
        q = Queue()
        for name in self.pluginNames:
            try :
                plugin = getattr(plugins, name)(self.config, self.cache_path)
                log.info("Searching on %s " %plugin.__class__.__name__)
                thread = threading.Thread(target=plugin.searchInThread, args=(q, filename, langs))
                thread.start()
            except ImportError :
                log.error("Plugin %s is not a valid plugin name. Skipping it.")        

        # Get data from the queue and wait till we have a result
        for name in self.pluginNames:
            subs = q.get(True)
            if subs and len(subs) > 0:
                if not langs:
                    subtitles += subs
                else:
                    for sub in subs:
                        if sub["lang"] in langs:
                            subtitles += [sub] # Add an array with just that sub
            
        if len(subtitles) == 0:
            return []
        return subtitles
    
    
    def selectBestSubtitle(self, inputSubtitles, langs=None, maxTotalNumber=None, maxNumberPerPlugin=None):
        '''Searches inputSubtitles from plugins and returns the best inputSubtitles from all candidates'''   
        '''Input subtitles are sorter by plugin and language'''
        outputSubtitles = []
        if maxTotalNumber is None and maxNumberPerPlugin is None:
            maxTotalNumber = 1
        if not inputSubtitles:
            return None
        if maxNumberPerPlugin is None:
            if langs is None:  
                outputSubtitles = self.filterByMaxNumber(inputSubtitles, maxTotalNumber)
            else:
                for language in langs:
                    languageFiltered = self.filterByLanguages([language], inputSubtitles)
                    languageAndMaxTotalNumberFiltered = self.filterByMaxNumber(languageFiltered, maxTotalNumber)
                    outputSubtitles.extend(languageAndMaxTotalNumberFiltered)
        else:
            if langs is None:
                for pluginName in self.listActivePlugins():
                    pluginFiltered = self.filterByPluginName([pluginName], inputSubtitles)
                    pluginAndMaxTotalNumberFiltered = self.filterByMaxNumber(pluginFiltered, maxNumberPerPlugin)
                    if pluginAndMaxTotalNumberFiltered is not None and len(pluginAndMaxTotalNumberFiltered) > 0:
                        outputSubtitles.extend(pluginAndMaxTotalNumberFiltered)
            else:
                for language in langs:
                    languageFiltered = self.filterByLanguages([language], inputSubtitles)
                    for pluginName in self.listActivePlugins():
                        pluginFiltered = self.filterByPluginName([pluginName], languageFiltered)
                        pluginAndMaxNumberPerPluginFiltered = self.filterByMaxNumber(pluginFiltered, maxNumberPerPlugin)
                        if pluginAndMaxNumberPerPluginFiltered is not None and len(pluginAndMaxNumberPerPluginFiltered) > 0:
                            outputSubtitles.extend(pluginAndMaxNumberPerPluginFiltered)
        return outputSubtitles
    
    def filterByPluginName(self, pluginNames, inputSubtitles):
        log.debug("Filtering by plug-in names %s" %pluginNames)
        outputSubtitles = []
        if inputSubtitles is None or len(inputSubtitles) == 0:
            return None
        if pluginNames is None or len(pluginNames) == 0:
            return None
        for subtitle in inputSubtitles:
            pluginName = subtitle["plugin"].__class__.__name__ 
            if(pluginName in pluginNames):
                outputSubtitles.append(subtitle)
        log.debug("Filtering by plugin %s result(s)." %len(outputSubtitles))
        return outputSubtitles
    
    def filterByMaxNumber(self, inputSubtitles, maxNumber):
        log.debug("Filtering by max number %s" %maxNumber)
        outputSubtitles = []
        if inputSubtitles is None or len(inputSubtitles) == 0:
            return None
        if maxNumber <= 0:
            return None
        maxIndex = maxNumber
        if len(inputSubtitles) < maxNumber:
            log.debug("len %s" % len(inputSubtitles).__class__.__name__)
            log.debug("max %s" % maxNumber.__class__.__name__)
            log.debug("%s < %s" % (len(inputSubtitles), maxNumber))
            maxIndex = len(inputSubtitles) 
        log.debug("Max index set to %s" %maxIndex)
        outputSubtitles = inputSubtitles[:maxIndex]
        log.debug("Filtering by max number %s result(s)." %len(outputSubtitles))
        return outputSubtitles
        
    def filterByLanguages(self, languages, inputSubtitles):
        log.debug("Filtering by languages %s" %languages)
        outputSubtitles = []
        if inputSubtitles == None or len(inputSubtitles) == 0:
            return None
        if languages is None or len(languages) == 0:
            return None
        for subtitle in inputSubtitles:
            if(subtitle["lang"] in languages):
                outputSubtitles.append(subtitle)
        log.debug("Filtering by languages %s result(s)." %len(outputSubtitles))
        return outputSubtitles

    def downloadSubtitle(self, filename, langs=None, maxTotalNumber=None, maxNumberPerPlugin=None):
        ''' Takes a filename and a language and creates ONE subtitle through plugins'''
        subtitles = self.listSubtitles(filename, langs)
        if subtitles:
            log.debug("All subtitles: ")
            log.debug(subtitles)    
            return self.attemptDownloadSubtitle(subtitles, langs, maxTotalNumber, maxNumberPerPlugin)
        else:
            return None
        
        
    def attemptDownloadSubtitle(self, foundedSubtitles, langs=None, maxTotalNumber=None, maxNumberPerPlugin=None):
        selectedSubtitles = self.selectBestSubtitle(foundedSubtitles, langs, maxTotalNumber, maxNumberPerPlugin)
        downloadedSubtitles = []
        indexPerPlugin = {}
        isFirstSubtitle = True
        firstSubtitle = None
        if selectedSubtitles is None or len(selectedSubtitles) == 0:
            log.error("No subtitles could be chosen.")
            return None
        for subtitle in selectedSubtitles:
            pluginName = subtitle["plugin"].__class__.__name__            
            if pluginName not in indexPerPlugin:
                indexPerPlugin[pluginName] = 1
            else:
                indexPerPlugin[pluginName] += 1 
            log.info("Trying to download subtitle: %s number: %s" % (subtitle['link'], indexPerPlugin[pluginName]))
            #Download the subtitle
            try:                
                tempSubtitleName = subtitle["plugin"].createFile(subtitle)        
                if tempSubtitleName:
                    uniqueSubtitleName = self.generateUniqueSubtitleName(indexPerPlugin[pluginName], subtitle)
                    self.renameSubtitle(tempSubtitleName, uniqueSubtitleName)
                    subtitle["subtitlepath"] = uniqueSubtitleName
                    downloadedSubtitles.append(subtitle)
                    # in case if this is first subtitle then copy to basic name for back compatibility
                    if(isFirstSubtitle):                        
                        isFirstSubtitle = False
                        firstSubtitle = subtitle                                                                         
                else:
                    # throw exception to remove it
                    raise Exception("Not downloaded")            
            except Exception as inst:
                # Could not download that subtitle, remove it
                log.warn("Subtitle %s could not be downloaded, trying the next on the list" %subtitle['link'])
                log.error(inst)
                foundedSubtitles.remove(subtitle)
                return self.attemptDownloadSubtitle(foundedSubtitles, langs, maxTotalNumber, maxNumberPerPlugin)
        if(firstSubtitle):
            try:
                log.debug("Subtitle: %s is first on the list, copying to basic name." % firstSubtitle["subtitlepath"])
                genericSubtitleName = self.generateBasicSubtitleName(firstSubtitle)
                self.copySubtitle(firstSubtitle["subtitlepath"], genericSubtitleName)                
            except Exception as inst:
                log.error(inst)
        return downloadedSubtitles
                    
    def generateUniqueSubtitleName(self, index, subtitle):
        videoFileName = subtitle["filename"]
        subtitleBaseName = videoFileName.rsplit(".", 1)[0]
        pluginName = subtitle["plugin"].__class__.__name__
        language = subtitle["lang"]
        extension = "srt"
        subtitleFullName = "%s.%s_%s_%s.%s" % (subtitleBaseName, pluginName, language, index, extension) 
        log.debug("Generated unique subtitle name %s" % subtitleFullName)
        return subtitleFullName
    
    def generateBasicSubtitleName(self, subtitle):
        log.debug("Input name: %s" % subtitle)
        videoFileName = subtitle["filename"]
        log.debug("Video file core name: %s" % videoFileName)
        subtitleBaseName = videoFileName.rsplit(".", 1)[0]
        log.debug("Subtitle base name: %s" % subtitleBaseName)
        extension = "srt"
        subtitleFullName = "%s.%s" % (subtitleBaseName, extension)
        log.debug("Generated basic subtitle name %s" % subtitleFullName)
        return subtitleFullName
    
    def renameSubtitle(self, oldName, newName):
        log.debug("Renaming file: %s to: %s" % (oldName, newName))
        try:            
            os.rename(oldName, newName)            
            return newName
        except OSError as (errno, strerror):
            log.error("Error %s while renaming file from %s to %s" % (strerror, oldName, newName))
            raise   
    
    def copySubtitle(self, srcFile, dstFile):
        log.debug("Copying file: %s to: %s" % (srcFile, dstFile))
        try:            
            shutil.copy2(srcFile, dstFile)
            log.debug("File copied successfully to: %s, size: %s, location: %s " % (dstFile, os.path.getsize(dstFile), os.path.abspath(dstFile)))            
            return dstFile
        except IOError as (errno, strerror):
            log.error("IOError error %s while copying file from %s to %s" % (strerror, srcFile, dstFile))        
            raise
        except Exception as inst:
            log.error("Exception %s while copying file from %s to %s" % (inst, srcFile, dstFile))            
            raise
    
    def guessFileData(self, filename):
        subdb = plugins.SubtitleDatabase.SubtitleDB(None)
        return subdb.guessFileData(filename)        
        
    def __orderSubtitles__(self, subs):
        '''reorders the subtitles according to the languages then the website'''
        try:
            from collections import defaultdict
            subtitles = defaultdict(list) #Order matters (order of plugin and result from plugins)
            for s in subs:
                subtitles[s["lang"]].append(s)
            return subtitles
        except ImportError, e: #Don't use Python 2.5
            subtitles = {}
            for s in subs:
                # return subtitles[s["lang"]], if it does not exist, set it to [] and return it, then append the subtitle
                subtitles.setdefault(s["lang"], []).append(s)
            return subtitles
