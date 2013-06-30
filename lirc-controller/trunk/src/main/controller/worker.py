'''
Created on 8 May 2013

@author: abednarski
'''
import logging

class Job:
    
    def __init__(self, buttonId, actionType):
        self.buttonId = buttonId
        self.actionType = actionType
    
    def __str__(self):
        return self.buttonId + ", " + self.actionType
    
        
class Worker:
    
    def __init__(self, configuration, workerQueue):
        self.workerQueue = workerQueue
        self.mapping = configuration.buttons
        self.cache = configuration.cache
        self.logger = logging.getLogger("worker")
    
    def loop(self):
        self.logger.info("Starting up.")
        while True:
            job = self.workerQueue.get()
            if job is None:
                self.logger.info("Shutting down.")
                break            
            self.onEvent(job)        
    
    def onEvent(self, job):
        cacheKey = job.taskUniqueKey()
        self.logger.info("Searching for method at: %s" % cacheKey)
        if cacheKey not in self.cache:
            self.logger.error("No task with id: %s in cache: %s" % cacheKey, self.cache);
            return        
        self.logger.info("Cache contains method: %s" % cacheKey)
        method = self.cache[cacheKey]
        if method is None:
            self.logger.error("Method is missing: %s" % cacheKey)
            return
        self.logger.debug("Method is populated: %s" % cacheKey)
        try:
            method(job.parameter)
        except Exception as details:
            self.logger.error("Can't run method %s, details: %s" % (cacheKey, details))
    
    def shutdown(self):        
        self.workerQueue.put_nowait(None)
            