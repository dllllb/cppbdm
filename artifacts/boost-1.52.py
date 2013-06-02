import subprocess as sp, os.path as path, os

class Description:
    def __init__(self, env):
        self.env = env

    def getArchiveType(self):
        return 'tar.gz'
    
    def getDownloadUrls(self):
        return ['http://sourceforge.net/projects/boost/files/boost/1.52.0/boost_1_52_0.tar.gz/download']
        
    def getDependencies(self):
        return []
        
    def getIncludePaths(self):
        if self.env.config == 'mingw':
            return [path.join('include', 'boost-1_52')]
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
        workDir = os.path.join(buildPath, 'boost_1_52_0')
                
        #setting locale in order to get english errors from mingw GCC
        modEnv = os.environ.copy()
        modEnv['LC_ALL'] = 'en_US.UTF-8'
                
        sp.check_call(['cmd', '/C', '.\\bootstrap.bat mingw'], cwd=workDir, env=modEnv)

        #context library is ignored because it requires MS assembler (ml) in path
        sp.check_call([path.join(workDir, 'bjam'),
                       'toolset=gcc',
                       'install',
                       '--without-context',
                       '--prefix=%s' % targetPath], cwd=workDir, env=modEnv)

    def install_unix(self, buildPath, targetPath):
        workDir = os.path.join(buildPath, 'boost_1_52_0')
        
        bootstrapCommand = ['./bootstrap.sh', '--prefix=%s' % targetPath]
        
        sp.check_call(['bash', '-c', ' '.join(bootstrapCommand)], cwd=workDir)
        sp.check_call(['%s/bjam' % workDir, 'install'], cwd=workDir)