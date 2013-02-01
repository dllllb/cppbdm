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
        
    def install(self, buildPath, targetPath, env):
        workDir = os.path.join(buildPath, 'boost_1_43_0')
        bootstrapCommand = ['./bootstrap.sh', '--prefix=%s' % targetPath]
        
        if env.buildEnv == 'mingw':
            bootstrapCommand.append('--with-toolset=mingw')
        
        print ' '.join(bootstrapCommand)
        sp.check_call(['bash', '-c', ' '.join(bootstrapCommand)], cwd=workDir)
        
        #fix incorrectly generated jam file
        if env.buildEnv == 'mingw':
            with open('%s/project-config.jam' % workDir, "r") as conf:
                contents = conf.read()
                contents = contents.replace("mingw", "gcc")
            with open('%s/project-config.jam' % workDir, "w") as conf:
                conf.write(contents)
        
        sp.check_call(['%s/bjam' % workDir, 'install'], cwd=workDir)