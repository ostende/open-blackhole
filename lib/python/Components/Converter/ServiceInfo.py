from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService
from Screens.InfoBarGenerics import hasActiveSubservicesForCurrentChannel
from Components.Element import cached
from Components.Converter.Poll import Poll
from Components.Converter.VAudioInfo import StdAudioDesc
from Tools.Transponder import ConvertToHumanReadable


WIDESCREEN = [1, 3, 4, 7, 8, 0xB, 0xC, 0xF, 0x10]

def getProcVal(pathname, base=10):
	val = None
	try:
		f = open(pathname, "r")
		val = int(f.read(), base)
		f.close()
		if val >= 2 ** 31:
			val -= 2 ** 32
	except:
		pass
	return val


def getVal(pathname, info, infoVal, base=10):
	val = getProcVal(pathname, base=base)
	return val if val is not None else info.getInfo(infoVal)


def getValInt(pathname, info, infoVal, base=10, default=-1):
	val = getVal(pathname, info, infoVal, base)
	return val if val is not None else default


def getValStr(pathname, info, infoVal, base=10, convert=lambda x: "%d" % x, instance=None):
	val = getProcVal(pathname, base=base)
	return convert(val) if val is not None else instance.getServiceInfoString(info, infoVal, convert)


def getVideoHeight(info):
	return getValInt("/proc/stb/vmpeg/0/yres", info, iServiceInformation.sVideoHeight, base=16)


def getVideoHeightStr(info, convert=lambda x: "%d" % x if x > 0 else "?", instance=None):
	return getValStr("/proc/stb/vmpeg/0/yres", info, iServiceInformation.sVideoHeight, base=16, convert=convert, instance=instance)


def getVideoWidth(info):
	return getValInt("/proc/stb/vmpeg/0/xres", info, iServiceInformation.sVideoWidth, base=16)


def getVideoWidthStr(info, convert=lambda x: "%d" % x if x > 0 else "?", instance=None):
	return getValStr("/proc/stb/vmpeg/0/xres", info, iServiceInformation.sVideoWidth, base=16, convert=convert, instance=instance)


def getFrameRate(info):
	return getValInt("/proc/stb/vmpeg/0/framerate", info, iServiceInformation.sFrameRate)


def getFrameRateStr(info, convert=lambda x: "%d" % x if x > 0 else "", instance=None):
	return getValStr("/proc/stb/vmpeg/0/framerate", info, iServiceInformation.sFrameRate, convert=convert, instance=instance)


def getProgressive(info):
	return getValInt("/proc/stb/vmpeg/0/progressive", info, iServiceInformation.sProgressive, default=0)


def getProgressiveStr(info, convert=lambda x: "" if x else "i", instance=None):
	return getValStr("/proc/stb/vmpeg/0/progressive", info, iServiceInformation.sProgressive, convert=convert, instance=instance)


