"""Subclass of MainFrameBase, which is generated by wxFormBuilder."""

import wx
import wx.calendar as cal
import gui
import src.resources.finance as fin
import src.resources.utilities as u
import numpy as num
import matplotlib.dates as mdates
import matplotlib.backends.backend_wxagg as mpl
import time
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import matplotlib.pyplot as plt
from operator import itemgetter

# Implementing MainFrameBase
class MainFrame( gui.MainFrameBase ):
	def __init__( self, parent, portfolio ):
		gui.MainFrameBase.__init__( self, parent )
		self.portfolio = portfolio
		self.m_stocklist.InsertColumn(0, '')
	# Handlers for MainFrameBase events.
	def startDateChanged( self, event ):
		# TODO: Implement startDateChanged
		pass
	
	def stockSelected( self, event ):
		sym = self.m_stocklist.GetItemText(event.m_itemIndex).encode('ascii')
		for s in self.portfolio.assets:
			if s.symbol == sym:
				stock = s
				break
		prices = [(date, price.adjclosing) for date,price in stock.prices.iteritems() if date >= self.portfolio.startdate]
		
		prices = sorted(prices, key=itemgetter(0), reverse=True)
		
		data = zip(*prices)
		
		plt.figure(1)
		plt.subplot(111)
		plt.plot_date(data[0], data[1], '-', xdate=True)
		plt.ylabel("Market Value")
		plt.title(stock.symbol)
		plt.show()
	
	def m_addButtonClick( self, event ):
		
		"""Parse the text in the input box"""
		stockstr = self.m_symbolinput.Value.encode('ascii')
		stocks = stockstr.split(",")
		stocks = [s.strip() for s in stocks]
		
		"""Get the historical prices and
		create a new Asset object for each stock symbol"""
		curSymbols = [a.symbol for a in self.portfolio.assets]
		for s in stocks:
			if s not in curSymbols:
				prices = u.getHistoricalPrices(s)
				asset = fin.Asset(s, prices)
				self.portfolio.addAsset(asset)
		self.updateGridSymbols()
				
	def updateGridSymbols(self):
		colcount = self.m_stocklist.ColumnCount
		if colcount < 2:
			self.m_stocklist.DeleteColumn(0)
			self.m_stocklist.InsertColumn(0, "Symbol")
			
		for asset in self.portfolio.assets:
			pos = self.m_stocklist.FindItem(-1, asset.symbol)	
			if pos ==-1:
				pos = self.m_stocklist.ItemCount
				self.m_stocklist.InsertStringItem(pos, asset.symbol)
				self.m_stocklist.SetStringItem(pos,0, asset.symbol)
		
	def calculateGrid(self):
		allocations = self.portfolio.getAllocations()
		colcount = self.m_stocklist.ColumnCount
		if colcount < 4:
			self.m_stocklist.InsertColumn(0, "Symbol")
			self.m_stocklist.InsertColumn(1, "Mean Rate")
			self.m_stocklist.InsertColumn(2, "Std. Deviation", width=120)
			self.m_stocklist.InsertColumn(3, "Allocation")
			self.m_stocklist.InsertColumn(4, "Correlation")
			self.m_stocklist.InsertColumn(5, "Beta")
			self.m_stocklist.InsertColumn(6, "Sharpe Ratio")
		
		if len(self.portfolio.assets) != 0:	
			MRAprices = u.getHistoricalPrices("SPY")
			marketRetAsset = fin.Asset("SPY", MRAprices)
			rfr = self.m_rfRadBox.GetStringSelection()
			
			rfRates = u.getHistoricalRates(rfr)
			mrRates = marketRetAsset.getRatesOfReturn(self.portfolio.startdate, self.portfolio.ratemethod)
			dates = u.date_range(self.portfolio.startdate)
			
			ratesmatrix = []
					
			for asset in self.portfolio.assets:
				rates = asset.getRatesOfReturn(self.portfolio.startdate, self.portfolio.ratemethod)
				annmean = 100 * asset.getMeanROR(rates, annualized=True)
				annstd = 100 * asset.getStd(rates, annualized=True)
				rateBundle = []
				for d in dates:
					if d in rfRates.keys() and d in mrRates.keys() and d in rates.keys():
						rateBundle.append((rates[d],rfRates[d],mrRates[d]))
				
				correlation = asset.getCorrelation(rateBundle)
				beta = asset.getBeta(rateBundle, correlation)
				sharpe = asset.getSharpe(rateBundle)
				
				ratesmatrix.append(rateBundle)
				
				pos = self.m_stocklist.FindItem(-1, asset.symbol)	
				if pos ==-1:
					pos = self.m_stocklist.ItemCount
					self.m_stocklist.InsertStringItem(pos, asset.symbol)
					self.m_stocklist.SetStringItem(pos,1, str("%.2f" % annmean)+"%")
					self.m_stocklist.SetStringItem(pos,2, str("%.2f" % annstd)+"%")
					self.m_stocklist.SetStringItem(pos,3, str("%.2f" % allocations[asset.symbol]))
					self.m_stocklist.SetStringItem(pos,4, str("%.2f" % correlation))
					self.m_stocklist.SetStringItem(pos,5, str("%.2f" % beta))
					self.m_stocklist.SetStringItem(pos,6, str("%.2f" % sharpe))
				else:
					self.m_stocklist.SetStringItem(pos,1, str("%.2f" % annmean)+"%")
					self.m_stocklist.SetStringItem(pos,2, str("%.2f" % annstd)+"%")
					self.m_stocklist.SetStringItem(pos,3, str("%.2f" % allocations[asset.symbol]))
					self.m_stocklist.SetStringItem(pos,4, str("%.2f" % correlation))
					self.m_stocklist.SetStringItem(pos,5, str("%.2f" % beta))
					self.m_stocklist.SetStringItem(pos,6, str("%.2f" % sharpe))

			cvmatrix = self.portfolio.getMatrix(ratesmatrix)
			assets = []
			assets.extend(self.portfolio.assets)
			assets.append(marketRetAsset)
			grid = self.m_corgrid
			grid.ClearGrid()
			while self.m_corgrid.NumberRows != 0:
				self.m_corgrid.DeleteCols()
				self.m_corgrid.DeleteRows()

			grid.AppendCols(len(assets))
			grid.AppendRows(len(assets))
			i = 0
			for asset in assets:
				self.m_corgrid.SetRowLabelValue(i, asset.symbol)
				self.m_corgrid.SetColLabelValue(i, asset.symbol)
				i = i+1
			for i in range(len(assets)):
				for j in range(len(assets)):
					self.m_corgrid.SetCellValue(i, j, str("%.2f" % cvmatrix[i][j]))
			
	def analyzeButtonClicked( self, event ):
		"""
		Set the start date of the portfolio based upon the
		stock with the most recent startdate
		"""
		
		dates = [stock.startdate for stock in self.portfolio.assets]
		
		dateWidgetValue = cal._wxdate2pydate(self.m_startingdate.GetValue())
		dates.append(dateWidgetValue)
		maxdate = max(dates)

		if not maxdate == dateWidgetValue:
			for stock in self.portfolio.assets:
				if stock.startdate == maxdate:
					datedictator = stock 
					message = "The stock %s has a later starting date than you specified. Your portfolio's start date will be set to %s ." %(datedictator.symbol, datedictator.startdate)			
					wx.MessageBox(message, 'Info', wx.OK | wx.ICON_INFORMATION)
				
			self.m_startingdate.SetValue(cal._pydate2wxdate(maxdate))
		self.portfolio.startdate = maxdate
		
		if self.m_meanCalcRadBox.GetStringSelection()=="Simple":
			self.portfolio.ratemethod = "Simple"
		else:
			self.portfolio.ratemethod = "Log"
		for asset in self.portfolio.assets:
			asset.rates = asset.getRatesOfReturn(self.portfolio.startdate, self.portfolio.ratemethod)
		
		if self.m_backtestCB.IsChecked():
			self.weightDialog = WeightDialog(self, self.portfolio)
			self.weightDialog.Show()
		
		self.calculateGrid()

	def removeSelClicked( self, event ):
		sel = self.m_stocklist.GetFirstSelected()
		if not sel == -1:
			symbol = self.m_stocklist.GetItemText(sel)
			idx = 0
			for a in self.portfolio.assets:
				if a.symbol ==symbol:
					break
				idx = idx + 1
			del self.portfolio.assets[idx]
			self.m_stocklist.DeleteItem(sel)
			self.calculateGrid()
			
	def removeAllClicked( self, event ):
		del self.portfolio.assets
		self.portfolio.assets = []
		self.m_stocklist.DeleteAllItems()
		self.m_corgrid.ClearGrid()
		while self.m_corgrid.NumberRows != 0:
			self.m_corgrid.DeleteCols()
			self.m_corgrid.DeleteRows()
		self.calculateGrid()
		
	def rfrChanged( self, event ):
		pass
	
	def meanCalcMethChanged( self, event ):
		method = self.m_meanCalcRadBox.GetStringSelection()
		if method != "Simple":
			method = "Log"
		self.portfolio.ratemethod = method
		self.calculateGrid()
	
	def m_mniExitClick( self, event ):
		# TODO: Implement m_mniExitClick
		pass

