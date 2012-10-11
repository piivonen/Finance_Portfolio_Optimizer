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
		prices = [(p.date, p.adjclosing) for p in stock.prices if p.date >= self.portfolio.startdate]
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
		for s in stocks:
			exists = False
			for a in self.portfolio.assets:
				if a.symbol == s:
					exists = True
	
			if not exists:
				prices = u.getHistoricalPrices(s)
				asset = fin.Asset(s, prices)
				self.portfolio.addAsset(asset)
		
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
		
		for asset in self.portfolio.assets:
			asset.rates = asset.getRatesOfReturn(self.portfolio.startdate)
		
		self.calculateGrid()
		
	def calculateGrid(self):
		allocations = self.portfolio.getAllocations()
		colcount = self.m_stocklist.ColumnCount
		if colcount < 4:
			self.m_stocklist.InsertColumn(0, "Symbol")
			self.m_stocklist.InsertColumn(1, "Mean Rate")
			self.m_stocklist.InsertColumn(2, "Std. Deviation (ln)", width=120)
			self.m_stocklist.InsertColumn(3, "Allocation")
			
			
		for asset in self.portfolio.assets:
	
			annmean = asset.getMeanROR(self.portfolio.startdate, self.portfolio.meanmethod)
			annstd = asset.getStd(self.portfolio.startdate, self.portfolio.meanmethod)
			pos = self.m_stocklist.FindItem(-1, asset.symbol)	
			if pos ==-1:
				pos = self.m_stocklist.ItemCount
				self.m_stocklist.InsertStringItem(pos, asset.symbol)
				self.m_stocklist.SetStringItem(pos,1, str("%.2f" % annmean))
				self.m_stocklist.SetStringItem(pos,2, str("%.2f" % annstd))
				self.m_stocklist.SetStringItem(pos,3, str("%.2f" % allocations[asset.symbol]))
			else:
				self.m_stocklist.SetStringItem(pos,1, str("%.2f" % annmean))
				self.m_stocklist.SetStringItem(pos,2, str("%.2f" % annstd))
				self.m_stocklist.SetStringItem(pos,3, str("%.2f" % allocations[asset.symbol]))
				
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
		self.calculateGrid()
		
	def rfrChanged( self, event ):
		pass
	
	def stdMethChanged( self, event ):
		method = self.m_sdRadBox.GetStringSelection()
		if method != "Simple":
			method = "Log"
		self.portfolio.meanmethod = method
		self.calculateGrid()
	
	def m_mniExitClick( self, event ):
		# TODO: Implement m_mniExitClick
		pass
	
	
