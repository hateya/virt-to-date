#! /usr/bin/python

import os
import glob
import sys
import commands
import subprocess
import optparse


''' Constants '''

EXT_YUM = ['/usr/bin/yum', 'install', '-y']
EXT_GIT_STASH = ['/usr/bin/git', 'stash']
EXT_GIT_PULL = ['/usr/bin/git', 'pull']
EXT_RPMBUILD = ['rpm', '-ba', '--buildroot']
EXT_GIT_CLONE = ['/usr/bin/git', 'clone', '-q']
EXT_WGET = ['/usr/bin/wget', '-r', '-l1', '-H', '-t1', '-nd', '-N', '-q','-np', '-A.rpm', '-erobots=off']
EXT_REPO_NAME = 'upstream-repo'
EXT_HTTPD_STOP = ['/sbin/service', 'httpd', 'stop']
EXT_HTTPD_START= ['/sbin/service', 'httpd', 'start']
EXT_CREATE_YUM_REPO = ['/usr/bin/createrepo']

P_HOMEF = os.getenv('HOME')
P_VDSM = ''.join([P_HOMEF,'/git/','vdsm/'])
P_LIBVIRT = ''.join([P_HOMEF,'/git/','libvirt/'])
P_ENGINE = ''.join([P_HOMEF,'/git/','ovirt-engine/'])
P_ENGINE_CLI = ''.join([P_HOMEF,'/git/','ovirt-engine-cli/'])
P_ENGINE_PSDK = ''.join([P_HOMEF,'/git/','ovirt-engine-python/'])
P_LVM2 = ''.join([P_HOMEF,'/git/','lvm2/'])
P_QEMU = ''.join([P_HOMEF,'/git/','qemu/'])
P_SPICE = ''.join([P_HOMEF,'/git/','spice/'])
P_LOCAL_YUM = ''.join(['/var/www/html/', EXT_REPO_NAME])
P_RPMBUILD = ''.join([P_HOMEF, '/rpmbuild/'])
P_RPM_BUILDROOT = ''.join([P_RPMBUILD, '/BUILDROOT/'])
P_RPM_SOURCES= ''.join([P_RPMBUILD, '/SOURCES/'])
P_RPM_SPECS = ''.join([P_RPMBUILD, '/SPECS/'])
P_RPM_BUILD = ''.join([P_RPMBUILD, '/BUILD/'])
P_RPM_SRPMS= ''.join([P_RPMBUILD, '/SRPMS/'])
P_RPM_RPMS = ''.join([P_RPMBUILD, '/RPMS/'])
P_RPM_X86_64= ''.join([P_RPM_RPMS, '/x86_64/'])
P_RPM_NOARCH= ''.join([P_RPM_RPMS, '/noarch/'])

DIRS = (P_HOMEF, P_VDSM, P_LIBVIRT,
        P_ENGINE, P_ENGINE_CLI, P_ENGINE_PSDK,
        P_LVM2, P_QEMU, P_SPICE,
        P_LOCAL_YUM, P_RPMBUILD, P_RPM_BUILDROOT,
        P_RPM_RPMS, P_RPM_SPECS, P_RPM_SRPMS, P_RPM_BUILD,
        P_RPM_X86_64, P_RPM_SOURCES, P_RPM_NOARCH)

conf_projectDict = { 'vdsm':{'url':'git://gerrit.ovirt.org/vdsm','dir':'/usr/local/git/vdsm/', 'buildFromGit': 'yes', 'cmds': (['./autogen.sh', '--system'],['./configure'], ['make', 'clean'], ['make', 'rpm'])},
                 'libvirt':{'url':'git://libvirt.org/libvirt.git','dir':'/usr/local/git/libvirt/', 'buildFromGit': 'yes', 'cmds': (['./autogen.sh', '--system'],['make'], ['make', 'dist'])},
                 'qemu':{'url':'git://git.kernel.org/pub/scm/virt/kvm/kvm.git','dir':'/usr/local/git/qemu-kvm/', 'buildFromGit': 'no', 'cmds': (['./configure'],['make'],['make', 'install'])},
                 'multipath':{'url':'http://git.opensvc.com/multipath-tools/.git','dir':'/usr/local/git/multipath/', 'buildFromGit': 'yes'},
                 'lvm2':{'url':'git://sourceware.org/git/lvm2','dir':'/usr/local/git/lvm2', 'buildFromGit': 'no'},
                 'ovirt-engine':{'url':'git://gerrit.ovirt.org/ovirt-engine','dir':'/usr/local/git/ovirt-engine/','buildFromGit': 'yes'}}