class ServiceInfo(Poll, Converter):
	HAS_TELETEXT = 1
	IS_MULTICHANNEL = 2
	IS_STEREO = 3
	IS_CRYPTED = 4
	IS_WIDESCREEN = 5
	IS_NOT_WIDESCREEN = 6
	SUBSERVICES_AVAILABLE = 7
	XRES = 8
	YRES = 9
	APID = 10
	VPID = 11
	PCRPID = 12
	PMTPID = 13
	TXTPID = 14
	TSID = 15
	ONID = 16
	SID = 17
	FRAMERATE = 18
	TRANSFERBPS = 19
	HAS_HBBTV = 20
	AUDIOTRACKS_AVAILABLE = 21
	SUBTITLES_AVAILABLE = 22
	EDITMODE = 23
	IS_STREAM = 24
	IS_SD = 25
	IS_HD = 26
	IS_1080 = 27
	IS_720 = 28
	IS_576 = 29
	IS_480 = 30
	IS_4K = 31
	FREQ_INFO = 32
	PROGRESSIVE = 33
	VIDEO_INFO = 34
	IS_SD_AND_WIDESCREEN = 35
	IS_SD_AND_NOT_WIDESCREEN = 36
	IS_SDR = 37
	IS_HDR = 38
	IS_HDR10 = 39
	IS_HLG = 40
	IS_VIDEO_MPEG2 = 41
	IS_VIDEO_AVC = 42
	IS_VIDEO_HEVC = 43

	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.poll_interval = 5000
		self.poll_enabled = True
		self.type, self.interesting_events = {
			"HasTelext": (self.HAS_TELETEXT, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsMultichannel": (self.IS_MULTICHANNEL, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsStereo": (self.IS_STEREO, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsCrypted": (self.IS_CRYPTED, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsWidescreen": (self.IS_WIDESCREEN, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsNotWidescreen": (self.IS_NOT_WIDESCREEN, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"SubservicesAvailable": (self.SUBSERVICES_AVAILABLE, (iPlayableService.evStart,)),
			"VideoWidth": (self.XRES, (iPlayableService.evVideoSizeChanged,)),
			"VideoHeight": (self.YRES, (iPlayableService.evVideoSizeChanged,)),
			"AudioPid": (self.APID, (iPlayableService.evUpdatedInfo,)),
			"VideoPid": (self.VPID, (iPlayableService.evUpdatedInfo,)),
			"PcrPid": (self.PCRPID, (iPlayableService.evUpdatedInfo,)),
			"PmtPid": (self.PMTPID, (iPlayableService.evUpdatedInfo,)),
			"TxtPid": (self.TXTPID, (iPlayableService.evUpdatedInfo,)),
			"TsId": (self.TSID, (iPlayableService.evUpdatedInfo,)),
			"OnId": (self.ONID, (iPlayableService.evUpdatedInfo,)),
			"Sid": (self.SID, (iPlayableService.evUpdatedInfo,)),
			"Framerate": (self.FRAMERATE, (iPlayableService.evVideoFramerateChanged, iPlayableService.evUpdatedInfo,)),
			"Progressive": (self.PROGRESSIVE, (iPlayableService.evVideoProgressiveChanged, iPlayableService.evUpdatedInfo,)),
			"VideoInfo": (self.VIDEO_INFO, (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evVideoProgressiveChanged, iPlayableService.evUpdatedInfo,)),
			"TransferBPS": (self.TRANSFERBPS, (iPlayableService.evUpdatedInfo,)),
			"HasHBBTV": (self.HAS_HBBTV, (iPlayableService.evUpdatedInfo, iPlayableService.evHBBTVInfo, iPlayableService.evStart)),
			"AudioTracksAvailable": (self.AUDIOTRACKS_AVAILABLE, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"SubtitlesAvailable": (self.SUBTITLES_AVAILABLE, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"Freq_Info": (self.FREQ_INFO, (iPlayableService.evUpdatedInfo,)),
			"Editmode": (self.EDITMODE, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsStream": (self.IS_STREAM, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsSD": (self.IS_SD, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsHD": (self.IS_HD, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsSDAndWidescreen": (self.IS_SD_AND_WIDESCREEN, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsSDAndNotWidescreen": (self.IS_SD_AND_NOT_WIDESCREEN, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"Is1080": (self.IS_1080, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"Is720": (self.IS_720, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"Is576": (self.IS_576, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"Is480": (self.IS_480, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"Is4K": (self.IS_4K, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsSDR": (self.IS_SDR, (iPlayableService.evVideoGammaChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsHDR": (self.IS_HDR, (iPlayableService.evVideoGammaChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsHDR10": (self.IS_HDR10, (iPlayableService.evVideoGammaChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsHLG": (self.IS_HLG, (iPlayableService.evVideoGammaChanged, iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsVideoMPEG2": (self.IS_VIDEO_MPEG2, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsVideoAVC": (self.IS_VIDEO_AVC, (iPlayableService.evUpdatedInfo, iPlayableService.evStart)),
			"IsVideoHEVC": (self.IS_VIDEO_HEVC, (iPlayableService.evUpdatedInfo, iPlayableService.evVideoSizeChanged)),
		}[type]

	def isVideoService(self, info):
		serviceInfo = info.getInfoString(iServiceInformation.sServiceref).split(':')
		return len(serviceInfo) < 3 or serviceInfo[2] != '2'

	def getServiceInfoString(self, info, what, convert=lambda x: "%d" % x):
		v = info.getInfo(what)
		if v == -1:
			return _("N/A")
		if v == -2:
			return info.getInfoString(what)
		return convert(v)

	@cached
	def getBoolean(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return False
		video_height = None
		video_width = None
		video_aspect = None
		video_height = getVideoHeight(info)
		video_width = getVideoWidth(info)
		video_aspect = info.getInfo(iServiceInformation.sAspect)
		if self.type == self.HAS_TELETEXT:
			tpid = info.getInfo(iServiceInformation.sTXTPID)
			return tpid != -1
		elif self.type in (self.IS_MULTICHANNEL, self.IS_STEREO):
			# FIXME. but currently iAudioTrackInfo doesn't provide more information.
			audio = service.audioTracks()
			if audio:
				n = audio.getNumberOfTracks()
				idx = 0
				while idx < n:
					i = audio.getTrackInfo(idx)
					description = StdAudioDesc(i.getDescription())
					if description and description.split()[0] in ("AC4", "AAC+", "AC3", "AC3+", "Dolby", "DTS", "DTS-HD", "HE-AAC", "IPCM", "LPCM", "WMA Pro"):
						if self.type == self.IS_MULTICHANNEL:
							return True
						elif self.type == self.IS_STEREO:
							return False
					idx += 1
				if self.type == self.IS_MULTICHANNEL:
					return False
				elif self.type == self.IS_STEREO:
					return True
			return False
		elif self.type == self.IS_CRYPTED:
			return info.getInfo(iServiceInformation.sIsCrypted) == 1
		elif self.type == self.SUBSERVICES_AVAILABLE:
			return hasActiveSubservicesForCurrentChannel(':'.join(info.getInfoString(iServiceInformation.sServiceref).split(':')[:11]))
		elif self.type == self.HAS_HBBTV:
			return info.getInfoString(iServiceInformation.sHBBTVUrl) != ""
		elif self.type == self.AUDIOTRACKS_AVAILABLE:
			audio = service.audioTracks()
			return bool(audio) and audio.getNumberOfTracks() > 1
		elif self.type == self.SUBTITLES_AVAILABLE:
			subtitle = service and service.subtitle()
			subtitlelist = subtitle and subtitle.getSubtitleList()
			if subtitlelist:
				return len(subtitlelist) > 0
			return False
		elif self.type == self.EDITMODE:
			return hasattr(self.source, "editmode") and not not self.source.editmode
		elif self.type == self.IS_STREAM:
			return service.streamed() is not None
		elif self.isVideoService(info):
			if self.type == self.IS_WIDESCREEN:
				return video_aspect in WIDESCREEN
			elif self.type == self.IS_NOT_WIDESCREEN:
				return video_aspect not in WIDESCREEN
			elif self.type == self.IS_HD:
				return video_width > 1025 and video_width <= 1920 and video_height >= 481 and video_height < 1440 or video_width >= 960 and video_height == 720
			elif self.type == self.IS_SD:
				return video_width > 1 and video_width <= 1024 and video_height > 1 and video_height <= 578
			elif self.type == self.IS_SD_AND_WIDESCREEN:
				return video_height < 578 and video_aspect in WIDESCREEN
			elif self.type == self.IS_SD_AND_NOT_WIDESCREEN:
				return video_height < 578 and video_aspect not in WIDESCREEN
			elif self.type == self.IS_1080:
				return video_width >= 1367 and video_width <= 1920 and video_height >= 768 and video_height <= 1440
			elif self.type == self.IS_720:
				return video_width >= 1025 and video_width <= 1366 and video_height >= 481 and video_height <= 768 or video_width >= 960 and video_height == 720
			elif self.type == self.IS_576:
				return video_width > 1 and video_width <= 1024 and video_height > 481 and video_height <= 578
			elif self.type == self.IS_480:
 				return video_width > 1 and video_width <= 1024 and video_height > 1 and video_height <= 480
			elif self.type == self.IS_4K:
				return video_height >= 1460
			elif self.type == self.PROGRESSIVE:
				return bool(self._getProgressive(info))
			elif self.type == self.IS_SDR:
				return info.getInfo(iServiceInformation.sGamma) == 0
			elif self.type == self.IS_HDR:
				return info.getInfo(iServiceInformation.sGamma) == 1
			elif self.type == self.IS_HDR10:
				return info.getInfo(iServiceInformation.sGamma) == 2
			elif self.type == self.IS_HLG:
				return info.getInfo(iServiceInformation.sGamma) == 3
			elif self.type == self.IS_VIDEO_MPEG2:
				return info.getInfo(iServiceInformation.sVideoType) == 0
			elif self.type == self.IS_VIDEO_AVC:
				return info.getInfo(iServiceInformation.sVideoType) == 1
			elif self.type == self.IS_VIDEO_HEVC:
				if info.getInfoString(iServiceInformation.sServiceref).startswith("5002") and info.getInfo(iServiceInformation.sVideoType) == -1:
					return 7
				else:
					return info.getInfo(iServiceInformation.sVideoType) == 7
		return False

	boolean = property(getBoolean)

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""
		if self.type == self.XRES:
			return getVideoWidthStr(info, instance=self)
		elif self.type == self.YRES:
			return getVideoHeightStr(info, instance=self)
		elif self.type == self.APID:
			return self.getServiceInfoString(info, iServiceInformation.sAudioPID)
		elif self.type == self.VPID:
			return self.getServiceInfoString(info, iServiceInformation.sVideoPID)
		elif self.type == self.PCRPID:
			return self.getServiceInfoString(info, iServiceInformation.sPCRPID)
		elif self.type == self.PMTPID:
			return self.getServiceInfoString(info, iServiceInformation.sPMTPID)
		elif self.type == self.TXTPID:
			return self.getServiceInfoString(info, iServiceInformation.sTXTPID)
		elif self.type == self.TSID:
			return self.getServiceInfoString(info, iServiceInformation.sTSID)
		elif self.type == self.ONID:
			return self.getServiceInfoString(info, iServiceInformation.sONID)
		elif self.type == self.SID:
			return self.getServiceInfoString(info, iServiceInformation.sSID)
		elif self.type == self.FRAMERATE:
			return getFrameRateStr(info, convert=lambda x: "%d fps" % ((x + 500) // 1000), instance=self)
		elif self.type == self.PROGRESSIVE:
			return getProgressiveStr(info, instance=self)
		elif self.type == self.TRANSFERBPS:
			return self.getServiceInfoString(info, iServiceInformation.sTransferBPS, lambda x: "%d kB/s" % (x // 1024))
		elif self.type == self.HAS_HBBTV:
			return info.getInfoString(iServiceInformation.sHBBTVUrl)
		elif self.type == self.FREQ_INFO:
			feinfo = service.frontendInfo()
			if feinfo is None:
				return ""
			feraw = feinfo.getAll(False)
			if feraw is None:
				return ""
			fedata = ConvertToHumanReadable(feraw)
			if fedata is None:
				return ""
			frequency = fedata.get("frequency")
			sr_txt = "Sr:"
			polarization = fedata.get("polarization_abbreviation")
			if polarization is None:
				polarization = ""
			symbolrate = str(int(fedata.get("symbol_rate", 0)))
			if symbolrate == "0":
				sr_txt = ""
				symbolrate = ""
			fec = fedata.get("fec_inner")
			if fec is None:
				fec = ""
			out = "Freq: %s %s %s %s %s" % (frequency, polarization, sr_txt, symbolrate, fec)
			return out
		elif self.type == self.VIDEO_INFO:
			progressive = getProgressiveStr(info, instance=self)
			fieldrate = getFrameRate(info)
			if fieldrate > 0:
				if progressive == 'i':
					fieldrate *= 2
				fieldrate = "%dHz" % ((fieldrate + 500) // 1000,)
			else:
				fieldrate = ""
			return "%sx%s%s %s" % (getVideoWidthStr(info, instance=self), getVideoHeightStr(info, instance=self), progressive, fieldrate)
		return ""

	text = property(getText)

	@cached
	def getValue(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return -1
		if self.type == self.XRES:
			return str(getVideoWidth(info))
		elif self.type == self.YRES:
			return str(getVideoHeight(info))
		elif self.type == self.FRAMERATE:
			return str(getFrameRate(self, info))
		return -1

	value = property(getValue)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
			Converter.changed(self, what)
