import subprocess as sp, os.path

class Description:
	def getArchiveType(self):
		return 'tar.gz'
	
	def getDownloadUrls(self):
		return ['http://sourceforge.net/projects/boost/files/boost/1.43.0/boost_1_43_0.tar.gz/download']
		
	def getDependencies(self):
		return []
		
	def getIncludePaths(self):
		return ['include']
		
	def getLibPaths(self):
		return ['lib']
		
	def install(self, buildPath, targetPath, toolchain):
		workDir = os.path.join(buildPath, 'boost_1_43_0')
		sp.check_call(['bash', '-c', './bootstrap.sh --prefix=%s' % targetPath], cwd=workDir)
		sp.check_call(['./bjam', 'install'], cwd=workDir)