conf_preReqPkgs = ['make','createrepo', 'dwarves','tree' ,'gdb', 'gcc', 'autofs', 'samba-common','wget',
                'automake', 'git', 'pyflakes', 'rpm-build', 'redhat-rpm-config',
                'httpd','libtool','gettext-devel','glibc','libxml2-python', 'libxml2-devel','gnutls-devel',
                'python-devel','libnl-devel','xhtml1-dtds','createrepo','httpd','readline-devel',
                'ncurses-devel', 'augeas', 'libudev-devel', 'libpciaccess-devel', 'yajl-devel', 'sanlock-devel',
                'libpcap-devel', 'avahi-devel', 'parted-devel' ,'device-mapper-devel', 'numactl-devel', 'libcap-ng-devel',
                'libssh2-devel', 'libblkid-devel','libselinux-devel','cyrus-sasl-devel', 'xen-devel',
                'netcf-devel', 'libcurl-devel', 'libwsman-devel', 'audit-libs-devel', 'systemtap-sdt-devel','radvd','ebtables']

HOSTS = []
REPO_NAME = 'upstream.repo'
REPO_PATH = DIRS[8]

FEDORA_PKGS = {'sanlock':'11619','systemd':'10477',
               'pm-utils':'580', 'pkgconfig':'326',
               'udev':'36', 'iptables': '703','ebtables': '1638',
               'iproute': '161', 'pm-utils': '580',
               'qemu': '3685', 'cyrus-sasl': '102',
               'parted': '75', 'iscsi-initiator-utils': '81',
               'polkit': '8535', 'dnsmasq': '1606',
               'libcgroup': '6291','sanlock':'11619',
               'fence-agents': '7793','dracut':'8714',
               'radvd': '452','bridge-utils':'309',
               'glusterfs':'5443','gnutls':'286',
               'xen':'7','netcf':'8190','ceph':'10264',
               'SDL':'590','spice':'10623','openwsman':'6952',
               'lzop':'2481','net-snmp':'137','nfs-utils':'218',
               'perl-Net-Telnet':'1155','perl':'84',
               'pexpect':'3366','python-suds':'7092',
               'seabios':'9765','sg3_utils':'923',
               'telnet':'690','vgabios':'7853',
               'OpenIPMI':'568','gpxe':'8390', 'gdbm':'1042', 'spice':'10623', 'spice-protocol':'10624'}

SITE = 'http://koji.fedoraproject.org/koji/packageinfo?packageID='
BASE = 'http://kojiFEDORA_PKGS.fedoraproject.org/packages/'
POSTFIX = '/x86_64/'
SLASH = '/'

def execCommand(cmd, cwd=None, logging=None, needRoot=False):
    cmdLogging = "execCommand: running command: %s" % cmd
    if logging:
        print cmdLogging
    if needRoot:
        checkIfRoot()
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        (out,err) = p.communicate()
        rc = p.returncode
        if rc == 128:
            raise OSError
        if rc != 0:
            print rc,err
            print "execCommand: exit with rc %s" % rc
            sys.exit(rc)
        print "execCommand: last return, p.returncode: %s" % (p.returncode)
    except OSError:
        raise OSError
    return True

def execCommands(proj, cmds):
    for cmd in cmds:
        print "execCommands: path: %s, proj: %s" % (conf_projectDict[proj]['dir'], proj)
        if not execCommand(cmd, conf_projectDict[proj]['dir']):
            print "execCommands: execCommand return False"
            return False
    return True