class WeightDialog( gui.WeightDialogBase ):
	def __init__( self, parent, portfolio ):
		gui.WeightDialogBase.__init__( self, parent )
		self.portfolio = portfolio
		self.totalValue = 100
		self.addSliders()
	
	def addSliders(self):
		self.sliders = {}
		self.sliderLabels = {}
		gSizer = self.sliderPanel.GetSizer()
		
		self.sliderPanel.DestroyChildren()
		val = 100/len(self.portfolio.assets)
		for asset in self.portfolio.assets:
			slider = wx.Slider(self.sliderPanel, wx.ID_ANY, val, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL|wx.SL_LABELS)
			label = wx.StaticText(self.sliderPanel, wx.ID_ANY, asset.symbol, wx.DefaultPosition, wx.DefaultSize, 0)
			label.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
			slider.Bind( wx.EVT_SCROLL, self.sliderScrolling )
			gSizer.Add(label, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
			gSizer.Add(slider, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
			self.sliders[asset.symbol] = slider
			self.sliderLabels[asset.symbol] = label
		
		val *= len(self.portfolio.assets)
		if val != 100:
			add = 100-val
			sl = self.sliders.values()[0]
			sl.SetValue(sl.GetValue()+add)
			
		self.sliderPanel.SetSizer(gSizer)
		self.sliderPanel.Layout()
		self.sliderPanel.Fit()
		gSizer.Fit(self.sliderPanel)
		self.Layout()
		self.Fit()
	
	def sliderScrolling(self, event):
		slideObj = event.EventObject
		val = 0
		for s in self.sliders.itervalues():
			val += s.GetValue()
		
		if val > 100:
			surplus = val - 100
			while int(surplus) > 0:
				slides = [s for s in self.sliders.values() if s.GetId() != slideObj.GetId() and s.GetValue() != 0]
				diff = int(surplus/len(slides))
				if diff == 0:
					diff = surplus
					
				for s in slides:										
					sVal = s.GetValue()
					if sVal-diff >= 0:
						s.SetValue(int(sVal - diff))
						surplus -= int(diff)
					if surplus <= 0:
						break
			
	def weightCancelClicked( self, event ):
		self.Destroy()
	
	def weightOKClicked( self, event ):
		pass