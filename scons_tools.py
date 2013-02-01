import os, os.path, fnmatch, platform
from SCons.Environment import *
from SCons.Builder import *
from SCons.Script.SConscript import *

def configNameByPlatform():
    return {
        'posix': 'unix'
    }.get(os.name, 'windows')

class ExtEnviroment(Environment):
    def __init__(self,
                 args,
                 configDefault=configNameByPlatform(),
                 targetDefault="debug",
                 duplicateSrc=False):
        
        Environment.__init__(self, ENV = os.environ)
        
        self.config = args.get('config', configDefault)
        self.target = args.get('target', targetDefault)
        self.srcPath = 'src'
        self.buildPath = 'build'
        self.SConsignFile(".sconsign")
        
        self.targetBuildDir = os.path.join(self.buildPath, self.config, self.target )
        self.BuildDir(self.targetBuildDir, self.srcPath, duplicate=duplicateSrc)

        configureEnv(self, self.config)
            
    def configure(self, configurer):
        configurer(self)
        
    def getTarget(self):
        return self.target
    
    def setCppRoot(self, path):
        self.cppRoot = path
        
    def cppRootSubdir(self, *pathParts):
        res = self.cppRoot
        for path in pathParts:
            res = os.path.join(res, path)
        return res
        
    def buildFiles(self, list):
        return changeHead(list, 'src', self.targetBuildDir)
        
    def findCppFiles(self, *paths):
        return self.findBuildFiles('*.cpp', *paths)
    
    def cppFiles(self, *paths):
        return self.buildFiles(paths)
    
    def findBuildFiles(self, sign, *paths):
        return self.buildFiles(filesBySign( sign, *paths))
    
    def appendCppExternalIncludes(self, *paths):
        includes = [self.cppRootSubdir('include', path) for path in paths]
        self.Append(CPPPATH=includes)
        
    def appendCppBuildPathIncludes(self, *paths):
        includes = [os.path.join(self.targetBuildDir, path) for path in paths]
        self.Append(CPPPATH=includes)
        
    def appendCppIncludes(self, *paths):
        self.Append(CPPPATH=paths)
        
    def appendCppIncludeList(self, paths):
        self.Append(CPPPATH=paths)
        
    def appendCppLibs(self, *names):
        self.Append(LIBS=names)
        
    def appendCppLibPaths(self, *paths):
        self.Append(LIBPATH=paths)
        
    def appendCppLibPathList(self, paths):
        self.Append(LIBPATH=paths)
        
    def appendCppFlags(self, *flags):
        self.Append(CXXFLAGS=flags)
        
    def testAlias(self, program, name='test'):
        self.AlwaysBuild(self.Alias(name, [program], [program[0].abspath]))
        
    def appendDynamicLibPathList(self, paths):
        self.PrependENVPath(getDynLibEnvVariable(), ':'.join(paths))
        
def getDynLibEnvVariable():
    return {
        'Darwin': 'DYLD_LIBRARY_PATH',
        'Windows': 'PATH',
        'Linux': 'LD_LIBRARY_PATH'
    }.get(platform.system())
        
def filesBySign(pattern, *paths):
    for path in paths:
        for (dir, subdirs, files) in os.walk(path):
            for name in fnmatch.filter(files, pattern):
                yield os.path.join(dir, name)
                
def configureEnv(env, name):
    configurer = {
        'mingw': mingwConfigurer,
        'windows': windowsConfigurer,
        'unix': unixConfigurer,
        'unix-stlport': unixStlPortConfigurer,
        'macports': macportsConfigurer
    }.get(name)

    if configurer == None:
        raise ValueError('"%s" configuration is not supported' % self.config)
        
    env.configure(configurer)
    
def changeHead(iList, old, new):
    return [new + tmp[len(old):] for tmp in iList]
    
def gccConfigurer(env):
    target = env.getTarget()
    if target == 'release-opt':
        env.appendCppFlags('-O3', '-DNDEBUG')
    elif target == 'release':
        env.appendCppFlags('-g', '-O2')
    elif target == 'debug':
        env.appendCppFlags('-g')
    else:
        raise ValueError('wrong target "%s"' % target)
            
    env.appendCppFlags( '-Wall' )
    
def windowsCppRootConfigurer(env):
    cppRoot = os.environ.get('cpproot', 'c:\\cpproot')
    env.setCppRoot(cppRoot)
    env.appendCppIncludes(env.cppRootSubdir( 'include' ))
    env.appendCppLibPaths(env.cppRootSubdir('lib'))
        
def mingwConfigurer(env):
    env.Append(tools=['mingw'])
    #env.configure(windowsCppRootConfigurer)
    env.configure(gccConfigurer)
    
def windowsConfigurer(env):
    vsRoot = os.environ.get('VS_ROOT', 'c:\\VS')
    env.Append(ENV={'PATH' : '%s;%s\\VC\\bin;%s\\Common7\IDE' % (os.environ.get('PATH'), vsRoot, vsRoot)})
    sdkRoot = os.environ.get('WIN_SDK_ROOT', 'c:\\WIN_SDK')
    env.appendCppIncludes(sdkRoot+'\\Include', vsRoot+'\\VC\\include')
    env.appendCppLibPaths(sdkRoot+'\\Lib', vsRoot+'\\VC\\lib')
        
    env.configure(windowsCppRootConfigurer)
    
def unixStlPortConfigurer(env):
    env.appendCppExternalIncludes('stlport')
    env.appendCppLibs('stlport')
    env.appendCppFlags('-ftemplate-depth-50', '-D_REENTRANT')

    #stlport 4.5 __opr bug fix
    env.appendCppFlags('-D__opr=__operNameThatDoesNotConflictWithEgcs')
    
    env.configure(unixConfigurer)
    
def unixConfigurer(env):
    env.setCppRoot('/usr')
    env.configure(gccConfigurer)

def macportsConfigurer(env):
    cppRoot = '/opt/local/include'
    env.setCppRoot(cppRoot)
    env.appendCppIncludes(cppRoot)
    env.appendCppLibPaths('/opt/local/lib')
    env.configure(gccConfigurer)
    
def iterateDirs(path):
    while True:
        path, tail = os.path.split(path)
        if tail == '': break
        yield tail
        
def toMsysPath(winPath):
    drive, dirs = os.path.splitdrive(winPath)
    if drive.endswith(':'): drive = drive[:-1]
    return '/' + '/'.join([drive]+[dir for dir in iterateDirs(dirs)][::-1])
    
def replaceInFile(path, old, new):
    with open(path, "r") as f:
        contents = f.read()
        contents = contents.replace(old, new)
    with open(path, "w") as f:
        f.write(contents)