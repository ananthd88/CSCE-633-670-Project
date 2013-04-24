import time


class Timer:
   """Class to time function calls - Counts the CPU time used"""
   # Start the timer
   def __init__(self, string):
      self.string = string
      self.start = time.clock()
   
   def stop(self):
      """"Print the CPU secs used"""
      print "\033[92mTime taken for (%s) = %f\033[0m" % (self.string, time.clock() - self.start)
