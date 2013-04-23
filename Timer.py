import time

class Timer:
   def __init__(self, string):
      self.string = string
      self.start = time.clock()
      #print "Start - %s" % (string)
      
   def stop(self):
      #print "Stop - %s" % (self.string)
      print "\033[92mTime taken for (%s) = %f\033[0m" % (self.string, time.clock() - self.start)
