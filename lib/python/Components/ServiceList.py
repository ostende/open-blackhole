from Components.GUIComponent import GUIComponent
from skin import parseColor, parseFont, parseScale

from enigma import eListboxServiceContent, eListbox, eServiceCenter, eServiceReference, gFont, eRect, eSize
from Tools.LoadPixmap import LoadPixmap
from Tools.TextBoundary import getTextBoundarySize

from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN

from Components.Renderer.Picon import getPiconName
from Components.config import config


def refreshServiceList(configElement=None):
	from Screens.InfoBar import InfoBar
	InfoBarInstance = InfoBar.instance
	if InfoBarInstance is not None:
		servicelist = InfoBarInstance.servicelist
		if servicelist:
			servicelist.setMode()


class ServiceList(GUIComponent):
	MODE_NORMAL = 0
	MODE_FAVOURITES = 1

	def __init__(self, serviceList):
		self.serviceList = serviceList
		GUIComponent.__init__(self)
		self.l = eListboxServiceContent()  # noqa: E741

		pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "icons/folder.png"))
		pic and self.l.setPixmap(self.l.picFolder, pic)

		pic = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "icons/marker.png"))
		pic and self.l.setPixmap(self.l.picMarker, pic)

		pic = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "icons/ico_dvb-s.png"))
		pic and self.l.setPixmap(self.l.picDVB_S, pic)

		pic = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "icons/ico_dvb-c.png"))
		pic and self.l.setPixmap(self.l.picDVB_C, pic)

		pic = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "icons/ico_dvb-t.png"))
		pic and self.l.setPixmap(self.l.picDVB_T, pic)

		pic = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "icons/ico_stream.png"))
		pic and self.l.setPixmap(self.l.picStream, pic)

		pic = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "icons/ico_service_group.png"))
		pic and self.l.setPixmap(self.l.picServiceGroup, pic)

		pic = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "icons/icon_crypt.png"))
		pic and self.l.setPixmap(self.l.picCrypto, pic)

		pic = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "icons/record.png"))
		pic and self.l.setPixmap(self.l.picRecord, pic)

		self.root = None
		self.mode = self.MODE_NORMAL
		self.listHeight = 0
		self.listWidth = 0
		self.ServiceNumberFontName = "Regular"
		self.ServiceNumberFontSize = 20
		self.ServiceNameFontName = "Regular"
		self.ServiceNameFontSize = 22
		self.ServiceInfoFontName = "Regular"
		self.ServiceInfoFontSize = 18
		self.ServiceNextInfoFontName = "Regular"
		self.ServiceNextInfoFontSize = 15
		self.progressBarWidth = 52
		self.progressPercentWidth = 0
		self.fieldMargins = 10
		self.ItemHeight = None
		self.skinItemHeight = None

		self.onSelectionChanged = []

	def applySkin(self, desktop, parent):
		def foregroundColorMarked(value):
			self.l.setColor(eListboxServiceContent.markedForeground, parseColor(value))

		def foregroundColorMarkedSelected(value):
			self.l.setColor(eListboxServiceContent.markedForegroundSelected, parseColor(value))

		def backgroundColorMarked(value):
			self.l.setColor(eListboxServiceContent.markedBackground, parseColor(value))

		def backgroundColorMarkedSelected(value):
			self.l.setColor(eListboxServiceContent.markedBackgroundSelected, parseColor(value))

		def foregroundColorServiceNotAvail(value):
			self.l.setColor(eListboxServiceContent.serviceNotAvail, parseColor(value))

		def foregroundColorServiceSelected(value):
			self.l.setColor(eListboxServiceContent.serviceSelected, parseColor(value))

		def foregroundColorEvent(value):
			self.l.setColor(eListboxServiceContent.eventForeground, parseColor(value))

		def foregroundColorNextEvent(value):
			self.l.setColor(eListboxServiceContent.eventNextForeground, parseColor(value))

		def colorServiceDescription(value):
			self.l.setColor(eListboxServiceContent.eventForeground, parseColor(value))

		def foregroundColorEventSelected(value):
			self.l.setColor(eListboxServiceContent.eventForegroundSelected, parseColor(value))

		def foregroundColorEventNextSelected(value):
			self.l.setColor(eListboxServiceContent.eventNextForegroundSelected, parseColor(value))

		def colorServiceDescriptionSelected(value):
			self.l.setColor(eListboxServiceContent.eventForegroundSelected, parseColor(value))

		def foregroundColorEventborder(value):
			self.l.setColor(eListboxServiceContent.eventborderForeground, parseColor(value))

		def foregroundColorEventborderSelected(value):
			self.l.setColor(eListboxServiceContent.eventborderForegroundSelected, parseColor(value))

		def colorEventProgressbar(value):
			self.l.setColor(eListboxServiceContent.serviceEventProgressbarColor, parseColor(value))

		def colorEventProgressbarSelected(value):
			self.l.setColor(eListboxServiceContent.serviceEventProgressbarColorSelected, parseColor(value))

		def colorEventProgressbarBorder(value):
			self.l.setColor(eListboxServiceContent.serviceEventProgressbarBorderColor, parseColor(value))

		def colorEventProgressbarBorderSelected(value):
			self.l.setColor(eListboxServiceContent.serviceEventProgressbarBorderColorSelected, parseColor(value))

		def colorServiceRecorded(value):
			self.l.setColor(eListboxServiceContent.serviceRecorded, parseColor(value))

		def colorFallbackItem(value):
			self.l.setColor(eListboxServiceContent.serviceItemFallback, parseColor(value))

		def colorServiceSelectedFallback(value):
			self.l.setColor(eListboxServiceContent.serviceSelectedFallback, parseColor(value))

		def colorServiceDescriptionFallback(value):
			self.l.setColor(eListboxServiceContent.eventForegroundFallback, parseColor(value))

		def colorServiceDescriptionSelectedFallback(value):
			self.l.setColor(eListboxServiceContent.eventForegroundSelectedFallback, parseColor(value))

		def colorServiceNextDescriptionFallback(value):
			self.l.setColor(eListboxServiceContent.eventNextForegroundFallback, parseColor(value))

		def colorServiceNextDescriptionSelectedFallback(value):
			self.l.setColor(eListboxServiceContent.eventNextForegroundSelectedFallback, parseColor(value))

		def picServiceEventProgressbar(value):
			pic = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, value))
			pic and self.l.setPixmap(self.l.picServiceEventProgressbar, pic)

		def serviceItemHeight(value):
			self.skinItemHeight = parseScale(value)

		def serviceNameFont(value):
			font = parseFont(value, ((1, 1), (1, 1)))
			self.ServiceNameFontName = font.family
			self.ServiceNameFontSize = font.pointSize

		def serviceInfoFont(value):
			font = parseFont(value, ((1, 1), (1, 1)))
			self.ServiceInfoFontName = font.family
			self.ServiceInfoFontSize = font.pointSize
			font = parseFont(value, ((5, 6), (1, 1)))
			self.ServiceNextInfoFontName = font.family
			self.ServiceNextInfoFontSize = font.pointSize

		def serviceNumberFont(value):
			font = parseFont(value, ((1, 1), (1, 1)))
			self.ServiceNumberFontName = font.family
			self.ServiceNumberFontSize = font.pointSize

		def progressbarHeight(value):
			self.l.setProgressbarHeight(parseScale(value))

		def progressbarBorderWidth(value):
			self.l.setProgressbarBorderWidth(parseScale(value))

		def progressBarWidth(value):
			self.progressBarWidth = parseScale(value)

		def progressPercentWidth(value):
			self.progressPercentWidth = parseScale(value)

		def fieldMargins(value):
			self.fieldMargins = parseScale(value)

		def nonplayableMargins(value):
			self.l.setNonplayableMargins(parseScale(value))

		def itemsDistances(value):
			self.l.setItemsDistances(parseScale(value))

		for (attrib, value) in self.skinAttributes[:]:
			try:
				locals().get(attrib)(value)
				self.skinAttributes.remove((attrib, value))
			except:
				pass
		rc = GUIComponent.applySkin(self, desktop, parent)
		self.listHeight = self.instance.size().height()
		self.listWidth = self.instance.size().width()
		self.setFontsize()
		self.setMode(self.mode)
		return rc

	def connectSelChanged(self, fnc):
		if fnc not in self.onSelectionChanged:
			self.onSelectionChanged.append(fnc)

	def disconnectSelChanged(self, fnc):
		if fnc in self.onSelectionChanged:
			self.onSelectionChanged.remove(fnc)

	def selectionChanged(self):
		for x in self.onSelectionChanged:
			x()

	def setCurrent(self, ref, adjust=True):
		if self.l.setCurrent(ref):
			return None
		from Components.ServiceEventTracker import InfoBarCount
		if adjust and config.usage.multibouquet.value and InfoBarCount == 1 and ref and ref.type != 8192:
			print("[servicelist] search for service in userbouquets")
			isRadio = ref.toString().startswith("1:0:2:") or ref.toString().startswith("1:0:A:")
			if self.serviceList:
				revert_mode = config.servicelist.lastmode.value
				revert_root = self.getRoot()
				if not isRadio:
					self.serviceList.setModeTv()
					revert_tv_root = self.getRoot()
					bouquets = self.serviceList.getBouquetList()
					for bouquet in bouquets:
						self.serviceList.enterUserbouquet(bouquet[1])
						if self.l.setCurrent(ref):
							config.servicelist.lastmode.save()
							self.serviceList.saveChannel(ref)
							return True
					self.serviceList.enterUserbouquet(revert_tv_root)
				else:
					self.serviceList.setModeRadio()
					revert_radio_root = self.getRoot()
					bouquets = self.serviceList.getBouquetList()
					for bouquet in bouquets:
						self.serviceList.enterUserbouquet(bouquet[1])
						if self.l.setCurrent(ref):
							config.servicelist.lastmode.save()
							self.serviceList.saveChannel(ref)
							return True
					self.serviceList.enterUserbouquet(revert_radio_root)
				print("[servicelist] service not found in any userbouquets")
				if revert_mode == "tv":
					self.serviceList.setModeTv()
				elif revert_mode == "radio":
					self.serviceList.setModeRadio()
				self.serviceList.enterUserbouquet(revert_root)
		return False

	def getCurrent(self):
		r = eServiceReference()
		self.l.getCurrent(r)
		return r

	def getPrev(self):
		r = eServiceReference()
		self.l.getPrev(r)
		return r

	def getNext(self):
		r = eServiceReference()
		self.l.getNext(r)
		return r

	def getList(self):
		return self.l.getList()

	def atBegin(self):
		return self.instance.atBegin()

	def atEnd(self):
		return self.instance.atEnd()

	def moveUp(self):
		self.instance.moveSelection(self.instance.moveUp)

	def moveDown(self):
		self.instance.moveSelection(self.instance.moveDown)

	def moveToChar(self, char):
		# TODO fill with life
		print("[ServiceList] Next char: ")
		index = self.l.getNextBeginningWithChar(char)
		indexup = self.l.getNextBeginningWithChar(char.upper())
		if indexup != 0:
			if index > indexup or index == 0:
				index = indexup

		self.instance.moveSelectionTo(index)
		print("[ServiceList] Moving to character " + str(char))

	def moveToNextMarker(self):
		idx = self.l.getNextMarkerPos()
		self.instance.moveSelectionTo(idx)

	def moveToPrevMarker(self):
		idx = self.l.getPrevMarkerPos()
		self.instance.moveSelectionTo(idx)

	def moveToIndex(self, index):
		self.instance.moveSelectionTo(index)

	def getCurrentIndex(self):
		return self.instance.getCurrentIndex()

	GUI_WIDGET = eListbox

	def setItemsPerPage(self):
		numberOfRows = config.usage.serviceitems_per_page.value
		itemHeight = (self.listHeight // numberOfRows if numberOfRows > 0 else self.skinItemHeight) or 28
		self.ItemHeight = itemHeight
		self.l.setItemHeight(itemHeight)
		if self.listHeight:
			self.instance.resize(eSize(self.listWidth, self.listHeight // itemHeight * itemHeight))

	def getSelectionPosition(self):
		# Adjust absolute index to index in displayed view
		rowCount = self.listHeight // self.ItemHeight
		index = self.getCurrentIndex() % rowCount
		sely = self.instance.position().y() + self.ItemHeight * index
		if sely >= self.instance.position().y() + self.listHeight:
			sely -= self.listHeight
		return self.listWidth + self.instance.position().x(), sely

	def setFontsize(self):
		self.ServiceNumberFont = gFont(self.ServiceNameFontName, self.ServiceNameFontSize + config.usage.servicenum_fontsize.value)
		self.ServiceNameFont = gFont(self.ServiceNameFontName, self.ServiceNameFontSize + config.usage.servicename_fontsize.value)
		self.ServiceInfoFont = gFont(self.ServiceInfoFontName, self.ServiceInfoFontSize + config.usage.serviceinfo_fontsize.value)
		self.ServiceNextInfoFont = gFont(self.ServiceNextInfoFontName, self.ServiceNextInfoFontSize + config.usage.serviceinfo_fontsize.value)
		self.l.setElementFont(self.l.celServiceName, self.ServiceNameFont)
		self.l.setElementFont(self.l.celServiceNumber, self.ServiceNumberFont)
		self.l.setElementFont(self.l.celServiceInfo, self.ServiceInfoFont)

	def postWidgetCreate(self, instance):
		instance.setWrapAround(True)
		instance.setContent(self.l)
		instance.selectionChanged.get().append(self.selectionChanged)
		self.setFontsize()

	def preWidgetRemove(self, instance):
		instance.setContent(None)
		instance.selectionChanged.get().remove(self.selectionChanged)

	def getRoot(self):
		return self.root

	def getRootServices(self):
		serviceHandler = eServiceCenter.getInstance()
		list = serviceHandler.list(self.root)
		dest = []
		if list is not None:
			while True:
				s = list.getNext()
				if s.valid():
					dest.append(s.toString())
				else:
					break
		return dest

	def setPlayableIgnoreService(self, ref):
		self.l.setIgnoreService(ref)

	def setRoot(self, root, justSet=False):
		self.root = root
		self.l.setRoot(root, justSet)
		if not justSet:
			self.l.sort()
		self.selectionChanged()

	def resetRoot(self):
		index = self.instance.getCurrentIndex()
		self.l.setRoot(self.root, False)
		self.l.sort()
		self.instance.moveSelectionTo(index)

	def removeCurrent(self):
		self.l.removeCurrent()

	def addService(self, service, beforeCurrent=False):
		self.l.addService(service, beforeCurrent)

	def finishFill(self):
		self.l.FillFinished()
		self.l.sort()

# stuff for multiple marks (edit mode / later multiepg)
	def clearMarks(self):
		self.l.initMarked()

	def isMarked(self, ref):
		return self.l.isMarked(ref)

	def addMarked(self, ref):
		self.l.addMarked(ref)

	def removeMarked(self, ref):
		self.l.removeMarked(ref)

	def getMarked(self):
		i = self.l
		i.markedQueryStart()
		ref = eServiceReference()
		marked = []
		while i.markedQueryNext(ref) == 0:
			marked.append(ref.toString())
			ref = eServiceReference()
		return marked

	# just for movemode.. only one marked entry..
	def setCurrentMarked(self, state):
		self.l.setCurrentMarked(state)

	def setMode(self, mode):
		self.mode = mode
		self.setItemsPerPage()
		two_lines_val = int(config.usage.servicelist_twolines.value)
		show_two_lines = two_lines_val and mode == self.MODE_FAVOURITES
		self.ItemHeight *= (2 if show_two_lines else 1)
		self.l.setItemHeight(self.ItemHeight)
		self.l.setVisualMode(eListboxServiceContent.visModeComplex)

		if config.usage.service_icon_enable.value:
			self.l.setGetPiconNameFunc(getPiconName)
		else:
			self.l.setGetPiconNameFunc(None)

		rowWidth = self.instance.size().width() - 30  # scrollbar is fixed 20 + 10 Extra marge

		if mode == self.MODE_NORMAL or not config.usage.show_channel_numbers_in_servicelist.value:
			channelNumberWidth = 0
			channelNumberSpace = 0
		else:
			channelNumberWidth = config.usage.alternative_number_mode.value and getTextBoundarySize(self.instance, self.ServiceNumberFont, self.instance.size(), "0000").width() or getTextBoundarySize(self.instance, self.ServiceNumberFont, self.instance.size(), "00000").width()
			channelNumberSpace = self.fieldMargins

		self.l.setElementPosition(self.l.celServiceNumber, eRect(0, 0, channelNumberWidth, self.ItemHeight))

		progressWidth = self.progressBarWidth
		if "perc" in config.usage.show_event_progress_in_servicelist.value:
			progressWidth = self.progressPercentWidth or self.progressBarWidth

		if "left" in config.usage.show_event_progress_in_servicelist.value:
			self.l.setElementPosition(self.l.celServiceEventProgressbar, eRect(channelNumberWidth + channelNumberSpace, 0, progressWidth, self.ItemHeight))
			self.l.setElementPosition(self.l.celServiceName, eRect(channelNumberWidth + channelNumberSpace + progressWidth + self.fieldMargins, 0, rowWidth - (channelNumberWidth + channelNumberSpace + progressWidth + self.fieldMargins), self.ItemHeight))
		elif "right" in config.usage.show_event_progress_in_servicelist.value:
			self.l.setElementPosition(self.l.celServiceEventProgressbar, eRect(rowWidth - progressWidth, 0, progressWidth, self.ItemHeight))
			self.l.setElementPosition(self.l.celServiceName, eRect(channelNumberWidth + channelNumberSpace, 0, rowWidth - (channelNumberWidth + channelNumberSpace + progressWidth + self.fieldMargins), self.ItemHeight))
		else:
			self.l.setElementPosition(self.l.celServiceEventProgressbar, eRect(0, 0, 0, 0))
			self.l.setElementPosition(self.l.celServiceName, eRect(channelNumberWidth + channelNumberSpace, 0, rowWidth - (channelNumberWidth + channelNumberSpace), self.ItemHeight))
		self.l.setElementFont(self.l.celServiceName, self.ServiceNameFont)
		self.l.setElementFont(self.l.celServiceNumber, self.ServiceNumberFont)
		self.l.setElementFont(self.l.celServiceInfo, self.ServiceInfoFont)
		if show_two_lines and two_lines_val == 2:
			self.l.setElementFont(self.l.celServiceNextInfo, self.ServiceNextInfoFont)
			nextTitle = _("NEXT") + ":  "
			self.l.setNextTitle(nextTitle)
		if "perc" in config.usage.show_event_progress_in_servicelist.value:
			self.l.setElementFont(self.l.celServiceEventProgressbar, self.ServiceInfoFont)
		self.l.setShowTwoLines(two_lines_val)
		self.l.setHideNumberMarker(config.usage.hide_number_markers.value)
		self.l.setServiceTypeIconMode(int(config.usage.servicetype_icon_mode.value))
		self.l.setCryptoIconMode(int(config.usage.crypto_icon_mode.value))
		self.l.setRecordIndicatorMode(int(config.usage.record_indicator_mode.value))
		self.l.setColumnWidth(-1 if show_two_lines else int(config.usage.servicelist_column.value))

	def selectionEnabled(self, enabled):
		if self.instance is not None:
			self.instance.setSelectionEnable(enabled)
