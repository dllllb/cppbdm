import subprocess as sp, os.path

class Description:
    def getArchiveType(self):
        return 'tar.gz'
    
    def getDownloadUrls(self):
        return ['http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz']
        
    def getDependencies(self):
        return []
        
    def getIncludePaths(self):
        return ['include']
        
    def getLibPaths(self):
        return ['lib']
    
    def getBinPaths(self):
        return ['bin']
        
    def install(self, buildPath, targetPath, env):
    	workDir = os.path.join(buildPath, 'Python-2.7.3')
        sp.check_call(['bash', '-c', './configure --prefix=%s' % targetPath], cwd=workDir)
        sp.check_call('make', cwd=workDir)
        #sp.check_call(['make', 'test'], cwd=workDir)
        sp.check_call(['make', 'install'], cwd=workDir)