def createDirIfNotExists():
    for path in DIRS:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                print "Failed to create %s - try manually" % path
                sys.exit(1)

def buildPackageIndex():
    pkgIndex = {}
    for pkgDir in DIRS:
        if pkgDir in ('/root/rpmbuild/RPMS/x86_64/','/root/rpmbuild/RPMS/noarch/'):
            FEDORA_PKGS = os.listdir(pkgDir)
            for pkg in FEDORA_PKGS:
                split = pkg.split('-')[0:-2]
                name = '-'.join(split)
                pkgIndex[name] = ''.join([pkgDir,pkg])
    return pkgIndex

def deployRepoToHost(hosts=None):
    if hosts:
        hosts = hosts.split(',')
    else:
        hosts = HOSTS
    for host in hosts:
        cmd = ['scp', createYumRepoFile(), 'root@'+host+':/etc/yum.repos.d/']
        if not execCommand(cmd):
            print "deployRepoToHost: return since execCommand exit with non positive value"


def createYumRepoFile():
    repoFile = ''.join([REPO_PATH,REPO_NAME])
    if os.path.exists(repoFile):
        cmd = ['rm', '-rf', repoFile]
        if not execCommand(cmd):
            print "createYumRepoFile: return since execCommand exit with non positive value"
            sys.exit(1)
    f = open(repoFile ,'a')
    part1 = "^name=Fedora $releasever - $basearch^baseurl=http://"
    hostname = commands.getoutput('hostname')
    ipaddr = commands.getoutput('ifconfig').split('inet addr:')[1].split(' ')[0]
    part2 = "^enabled=1^gpgcheck=0"
    config = ''.join(['[',REPO_NAME.split('.')[0] ,']', part1, ipaddr, '/' ,DIRS[8].split('/')[4], part2])
    parsedConfig = config.split('^')
    for line in parsedConfig:
        f.write(line)
        f.write('\n')
    f.close
    return repoFile


def createYumRepo():
    try:
        if len(os.listdir(DIRS[8])) > 0:
            print "Current repo '%s' is not empty - delelting old files" % DIRS[8]
            for pkg in os.listdir(DIRS[8]):
                cwd = DIRS[8]
                cmd = ['rm', '-f', pkg]
                if not execCommand(cmd, cwd):
                    print "createYumRepo: return since execCommand exit with non positive value"
        pkgIndex = buildPackageIndex()
        if pkgIndex and len(pkgIndex) > 0:
            print "Creating RPM repository under %s" % DIRS[8]
            for pkg in pkgIndex.values():
                cmd = ['cp', pkg, DIRS[8]]
                if not execCommand(cmd):
                    print "execCommands: execCommand return False"
                    return False
        else:
            print "No rpms found under %s" % ' and '.join([DIRS[9],DIRS[10]])
            sys.exit(1)

        if os.path.exists(DIRS[8]) and len(os.listdir(DIRS[8])) > 0:
                cmd = ['createYumRepo', DIRS[8]]
                if not execCommand(cmd):
                    print "execCommands: execCommand return False"
                    return False
                else:
                    print "Restarting httpd service"
                    if not execCommand(EXT_HTTPD_START):
                        print "execCommands: execCommand return False"
                        return False
    except OSError:
        pass

def cleanRepo():
    cmd = ['service', 'httpd', 'stop']
    if not execCommand(cmd):
        print "cleanRepo: return since execCommand exit with non positive value"
        return False
    pkgIndex = buildPackageIndex()
    if len(pkgIndex.values()) > 0:
        for pkg in pkgIndex.values():
            cmd = ['rm', '-f', pkg]
            if not execCommand(cmd):
                print "cleanRepo: return since execCommand exit with non positive value"
                return False
            path = DIRS[8]
            for link in glob.glob(path+'*.tar.gz'):
                if os.path.exists(link):
                    cmd = ['unlink', link]
                    if not execCommand(cmd):
                        print "cleanRepo: return since execCommand exit with non positive value"
                        return False
    return True

