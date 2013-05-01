import wx
import PayMaster
import sys
import re
import Collection

class DemoPanel(wx.Panel):

   def __init__(self, parent,inputfile, *args, **kwargs):
      wx.Panel.__init__(self, parent, *args, **kwargs)
      self.parent = parent
     
      self.setTextBoxs()
      self.setLabels()
      self.setComboBoxs()
      self.setButtons() 

      Sizer = self.setLayout()
      self.SetSizerAndFit(Sizer)

      self.regressorDict = {"":"UWR","K Nearest Neighbours":"KNR","SVM":"SVR","RandomForest":"RFR"}
      self.classifierDict = {"Naive Bayes":"NBC","SVM":"SVC"}
      self.inputfile = inputfile
      self.payMaster = PayMaster.PayMaster(self.inputfile,(str)(self.categoryComboBox.GetValue()).lower())
      self.testCollection = Collection.Collection("Online")

   #Event Handling
   def OnTrain(self, event=None):
   #Bring up a wx.MessageDialog with a useless message.
      

      s = self.featureTextBox.GetValue()
      classifier = self.classifierComboBox.GetValue()
      regressor = self.regressorComboBox.GetValue()
      
      if s.isdigit() and int(s) > 0 and (classifier != "" or regressor != ""):
         features = int(s)
         self.refresh()
          
         self.payMaster.refresh((str)(self.categoryComboBox.GetValue()).lower())
         
         if self.classifierComboBox.GetValue() != "":
            self.payMaster.train(False,self.classifierDict.get(classifier),self.regressorDict.get(regressor), features, features)
         else:
            self.payMaster.train(True,None,self.regressorDict.get(regressor), features, features)

         self.meanCategoryTextBox.SetValue(str(self.payMaster.getMeanSalary()))
         self.sdCategoryTextBox.SetValue(str(self.payMaster.getStdDeviationSalary()))
         
         dlg = wx.MessageDialog(self, message='Training done', caption='Information', style=wx.OK)
         dlg.ShowModal()
         dlg.Destroy()

      else:
         dlg = wx.MessageDialog(self, message='Please select the number of features', caption='Error', style=wx.OK)
         dlg.ShowModal()
         dlg.Destroy()


   def OnLoad(self, event = None):
   #Load a new Advertisement
      self.document = self.payMaster.getNextDocument()     
      if (self.document):
         self.actSalaryTextBox.SetValue(str(self.document.getSalary()))
         self.adTextBox.SetValue("Title:" + ' '.join(self.document.getTitle()) + 
                                 '\nDescription:' + ' '.join(self.document.getDescription()) + 
                                 '\nCompany:' + self.document.getCompany().getName() + 
                                 '\nLocation:' + ' '.join(self.document.getLocation())
                                  )
      
      else:
         dlg = wx.MessageDialog(self, 
                                message='All Ads tested in the Test Set.Please select a new category', 
                                caption='Information', 
                                style=wx.OK|wx.ICON_INFORMATION)
         dlg.ShowModal()
         dlg.Destroy() 
 

   def OnPredictNext(self, event=None):
   #Predict the salary for the current ad.
      if (self.adTextBox.GetValue() != ""):
           
         self.document = self.payMaster.getNextDocument()
         strings = self.adTextBox.GetValue() 
         document = self.testCollection.addDocument(self.createDocumentDictionary(strings))
         print document
         predictedSalary = self.payMaster.predict(document)
         self.predictSalaryTextBox.SetValue(str(predictedSalary))
         self.errorTextBox.SetValue(str(predictedSalary - self.document.getSalary()))
         self.runningMeanTextBox.SetValue(str(self.payMaster.getMean()))
            

      else:
         dlg = wx.MessageDialog(self,
                                message='Please Enter the Advertisement', 
                                caption='Information', 
                                style=wx.OK|wx.ICON_INFORMATION
                                )
         dlg.ShowModal()
         dlg.Destroy()


   def OnPredictAll(self, event=None):
   #Get the next advertisement.
      self.payMaster.resetStats()
      self.payMaster.predictAll()
      self.refresh()
      self.runningMeanTextBox.SetValue(str(self.payMaster.getMean()))
 

   def createDocumentDictionary(self, strings=""):
   #creates a new document with the specified Ad
      dictionary = {}
      list_of_strings = re.split("\n",strings)
      
      dictionary["Title"]            = re.split('Title:',list_of_strings[0])[1]
      dictionary["FullDescription"]  = re.split('Description:',list_of_strings[1])[1]
      dictionary["LocationRaw"]      = re.split('Location:',list_of_strings[3])[1]
      dictionary["Category"]         = self.categoryComboBox.GetValue().lower()
      dictionary["Company"]          = re.split('Company:',list_of_strings[2])[1]
      dictionary["SalaryNormalized"] = self.actSalaryTextBox.GetValue()
      print dictionary
      return dictionary

   
   #All GUI initialisation starts
   def setLabels(self):
   #Initialise all the labels
      self.categoryLabel       = wx.StaticText(self, label = "Category") 
      self.adLabel             = wx.StaticText(self, label = "Advertisement")
      self.actSalaryLabel      = wx.StaticText(self, label = "Actual Salary")
      self.predictSalaryLabel  = wx.StaticText(self, label = "Predicted Salary")
      self.runningMeanLabel    = wx.StaticText(self, label = "Running Mean")
      self.errorLabel          = wx.StaticText(self, label = "Absolute Error")
      self.classifierLabel     = wx.StaticText(self, label = "Classifier") 
      self.regressorLabel      = wx.StaticText(self, label = "Regressor")
      self.meanLabel           = wx.StaticText(self, label = "Mean")
      self.sdLabel             = wx.StaticText(self, label = "Standard Deviation")
      self.featuresLabel       = wx.StaticText(self, label = "Features")
      


   def setTextBoxs(self):
   #Initialize all the TextBoxs
      self.adTextBox            = wx.TextCtrl(self, size = (600,200), style = wx.TE_MULTILINE )
      self.actSalaryTextBox     = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.predictSalaryTextBox = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.runningMeanTextBox   = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.errorTextBox         = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.meanCategoryTextBox  = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.sdCategoryTextBox    = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.featureTextBox       = wx.TextCtrl(self)
      self.featureTextBox.SetValue("100")



   def setButtons(self):
   #Initialise all the Buttons 
      self.trainButton = wx.Button(self, label = "Train")
      self.trainButton.Bind(wx.EVT_BUTTON, self.OnTrain)
      self.predictButton = wx.Button(self, label = "Predict Ad")
      self.predictButton.Bind(wx.EVT_BUTTON, self.OnPredictNext)
      self.predictAllButton = wx.Button(self, label = "Predict All")
      self.predictAllButton.Bind(wx.EVT_BUTTON, self.OnPredictAll)
      self.loadAdButton = wx.Button(self, label = "Load Ad")
      self.loadAdButton.Bind(wx.EVT_BUTTON, self.OnLoad)
   

   def setComboBoxs(self):
   #Initialise all the ComboBoxs     
      category_list = ["Part Time Jobs","Engineering Jobs","Legal Jobs","Healthcare & Nursing Jobs","Graduate Jobs","Social Work Jobs"]
      classifiers = ["","Naive Bayes","SVM"]
      regressors = ["","K Nearest Neighbours","SVM","RandomForest"]
      self.categoryComboBox   = wx.ComboBox(self,style = wx.CB_READONLY, choices = category_list)
      self.categoryComboBox.SetValue("Part Time Jobs")
      self.classifierComboBox = wx.ComboBox(self,style = wx.CB_READONLY, choices = classifiers)
      self.classifierComboBox.SetValue("Naive Bayes")
      self.regressorComboBox  = wx.ComboBox(self,style = wx.CB_READONLY, choices = regressors)
      self.regressorComboBox.SetValue("RandomForest")


   def setLayout(self):
   #SetLayout for the Panel
     # firstRow = initFirstRowLayout(self)
      firstRow = wx.GridBagSizer(hgap = 5,vgap = 5)
      firstRow.Add(self.categoryLabel,flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (0,0),border = 5)
      firstRow.Add(self.categoryComboBox,flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (0,1) ,border = 5)
      firstRow.Add(self.featuresLabel,flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (0,2),border = 5)
      firstRow.Add(self.featureTextBox,flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (0,3),border = 5)
      firstRow.Add(self.classifierLabel, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (1,0), border = 5)
      firstRow.Add(self.classifierComboBox, flag = wx.ALL , pos = (1,1), border = 5)
      firstRow.Add(self.regressorLabel, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (1,2), border = 5)
      firstRow.Add(self.regressorComboBox, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (1,3), border = 5)
      firstRow.Add(self.trainButton, flag = wx.ALL,pos = (1,4), border = 5)

      middleRow = wx.GridBagSizer(hgap = 25, vgap = 5)
      middleRow.Add(self.adLabel, pos = (0,0))
      middleRow.Add(self.loadAdButton, pos = (0,1))
      middleRow.Add(self.predictButton, pos = (0,2))
      middleRow.Add(self.predictAllButton, pos = (0,3))
      middleRow.Add(self.adTextBox, pos = (1,0), span = (1,4),flag = wx.BOTTOM | wx.EXPAND, border = 5)

      bottomRow = wx.BoxSizer(wx.HORIZONTAL)
      bottomRow.Add(self.meanLabel, 0, wx.ALL| wx.ALIGN_CENTER_HORIZONTAL , 5)
      bottomRow.Add(self.meanCategoryTextBox, 0, wx.ALL| wx.ALIGN_CENTER_HORIZONTAL, 5)
      bottomRow.Add(self.sdLabel, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
      bottomRow.Add(self.sdCategoryTextBox, 0, wx.ALL| wx.ALIGN_CENTER_HORIZONTAL, 5)
     
      rightColumn = wx.BoxSizer(wx.VERTICAL)
      rightColumn.Add(self.actSalaryLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.actSalaryTextBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.predictSalaryLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.predictSalaryTextBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.errorLabel, 0 ,wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.errorTextBox, 0 ,wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.runningMeanLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.runningMeanTextBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
	
     
      Adjuster = wx.BoxSizer(wx.VERTICAL)
      Adjuster.Add(middleRow, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL)
      Adjuster.Add(bottomRow, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL) 
      Sizer = wx.GridBagSizer(hgap = 15, vgap = 15)
      Sizer.Add(firstRow, pos = (0,0))#, span = (0,5), flag = wx.EXPAND)
      Sizer.Add(Adjuster,pos = (1,0))#, span = (5,4))
      Sizer.Add(rightColumn, pos = (1,1))#, span = (5,5))
      
      return Sizer

   
	
   def refresh(self):
   #Refreshes the whole data
      self.adTextBox.SetValue("")
      self.actSalaryTextBox.SetValue("")
      self.predictSalaryTextBox.SetValue("")
      self.runningMeanTextBox.SetValue("")
      self.errorTextBox.SetValue("")



class DemoFrame(wx.Frame):
#Main Frame holding the Panel.
   def __init__(self, inputfile,  *args, **kwargs):
   #Create the DemoFrame.
      wx.Frame.__init__(self, *args, **kwargs)

      # Build the menu bar
      MenuBar = wx.MenuBar()
      FileMenu = wx.Menu()

      item = FileMenu.Append(wx.ID_EXIT, text="&Quit")
      self.Bind(wx.EVT_MENU, self.OnQuit, item)

      MenuBar.Append(FileMenu, "&File")
      self.SetMenuBar(MenuBar)

      # Add the Widget Panel
      self.Panel = DemoPanel(self,inputfile)

      self.Fit()
   
   def OnQuit(self, event=None):
   #Exit application.
      self.Close()
  
if __name__ == '__main__':
    app = wx.App()
    if len(sys.argv) > 1:
    	inputfile = sys.argv[1]
    	frame = DemoFrame(inputfile,None, title="The Pay Master")
    	frame.Show()
    	app.MainLoop()
    else:
        print "Please pass the correct filename as the argument"
