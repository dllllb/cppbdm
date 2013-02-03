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
        
        if env.config == 'mingw':
            bootstrapCommand.append('--with-toolset=mingw')
            
        sp.check_call(['bash', '-c', ' '.join(bootstrapCommand)], cwd=workDir)

        #mingw build configuration fix
        if env.config == 'mingw':
            with open('%s/project-config.jam' % workDir, 'w') as f:
                conf =  'import option ;\n'
                conf += 'using gcc ;\n'
                conf += 'project : default-build <toolset>gcc ;\n'
                conf += 'option.set prefix : %(targetPath)s ;\n'
                conf += 'option.set exec-prefix : %(targetPath)s ;\n'
                conf += 'option.set libdir : %(targetPath)s\\lib ;\n'
                conf += 'option.set includedir : %(targetPath)s\\include ;\n'
                f.write(conf % {'targetPath' : targetPath})
        
        sp.check_call(['%s/bjam' % workDir, 'install'], cwd=workDir)