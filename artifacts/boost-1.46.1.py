import subprocess as sp, os.path

class Description:
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
        
    def install(self, buildPath, targetPath, env):
        workDir = os.path.join(buildPath, 'boost_1_46_1')
        
        bootstrapCommand = ['./bootstrap.sh', '--prefix=%s' % targetPath]
        
        if env.config == 'mingw':
            bootstrapCommand.append('--with-toolset=mingw')
            
        sp.check_call(['bash', '-c', ' '.join(bootstrapCommand)], cwd=workDir)        
        sp.check_call(['%s/bjam' % workDir, 'install'], cwd=workDir)