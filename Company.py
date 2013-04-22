class Company:
   def __init__(self, key, name):
      self.key = key
      self.name = name
      
   def __hash__(self):
      return hash(self.key)
   def __eq__(self, other):
      return self.key == other.key
   
   def getKey(self):
      return self.Key
   def getName(self):
      return self.name
