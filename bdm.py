import sys, os, os.path as path, urllib2 as ul, shutil, zipfile, tarfile, mimetypes

def downloadFile(url, file):
	print "downloading '%s'" % url
	try:
		rem = ul.urlopen(url)
		with open(file, 'wb') as loc:
			while(True):
				bytes = rem.read(2**16)
				if len(bytes) == 0:
					break
				loc.write(bytes)
				sys.stdout.write('*')
	finally:
		rem.close()
	print 'downloaded'

def extractFile(file, path, type):
	print "unpacking '%s' to '%s'" % (file, path)

	if type == 'zip':
		with zipfile.ZipFile(file) as zf:
			zf.extractall(path)
	elif type == 'tar.gz':
		with tarfile.open(file, 'r:gz') as tf:
			tf.extractall(path)
	else:
		raise Exception("unknown archive type '%s'" % type)

	print 'unpacked'

class FileSystemResolver:
	def __init__(self, dir, namePattern='{name}-{version}.py'):
		self.dir = dir
		self.namePattern=namePattern
		
	def getDescription(self, name, version):
		name = path.join(self.dir, self.namePattern.format(name=name, version=version))
		dict = {}
		execfile(name, dict)
		return dict['Description']()
		
class HardCodedUrlResolver:
	def getDownloadUrls(self, name, value, description):
		return description.getDownloadUrls()
		
def defaultRepoRoot():
	windowsRepoRoot = path.join(os.environ.get('UserProfile', '.'), '.bdm')
	unixRepoRoot = path.join(os.environ.get('HOME', '.'), '.bdm')
	return {
		'posix': unixRepoRoot,
		'windows': windowsRepoRoot,
		'nt' : windowsRepoRoot
	}.get(os.name)
	
class Package:
	def __init__(self, env, name, version):
		self.env = env
		self.name = name
		self.version = version
		self.description = env.getPackageDescription(name, version)
		
	def getInstallPath(self):
		return path.join(self.env.installedPath, self.env.installedPattern.format(name=self.name, version=self.version))
		
	def getIntermediateInstallPath(self):
		return path.join(self.env.tempPath, self.env.installedPattern.format(name=self.name, version=self.version))
		
	def getIntermediateDownloadPath(self):
		return path.join(self.env.tempPath, self.env.packageFilePattern.format(name=self.name, version=self.version, type=self.description.getArchiveType()))
		
	def getDownloadPath(self):
		return path.join(self.env.packageCachePath, self.env.packageFilePattern.format(name=self.name, version=self.version, type=self.description.getArchiveType()))
		
	def getBuildPath(self):
		return path.join(self.env.tempPath, self.env.buildDirPattern.format(name=self.name, version=self.version))
		
	def download(self):
		for url in self.env.urlResolver.getDownloadUrls(self.name, self.version, self.description):
			if path.exists(self.getDownloadPath()):
				print "package '%s-%s' is already downloaded" % (self.name, self.version)
				return
			
			if path.exists(self.getIntermediateDownloadPath()):
				print "removing '%s'" % self.getIntermediateDownloadPath()
				os.remove(self.getIntermediateDownloadPath())
			
			try:
				downloadFile(url, self.getIntermediateDownloadPath())
				break
			finally:
				pass
			
		os.rename(self.getIntermediateDownloadPath(), self.getDownloadPath())
		
	def deploy(self):
		def shutilOnError(func, path, exc_info):
			"""
			Error handler for ``shutil.rmtree``.

			If the error is due to an access error (read only file)
			it attempts to add write permission and then retries.

			If the error is for another reason it re-raises the error.

			Usage : ``shutil.rmtree(path, onerror=shutilOnError)``
			"""
			import stat
			if not os.access(path, os.W_OK):
				# Is the error an access error ?
				os.chmod(path, stat.S_IWUSR)
				func(path)
				print "onerror"
			else:
				raise
			
		self.download()
			
		if path.exists(self.getBuildPath()):
			print "removing '%s'" % self.getBuildPath()
			shutil.rmtree(self.getBuildPath(), onerror=shutilOnError)
			
		extractFile(self.getDownloadPath(), self.getBuildPath(), self.description.getArchiveType())
		
		if path.exists(self.getIntermediateInstallPath()):
			print "removing '%s'" % self.getIntermediateInstallPath()
			shutil.rmtree(self.getIntermediateInstallPath())
		
		print 'installing'
		self.description.install(self.getBuildPath(), self.getIntermediateInstallPath(), self.env.toolchain)
		
		os.rename(self.getIntermediateInstallPath(), self.getInstallPath())
		print 'deployed'
			
	def getIncludePaths(self):
		return [path.join(self.getInstallPath(), dir) for dir in self.description.getIncludePaths()]
		
	def getLibPaths(self):
		return [path.join(self.getInstallPath(), dir) for dir in self.description.getLibPaths()]
		
	def getDependencies(self):
		return self.description.getDependencies()

class Environment:
	def __init__(self, artifactResolvers, urlResolver=HardCodedUrlResolver(), repoRoot=defaultRepoRoot(), toolchain='gcc'):
		self.repoRoot=repoRoot
		self.toolchain = toolchain
		self.artifactResolvers=artifactResolvers
		self.urlResolver=urlResolver
		self.packageCachePath=path.join(repoRoot, 'packages')
		self.installedPath=path.join(repoRoot, 'installed')
		self.tempPath=path.join(repoRoot, 'temp')
		self.packageFilePattern = '{name}-{version}.{type}'
		self.installedPattern = '{name}-{version}'
		self.buildDirPattern = '{name}-{version}_build'
		
		if not path.exists(self.packageCachePath):
			os.makedirs(self.packageCachePath)
			
		if not path.exists(self.installedPath):
			os.makedirs(self.installedPath)
			
		if not path.exists(self.tempPath):
			os.makedirs(self.tempPath)
		
	def getPackageDescription(self, name, version):
		try:
			return (res for res in (res.getDescription(name, version) for res in self.artifactResolvers) if res != None).next()
		except StopIteration:
			raise Exception("can't find dependency '%s-%s'" % (name, version))
		
	def requirePackage(self, name, version):
		package = Package(self, name, version)
		
		if path.exists(package.getInstallPath()):
			print "package '%s-%s' is already installed" % (name, version)
			return package
		
		for depName, depVersion in package.getDependencies():
			print "checking dependency '%s-%s'" % (depName. depVersion)
			self.requirePackage(depName, depVersion)
			
		package.deploy()
			
		return package