def downloadPackage(proj=None):
    print "Starting to download %s" %proj
    lines = []
    rpm = None
    if proj and proj in FEDORA_PKGS.keys():
        idNum = FEDORA_PKGS[proj]

        for line in commands.getoutput(''.join(['curl ', SITE, idNum])).split('\n'):
            if line.find('buildinfo') > 0 or line.find('complete.png') > 0:
                if line.find('complete.png') > 0:
                    break
                rpm = line.split('>')[2].split('<')[0]
    majorVer = rpm.split('-')[-2:-1][0]
    minorVer = rpm.split('-')[-1:][0]
    src = 'src'
    POSTFIX = '/x86_64/'
    if proj in ('dracut','gpxe','perl-Net-Telnet',
                'vgabios','pexpect','python-suds', 'spice-protocol'):
        url = ''.join([BASE,proj,'/',majorVer,'/',minorVer,'/',src])
        cmd = ['wget', '-r', '-l1', '-H', '-t1', '-nd', '-N', '-q','-np', '-A.rpm', '-erobots=off', url, '--directory-prefix=/root/rpmbuild/RPMS/x86_64']
        return execCommand(cmd)
    else:
        url = ''.join([BASE,proj,'/',majorVer,'/',minorVer,'/',POSTFIX])
        cmd = ['wget', '-r', '-l1', '-H', '-t1', '-nd', '-N', '-q','-np', '-A.rpm', '-erobots=off', url, '--directory-prefix=/root/rpmbuild/RPMS/x86_64']
        return execCommand(cmd)

def buildAllProjects(projectsList):
    results = {}
    for projectName in projectsList:
        results[projectName] = buildProject(projectName)
    return results

def buildProject(projectName):
    if projectName == 'libvirt':
        return execCommand(conf_projectDict[projectName]['cmds'][0], conf_projectDict[projectName]['dir']) and \
                execCommand(conf_projectDict[projectName]['cmds'][1], conf_projectDict[projectName]['dir']) and \
                execCommands([['ln', '-sf', max(glob.glob(path+'*tar.gz')), conf_projectDict[projectName]['dir']], ['rpmbuild', '-ba', path+'/libvirt.spec']], conf_projectDict[projectName]['dir']) and \
                execCommand(conf_projectDict[projectName]['cmds'][2], conf_projectDict[projectName]['dir'])
    return execCommands(conf_projectDict[projectName]['cmds'])

    pass
def buildLatestPackages(packagesList)
    for proj in toBuild:
        if conf_projectDict[proj]['buildFromGit'] == 'yes' and not skip == 'skip-git' and proj not in exclude:
            path = conf_projectDict[proj]['dir']
            print "buildLatestPackages: Building needed packages for %s" % proj
            if gitStatus[proj] == 'updated' and proj in ('qemu', 'vdsm'):
                cmds = {'qemu': (['./configure'],['make', '--directory='+path, '-j20'],['make' , '--directory='+path, 'install']),
                        'vdsm': (['./autogen.sh', '--system'],['./configure'],['make', '--directory='+path, 'rpm'])}
                if not execCommands(proj, cmds[proj]):
                    print "buildLatestPackages: return since execCommands exit with non positive value"
                    return False
            elif gitStatus[proj] == 'updated' and proj in ('libvirt'):
                cmds = (['./autogen.sh', '--system'],['make','--directory='+path],
                        ['make', '--directory='+path, 'dist'])
                if execCommands(proj, cmds):
                    cmds = (['ln', '-sf', max(glob.glob(path+'*tar.gz')), DIRS[11]],
                            ['rpmbuild', '-ba', path+'/libvirt.spec'])
                    if not execCommands(proj, cmds):
                        print "buildLatestPackages: return since execCommands exit with non positive value"
                        return False
        elif not skip == 'skip-web':
            to_download = [pkg for pkg in FEDORA_PKGS.keys() if pkg not in exclude]
            for pkg in to_download:
                if not downloadPackage(pkg):
                    print "buildLatestPackages: return since downloadPackage exit with non positive value"
                    return False

