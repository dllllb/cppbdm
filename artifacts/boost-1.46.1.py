import subprocess as sp, os.path

class Description:
    def __init__(self, env):
        self.env = env

    def getArchiveType(self):
        return 'tar.gz'
    
    def getDownloadUrls(self):
        return ['http://sourceforge.net/projects/boost/files/boost/1.46.1/boost_1_46_1.tar.gz/download']
        
    def getDependencies(self):
        return []
        
    def getIncludePaths(self):
        return ['include']
        
    def getLibPaths(self):
        return ['lib']
    
    def getBinPaths(self):
        return []
        
    def install(self, buildPath, targetPath):
        workDir = os.path.join(buildPath, 'boost_1_46_1')
        
        bootstrapCommand = ['./bootstrap.sh', '--prefix=%s' % targetPath]
                    
        sp.check_call(['bash', '-c', ' '.join(bootstrapCommand)], cwd=workDir)        
        sp.check_call(['%s/bjam' % workDir, 'install'], cwd=workDir)