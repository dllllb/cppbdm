import subprocess as sp, os.path

class Description:
    def __init__(self, env):
        self.env = env
        
    def getArchiveType(self):
        return 'tar.gz'
    
    def getDownloadUrls(self):
        return ['http://sourceforge.net/projects/boost/files/boost/1.43.0/boost_1_43_0.tar.gz/download']
        
    def getIncludePaths(self):
        return ['include']
        
    def getLibPaths(self):
        return ['lib']
    
    def getBinPaths(self):
        return []
        
    def install(self, buildPath, targetPath):
        workDir = os.path.join(buildPath, 'boost_1_43_0')
        
        python = self.env.requirePackage('python', '2.7.3')
        
        bootstrapCommand = ['./bootstrap.sh',
                            '--prefix=%s' % targetPath,
                            '--with-python-root=%s' % python.getInstallPath()]
            
        sp.check_call(['bash', '-c', ' '.join(bootstrapCommand)], cwd=workDir)
        sp.check_call(['%s/bjam' % workDir, 'install'], cwd=workDir)