def installNeededPackages():
    return execCommand(EXT_YUM + conf_preReqPkgs, needRoot=True)

def refreshGitRepo(projList=None, exclude=[]):
    gitStatus = {}
    if not exclude:
        exclud = []
    if projList:
        projList = projList.split(',')
    else:
        projList = conf_projectDict.keys()
    for name, build in conf_projectDict.iteritems():
        if build['buildFromGit'] == 'yes' and name in projList:
            if name not in exclude:
                try:
                    git = conf_projectDict[name]
                    path = git['dir']
                    cmd = ['git', 'stash']
                    execCommand(cmd, path)
                    cmd = ['git', 'pull']
                    execCommand(cmd, path)
                    gitStatus[name] = 'updated'
                except OSError:
                    print "ERROR: Unable to refresh GIT repos; consider running --build-git first"
                    sys.exit(1)
    return gitStatus

def cloneGitRepository(projectName):
    return execCommand(EXT_GIT_CLONE + [conf_projectDict[projectName]['url']],conf_projectDict[projectName]['dir'])

def pullGitRepository(projectName):
    return execCommand(EXT_GIT_PULL ,conf_projectDict[projectName]['dir'], logging=True)

def stashGitRepository(projectName):
    return execCommand(EXT_GIT_STASH ,conf_projectDict[projectName]['dir'])

def updateAllGitRepositories(projectsList):
    resutls = {}
    for projectName in projectsList:
        print "updating package %s" % (projectName)
        resutls[projectName] = updateGitRepository(projectName)
    return resutls

def updateGitRepository(projectName):
    if not os.path.exists(''.join([conf_projectDict[projectName]['dir'],'/.git'])):
        return cloneGitRepository(projectName)
    else:
        return stashGitRepository(projectName) and pullGitRepository(projectName)

def checkIfGitExists(projList=None):
    if projList:
        projList = projList.split(',')
    else:
        projList = conf_projectDict.keys()
    to_clone = []
    for name in projList:
        if conf_projectDict[name]['dir']:
            git = conf_projectDict[name]
            gitConfig = ''.join(git['dir'] + '/.git')
            if not os.path.exists(gitConfig):
                to_clone.append(name)
    return to_clone

def createGitRepos(projList=None, exclude=None):
    if projList:
        projList = projList.split(',')
    else:
        projList = conf_projectDict.keys()
    if exclude:
        excludeList = exclude.split(',')
    else:
        exclude = []
    to_clone = checkIfGitExists()
    if len(to_clone) > 0:
        neededProjs = [ proj for proj in to_clone if proj in projList and proj not in exclude ]
        for proj in neededProjs:
            print "Cloning GIT repo for %s" %proj
            cmd = ['git', 'clone','-q', conf_projectDict[proj]['url'], conf_projectDict[proj]['dir']]
            pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print "Creating %s git repo using command: %s" %(proj,' '.join(cmd))
            (out, err) = pr.communicate()
            if err and "exist" not in err:
                print "Failed cloning %s git repo - try manually" % proj
                sys.exit(1)
    else:
        print "GIT already deployed for project %s" %projList

        return True

def mandatoryPhases():
   createDirIfNotExists()
   installNeededPackages()
   return True

def runAllPhases():
    if not mandatoryPhases():
        print "mandatoryPhases: return since mandatoryPhases exit with non positive value"
    createGitRepos()
    buildLatestPackages(skip='')
    createYumRepo()

