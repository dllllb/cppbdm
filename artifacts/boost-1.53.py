import subprocess as sp, os.path

class Description:
    def __init__(self, env):
        self.env = env

    def getArchiveType(self):
        return 'tar.gz'
    
    def getDownloadUrls(self):
        return ['http://sourceforge.net/projects/boost/files/boost/1.53.0/boost_1_53_0.tar.gz/download']
        
    def getDependencies(self):
        return []
        
    def getIncludePaths(self):
        if self.env.config == 'mingw':
            return [path.join('include', 'boost_1_53_0')]
        else:
            return ['include']
        
    def getLibPaths(self):
        return ['lib']
    
    def getBinPaths(self):
        return []
        
    def install(self, buildPath, targetPath):
        if self.env.config == 'mingw':
            self.install_mingw(buildPath, targetPath)
        else:
            self.install_unix(buildPath, targetPath)

    def install_mingw(self, buildPath, targetPath):
        workDir = os.path.join(buildPath, 'boost_1_53_0')
                
        sp.check_call(['cmd', '/C', '.\\bootstrap.bat mingw'], cwd=workDir)
        sp.check_call(['%s\\bjam' % workDir,
                       'toolset=gcc',
                       'install',
                       '--prefix=%s' % targetPath], cwd=workDir)

    def install_unix(self, buildPath, targetPath):
        workDir = os.path.join(buildPath, 'boost_1_53_0')
        
        bootstrapCommand = ['./bootstrap.sh', '--prefix=%s' % targetPath]
        
        sp.check_call(['bash', '-c', ' '.join(bootstrapCommand)], cwd=workDir)
        sp.check_call(['%s/bjam' % workDir, 'install'], cwd=workDir)