from os import access, mkdir, path as ospath, rmdir, stat, statvfs, walk, W_OK
import enigma
import time

from Components.config import config
from Components.GUIComponent import GUIComponent
from Components import Harddisk
import Components.Task
from Components.VariableText import VariableText


def isTrashFolder(path):
	path = ospath.realpath(path)
	return getTrashFolder(path) == path


def getTrashFolder(path=None):
	# Returns trash folder without symlinks
	try:
		if path is None or ospath.realpath(path) == "/media/autofs":
			return ""
		else:
			trashcan = Harddisk.findMountPoint(ospath.realpath(path))
			if "/movie" in path:
				trashcan = ospath.join(trashcan, "movie")
			elif config.usage.default_path.value in path:
				# if default_path happens to not be the default /hdd/media/movie, then we can have a trash folder there instead
				trashcan = ospath.join(trashcan, config.usage.default_path.value)
			return ospath.realpath(ospath.join(trashcan, ".Trash"))
	except:
		return None


def createTrashFolder(path=None):
	trash = getTrashFolder(path)
	print("[Trashcan] Debug path %s => %s" % (path, trash))
	if trash and access(ospath.split(trash)[0], W_OK):
		if not ospath.isdir(trash):
			try:
				mkdir(trash)
			except:
				return None
		return trash
	else:
		return None


def get_size(start_path="."):
	total_size = 0
	if start_path:
		for dirpath, dirnames, filenames in walk(start_path):
			for f in filenames:
				try:
					fp = ospath.join(dirpath, f)
					total_size += ospath.getsize(fp)
				except:
					pass
	return total_size


class Trashcan:
	def __init__(self, session):
		self.session = session
		session.nav.record_event.append(self.gotRecordEvent)
		self.gotRecordEvent(None, None)

	def gotRecordEvent(self, service, event):
		if event == enigma.iRecordableService.evEnd:
			self.cleanIfIdle()

	def destroy(self):
		if self.session is not None:
			self.session.nav.record_event.remove(self.gotRecordEvent)
		self.session = None

	def __del__(self):
		self.destroy()

	def cleanIfIdle(self):
		# RecordTimer calls this when preparing a recording. That is a
		# nice moment to clean up.
		from RecordTimer import n_recordings
		if n_recordings > 0:
			print("[Trashcan] Recording(s) in progress:", n_recordings)
			return
# If movielist_trashcan_days is 0 it means don't timeout anything -
# just use the "leave nGB settting"
#
		if (config.usage.movielist_trashcan_days.value > 0):
			ctimeLimit = time.time() - (config.usage.movielist_trashcan_days.value * 3600 * 24)
		else:
			ctimeLimit = 0
		reserveBytes = 1024 * 1024 * 1024 * int(config.usage.movielist_trashcan_reserve.value)
		clean(ctimeLimit, reserveBytes)


def clean(ctimeLimit, reserveBytes):
	isCleaning = False
	for job in Components.Task.job_manager.getPendingJobs():
		jobname = str(job.name)
		if jobname.startswith(_("Cleaning Trashes")):
			isCleaning = True
			break

	if config.usage.movielist_trashcan.value and not isCleaning:
		name = _("Cleaning Trashes")
		job = Components.Task.Job(name)
		task = CleanTrashTask(job, name)
		task.openFiles(ctimeLimit, reserveBytes)
		Components.Task.job_manager.AddJob(job)
	elif isCleaning:
		print("[Trashcan] Cleanup already running")
	else:
		print("[Trashcan] Disabled skipping check.")


def cleanAll(path=None):
	trash = getTrashFolder(path)
	if not ospath.isdir(trash):
		print("[Trashcan] No trash.", trash)
		return 0
	for root, dirs, files in walk(trash.encode(), topdown=False):  # handle non utf-8 filenames
		for name in files:
			fn = ospath.join(root, name)
			enigma.eBackgroundFileEraser.getInstance().erase(fn)
		for name in dirs:		# Remove empty directories if possible
			try:
				rmdir(ospath.join(root, name))
			except:
				pass


def init(session):
	global instance
	instance = Trashcan(session)


