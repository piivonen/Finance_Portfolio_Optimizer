"""Subclass of MainFrameBase, which is generated by wxFormBuilder."""

import wx
import gui

# Implementing MainFrameBase
class MainFrameBase( gui.MainFrameBase ):
	def __init__( self, parent ):
		gui.MainFrameBase.__init__( self, parent )
	
	# Handlers for MainFrameBase events.
	def m_addButtonClick( self, event ):
		# TODO: Implement m_addButtonClick
		pass
	
	def m_mniExitClick( self, event ):
		# TODO: Implement m_mniExitClick
		self.close()
	
	
