#!/usr/bin/python

import wx
import PayMaster
import sys

class DemoPanel(wx.Panel):

   def __init__(self, parent,inputfile, *args, **kwargs):
      wx.Panel.__init__(self, parent, *args, **kwargs)
      self.parent = parent
     
      categoryLabel       = wx.StaticText(self, label = "Category") 
      actSalaryLabel      = wx.StaticText(self, label = "Actual Salary")
      predictSalaryLabel  = wx.StaticText(self, label = "Predicted Salary")
      runningMeanLabel    = wx.StaticText(self, label = "Running Mean")
      errorLabel          = wx.StaticText(self, label = "Absolute Error")
      adLabel             = wx.StaticText(self, label = "Advertisement")
      classifierLabel     = wx.StaticText(self, label = "Classifier") 
      regressorLabel      = wx.StaticText(self, label = "Regressor")
      meanLabel           = wx.StaticText(self, label = "Mean")
      sdLabel             = wx.StaticText(self, label = "Standard Deviation")
      featuresLabel       = wx.StaticText(self, label = "Features")
      
      self.adTextBox            = wx.TextCtrl(self, size = (600,200), style = wx.TE_MULTILINE | wx.TE_READONLY )

      self.actSalaryTextBox     = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.predictSalaryTextBox = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.runningMeanTextBox   = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.errorTextBox         = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.meanCategoryTextBox  = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.sdCategoryTextBox    = wx.TextCtrl(self, style = wx.TE_READONLY)
      self.featureTextBox       = wx.TextCtrl(self)
      #TODO : Remember to check for zero features or parse for numbers      

      self.trainButton = wx.Button(self, label = "Train")
      self.trainButton.Bind(wx.EVT_BUTTON, self.OnTrain)
      self.predictButton = wx.Button(self, label = "Predict")
      self.predictButton.Bind(wx.EVT_BUTTON, self.OnPredict)
      self.nextAdButton = wx.Button(self, label = "Next Ad")
      self.nextAdButton.Bind(wx.EVT_BUTTON, self.OnNextAd)
       
      category_list = ["Part Time Jobs","Engineering Jobs"]
      classifiers = ["","Naive Bayes","SVM"]
      regressors = ["","K Nearest Neighbours","SVM","RandomForest"]
      self.categoryComboBox   = wx.ComboBox(self,style = wx.CB_READONLY, choices = category_list)
      self.classifierComboBox = wx.ComboBox(self,style = wx.CB_READONLY, choices = classifiers)
      self.regressorComboBox  = wx.ComboBox(self,style = wx.CB_READONLY, choices = regressors)

      firstRow = wx.GridBagSizer(hgap = 5,vgap = 5)
      firstRow.Add(categoryLabel,flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (0,0),border = 5)
      firstRow.Add(self.categoryComboBox,flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (0,1) ,border = 5)
      firstRow.Add(featuresLabel,flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (0,2),border = 5)
      firstRow.Add(self.featureTextBox,flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (0,3),border = 5)
      firstRow.Add(classifierLabel, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (1,0), border = 5)
      firstRow.Add(self.classifierComboBox, flag = wx.ALL , pos = (1,1), border = 5)
      firstRow.Add(regressorLabel, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (1,2), border = 5)
      firstRow.Add(self.regressorComboBox, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, pos = (1,3), border = 5)
      firstRow.Add(self.trainButton, flag = wx.ALL,pos = (1,4), border = 5)

      middleRow = wx.GridBagSizer(hgap = 25, vgap = 5)
      middleRow.Add(adLabel, pos = (0,0))
      middleRow.Add(self.nextAdButton, pos = (0,1))
      middleRow.Add(self.predictButton, pos = (0,2))
      middleRow.Add(self.adTextBox, pos = (1,0), span = (1,3),flag = wx.BOTTOM | wx.EXPAND, border = 5)

      bottomRow = wx.BoxSizer(wx.HORIZONTAL)
      bottomRow.Add(meanLabel, 0, wx.ALL| wx.ALIGN_CENTER_HORIZONTAL , 5)
      bottomRow.Add(self.meanCategoryTextBox, 0, wx.ALL| wx.ALIGN_CENTER_HORIZONTAL, 5)
      bottomRow.Add(sdLabel, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
      bottomRow.Add(self.sdCategoryTextBox, 0, wx.ALL| wx.ALIGN_CENTER_HORIZONTAL, 5)
     
      rightColumn = wx.BoxSizer(wx.VERTICAL)
      rightColumn.Add(actSalaryLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.actSalaryTextBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(predictSalaryLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.predictSalaryTextBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(errorLabel, 0 ,wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.errorTextBox, 0 ,wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(runningMeanLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
      rightColumn.Add(self.runningMeanTextBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
	
     
      Adjuster = wx.BoxSizer(wx.VERTICAL)
      Adjuster.Add(middleRow, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL)
      Adjuster.Add(bottomRow, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL) 
      Sizer = wx.GridBagSizer(hgap = 15, vgap = 15)
      Sizer.Add(firstRow, pos = (0,0))#, span = (0,5), flag = wx.EXPAND)
      Sizer.Add(Adjuster,pos = (1,0))#, span = (5,4))
      Sizer.Add(rightColumn, pos = (1,1))#, span = (5,5))
      
      self.SetSizerAndFit(Sizer)

      self.regressorDict = {"":"UWR","K Nearest Neighbours":"KNR","SVM":"SVR","RandomForest":"RFR"}
      self.classifierDict = {"Naive Bayes":"NBC","SVM":"SVC"}
      self.inputfile = inputfile
      


  
   def OnTrain(self, event=None):
   #Bring up a wx.MessageDialog with a useless message.
      

      s = self.featureTextBox.GetValue()
      classifier = self.classifierComboBox.GetValue()
      regressor = self.regressorComboBox.GetValue()
      
      if s.isdigit() and int(s) > 0 and (classifier != "" or regressor != ""):
         features = int(s)
         self.refresh()
          
         self.payMaster = PayMaster.PayMaster(self.inputfile,(str)(self.categoryComboBox.GetValue()).lower())
         
         if self.classifierComboBox.getValue() != "":
            self.payMaster.train(False,self.classifierDict.get(classifier),self.regressorDict.get(regressor), features, features)
         else:
            self.payMaster.train(True,None,self.regressorDict.get(regressor), features, features)

         self.meanCategoryTextBox  = self.payMaster.getMean()
         self.sdCategoryTextBox    = self.payMaster.getStdDeviation()

      else:
         dlg = wx.MessageDialog(self, message='Please select the number of features', caption='Error', style=wx.OK)
         dlg.ShowModal()
         dlg.Destroy()


         
   def OnPredict(self, event=None):
   #Predict the salary for the current ad.
        print "came here" 
   
   def OnNextAd(self, event=None):
   #Get the next advertisement.
      if (self.payMaster.getNextDocument()):
         document = self.payMaster.getNextDocument()
         self.actSalaryTextBox.setValue(document.getSalaryNorm())
         self.adTextBox.setValue("Title:" + ' '.join(document.getTitle()) + '\nDescription:' + ' '.join(document.getDescription()) + '\nCompany:' + document.getCompany() + '\nLocation:' + document.getRawLocation())
      else:
         dlg = wx.MessageDialog(self, message='All documents tested.Please select a new category', caption='Information', style=wx.OK|wx.ICON_INFORMATION)
         dlg.ShowModal()
         dlg.Destroy()
  	
	
   def refresh(self):
   #Refreshes the whole data
      self.adTextBox            = ""
      self.actSalaryTextBox     = ""
      self.predictSalaryTextBox = ""
      self.runningMeanTextBox   = ""
      self.errorTextBox         = ""


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
    	inputfile = open(sys.argv[1], 'rt')
    frame = DemoFrame(inputfile,None, title="The Pay Master")
    frame.Show()
    app.MainLoop()