def parser():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option('--build-all', dest='build_all',
            action='store_true', help='Clone projects upstream GITs, build rpms, fetch latest packages from KOJI server, and create local Yum repo')
    parser.add_option('--clone-git', dest='clone_git',
            action='store_true', help='Clone projects upstream upstream GIT - Can be used with --exclude or --projects options')
    parser.add_option('--projects', dest='projList',
            nargs=1, help='')
    parser.add_option('--run-pre-requisite', dest='run_preReq',
            action='store_true', help='Install needed packages for compilation, build and deploy needed projects')
    parser.add_option('--build-latest', dest='build_latest',
            action='store_true', help='Refresh current GIT repos, build latest packages, rebuilds local Yum repository')
    parser.add_option('--skip-web', dest='skip_web',action='store_true', help='')
    parser.add_option('--skip-git', dest='skip_git',action='store_true', help='')
    parser.add_option('--exclude', dest='exclude',
            nargs=1, help='')
    parser.add_option('--deploy-repo', dest='deploy',
           action='store_true',help='Deploy current Yum repo file for selected hosts')
    parser.add_option('--hosts', dest='hosts',
           nargs=1, help='')
    parser.add_option('--list-projects', dest='listPorjects',
           action='store_true',help='Display a list of supported Projects')
    parser.add_option('--create--yum-repo', dest='createYumRepo',
           action='store_true',help='Display a list of current packages in yum repository')
    options, args = parser.parse_args()
    if not True in set(options.__dict__.values()):
        parser.print_help()
    return (options, args)

def checkIfRoot():
    import getpass
    if os.getuid() != 0:
        print "Error: insufficient permissions for user %s, you must run with user root for running Yum commands" %getpass.getuser()
        sys.exit(1)

def main(options, args=None):
    skip = ''
    projList = None
    exclude = None
    if options.build_all:
        runAllPhases()
    if options.clone_git:
        if options.projList:
            projList = options.projList
        if options.exclude:
            exclude = options.exclude
        if not mandatoryPhases():
            print "buildGitFailed: return since mandatoryPhases exit with non positive value"
        createGitRepos(projList=projList, exclude=exclude)
    if options.run_preReq:
        installNeededPackages()
    if options.build_latest:
        if options.projList or options.exclude:
            if options.projList:
                projList = options.projList
            if options.exclude:
                exclude = options.exclude
            if options.skip_web:
                skip = 'skip-web'
            if options.skip_git:
                skip = 'skip-git'
        if not mandatoryPhases():
            print "mandatoryPhases: return since mandatoryPhases exit with non positive value"
        buildLatestPackages(projList=projList, skip=skip, exclude=exclude)
        createYumRepo()
    if options.deploy:
        hosts = None
        if options.hosts:
            hosts = options.hosts
        deployRepoToHost(hosts=hosts)
    if options.createYumRepo:
        createYumRepo()
    if options.listPorjects:
        print "\n---------------------------"
        print "List of supported Projects:"
        print "---------------------------"
        for proj in conf_projectDict.keys():
            print "   Project: %s" % proj
        print "--------------------------"

def createPackagesList():
    options, args = parser()
    defaultList = conf_projectDict.keys() 
    if options.projList:
        defaultList = options.projList.split(',')
    elif options.exclude:
        toExclude = options.exclude.split(',')
        for packageName in toExclude:
            del defaultList[defaultList.index(packageName)]
    return defaultList

def flow():
    packagesList = createPackagesList()
    stepsList = createStepsList()
    #installDependencies()
    for step in stepsList:
        print updateAllGitRepositories(packagesList)
        print buildAllProjects()
        print createYumRepo()


def createStepsList():
    options, args = parser()
    defaultStepsList = [] 
    if options.clone_git:
        defaultStepsList.append([''])
    return defaultStepsList




if __name__ == '__main__':
    print flow()




  --build-all          Clone projects upstream GITs, build rpms, fetch latest
                       packages from KOJI server, and create local Yum repo
  --build-git          Clone projects upstream upstream GIT - Can be used with
                       --exclude or --projects options
  --install            Install needed packages allowing compile, build and
                       deploy needed packages
  --build-latest       Refresh current GIT repos, build latest packages,
                       rebuilds local Yum repository
  --skip-git           
  --deploy-repo        Deploy current Yum repo file for selected hosts
  --create-repo        Display a list of current packages in yum repository

