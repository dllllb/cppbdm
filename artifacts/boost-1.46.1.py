import subprocess as sp, os.path
from cppbdm.scons_tools import toMsysPath, replaceInFile

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
        
        prefix = targetPath
        
        if env.config == 'mingw':
            prefix = toMsysPath(targetPath)
        
        bootstrapCommand = ['./bootstrap.sh', '--prefix=%s' % prefix]
        
        if env.config == 'mingw':
            bootstrapCommand.append('--with-toolset=mingw')
            
        bootstrapCmd = ' '.join(bootstrapCommand)
        print 'bootstrap command: "%s"' % bootstrapCmd
            
        sp.check_call(['bash', '-c', bootstrapCmd], cwd=workDir)
        
        #fix incorrectly generated jam file
        if env.config == 'mingw':
            replaceInFile('%s/project-config.jam' % workDir, "mingw", "gcc")
        
        sp.check_call(['%s/bjam' % workDir, 'install'], cwd=workDir)