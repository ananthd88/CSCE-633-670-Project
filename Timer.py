import time


class Timer:
   """Class to time function calls - Counts the CPU time used"""
   # Start the timer
   def __init__(self, string):
      self.string = string
      self.start = time.clock()
      self.time  = 0.0
   
   def start(self, string):
      self.string = string
      self.start = time.clock()
      self.time  = 0.0
   def stop(self):
      """"Print the CPU secs used"""
      if self.start:
         print "\033[92mTime taken for (%s) = %f\033[0m" % (self.string, time.clock() - self.start + self.time)
      else:
         print "\033[92mTime taken for (%s) = %f\033[0m" % (self.string, self.time)
      self.string = None
      self.start = None
      self.time = None
      
   def pause(self):
      if self.start:
         self.time += time.clock() - self.start
         self.start = None
   def unpause(self):
      if not self.start:
         self.start = time.clock()