class CleanTrashTask(Components.Task.PythonTask):
	def openFiles(self, ctimeLimit, reserveBytes):
		self.ctimeLimit = ctimeLimit
		self.reserveBytes = reserveBytes

	def work(self):
		# add the default movie path
		trashcanLocations = set([ospath.join(config.usage.default_path.value)])

		# add the root and the movie directory of each mount
		print("[Trashcan] probing folders")
		f = open("/proc/mounts", "r")
		for line in f.readlines():
			parts = line.strip().split()
			if parts[1] == "/media/autofs":
				continue
			# skip network mounts unless the option to clean them is set
			if (not config.usage.movielist_trashcan_network_clean.value and
				(parts[1].startswith("/media/net") or parts[1].startswith("/media/autofs"))):
				continue
			# one trashcan in the root, one in movie subdirectory
			trashcanLocations.add(parts[1])
			trashcanLocations.add(ospath.join(parts[1], "movie"))
		f.close()

		for trashfolder in trashcanLocations:
			trashfolder = ospath.join(trashfolder, ".Trash")
			if ospath.isdir(trashfolder):
				print("[Trashcan][CleanTrashTask][work] looking in trashcan", trashfolder)
				trashsize = get_size(trashfolder)
				diskstat = statvfs(trashfolder)
				free = diskstat.f_bfree * diskstat.f_bsize
				bytesToRemove = self.reserveBytes - free
				print("[Trashcan][CleanTrashTask][work] " + str(trashfolder) + ": Size:", "{:,}".format(trashsize))
				candidates = []
				size = 0
				for root, dirs, files in walk(trashfolder.encode(), topdown=False):  # handle non utf-8 files
					for name in files:  # Don't delete any per-directory config files from .Trash
						if (config.movielist.settings_per_directory.value and name == b".e2settings.pkl"):
							continue
						fn = ospath.join(root, name)
						try:			# file may not exist, if dual delete activities.
							st = stat(fn)
						except FileNotFoundError:
							print("[Trashcan][CleanTrashTask[work]  FileNotFoundError ", fn)
							continue
						if st.st_ctime < self.ctimeLimit or config.usage.movielist_trashcan_days.value == 0:
							enigma.eBackgroundFileEraser.getInstance().erase(fn)
							bytesToRemove -= st.st_size
						else:
							candidates.append((st.st_ctime, fn, st.st_size))
							size += st.st_size
					for name in dirs:		# Remove empty directories if possible
						try:
							rmdir(ospath.join(root, name))
						except Exception as e:
							print("[Trashcan][CleanTrashTask][work] unable to delete directory ", root, "/", name, "   ", e)
							pass
					candidates.sort()
					# Now we have a list of ctime, candidates, size. Sorted by ctime (=deletion time)
					for st_ctime, fn, st_size in candidates:
						if bytesToRemove < 0:
							break
						try:  # file may not exist if simultaneously a network trashcan and main box emptying trash
							enigma.eBackgroundFileEraser.getInstance().erase(fn)
						except:
							pass
						bytesToRemove -= st_size
						size -= st_size
					print("[Trashcan][CleanTrashTask][work] " + str(trashfolder) + ": Size now:", "{:,}".format(size))


class TrashInfo(VariableText, GUIComponent):
	FREE = 0
	USED = 1
	SIZE = 2

	def __init__(self, path, type, update=True):
		GUIComponent.__init__(self)
		VariableText.__init__(self)
		self.type = type
		if update and path != "/media/autofs/":
			self.update(path)

	def update(self, path):
		try:
			total_size = get_size(getTrashFolder(path))
		except OSError:
			return -1

		if self.type == self.USED:
			try:
				if total_size < 10000000:
					total_size = _("%d KB") % (total_size >> 10)
				elif total_size < 10000000000:
					total_size = _("%d MB") % (total_size >> 20)
				else:
					total_size = _("%d GB") % (total_size >> 30)
				self.setText(_("Trashcan:") + " " + total_size)
			except:
				# occurs when f_blocks is 0 or a similar error
				self.setText("-?-")

	GUI_WIDGET = enigma.eLabel
