#! /usr/bin/python

import os
import glob
import sys
import commands
import subprocess
import optparse

import constants as c
import utils


def buildPackageIndex():
    pkgIndex = {}
    for pkgDir in c.DIRS:
        if pkgDir in ('/root/rpmbuild/RPMS/x86_64/','/root/rpmbuild/RPMS/noarch/'):
            pkgs = os.listdir(pkgDir)
            for pkg in pkgs:
                split = pkg.split('-')[0:-2]
                name = '-'.join(split)
                pkgIndex[name] = ''.join([pkgDir,pkg])
    return pkgIndex

def isPackageInstalled(host):
    pkgDict = {}
    rpm_q = ['rpm', '-q', ' '.join(buildPackageIndex().keys())]
    cmd = ['ssh', 'root@'+host, ' '.join(rpm_q)]
    out = commands.getoutput(' '.join(cmd))
    for pkg in out.split('\n'):
        if pkg.endswith('is not installed'):
            pkgName = pkg.split(' ')[1]
            pkgDict[pkgName] = 'toInstall'
        else:
            pkgDict[pkgName] = 'toUpgrade'
    return pkgDict


def deployRepoToHost(hosts=None):
    if hosts:
        hosts = hosts.split(',')
    else:
        hosts = c.HOSTS
    for host in hosts:
        cmd = ['scp', createRepoFile(), 'root@'+host+':/etc/yum.repos.d/']
        if not utils.execCommand(cmd):
            print "deployRepoToHost: return since utils.execCommand exit with non positive value"


def createRepoFile():
    repoFile = ''.join([c.REPO_PATH,c.REPO_NAME])
    if os.path.exists(repoFile):
        cmd = ['rm', '-rf', repoFile]
        if not utils.execCommand(cmd):
            print "createRepoFile: return since utils.execCommand exit with non positive value"
            sys.exit(1)
    f = open(repoFile ,'a')
    part1 = "^name=Fedora $releasever - $basearch^baseurl=http://"
    hostname = commands.getoutput('hostname')
    ipaddr = commands.getoutput('ifconfig').split('inet addr:')[1].split(' ')[0]
    part2 = "^enabled=1^gpgcheck=0"
    config = ''.join(['[',c.REPO_NAME.split('.')[0] ,']', part1, ipaddr, '/' ,c.DIRS[8].split('/')[4], part2])
    parsedConfig = config.split('^')
    for line in parsedConfig:
        f.write(line)
        f.write('\n')
    f.close
    return repoFile


def createRepo():
    try:
        if len(os.listdir(c.DIRS[8])) > 0:
            print "Current repo '%s' is not empty - delelting old files" % c.DIRS[8]
            for pkg in os.listdir(c.DIRS[8]):
                cwd = c.DIRS[8]
                cmd = ['rm', '-rf', pkg]
                if not utils.execCommand(cmd, cwd):
                    print "createRepo: return since utils.execCommand exit with non positive value"
        pkgIndex = buildPackageIndex()
        if pkgIndex and len(pkgIndex) > 0:
            print "Creating RPM repository under %s" % c.DIRS[8]
            for pkg in pkgIndex.values():
                cmd = ['cp', pkg, c.DIRS[8]]
                if not utils.execCommand(cmd):
                    print "utils.execCommands: utils.execCommand return False"
                    return False
        else:
            print "No rpms found under %s" % ' and '.join([c.DIRS[9],c.DIRS[10]])
            sys.exit(1)

        if os.path.exists(c.DIRS[8]) and len(os.listdir(c.DIRS[8])) > 0:
                cmd = ['createrepo', c.DIRS[8]]
                if not utils.execCommand(cmd):
                    print "utils.execCommands: utils.execCommand return False"
                    return False
                else:
                    print "Restarting httpd service"
                    cmd = ['/etc/init.d/httpd', 'restart']
                    if not utils.execCommand(cmd):
                        print "utils.execCommands: utils.execCommand return False"
                        return False
    except OSError:
        pass

def cleanRepo():
    cmd = ['service', 'httpd', 'stop']
    if not utils.execCommand(cmd):
        print "cleanRepo: return since utils.execCommand exit with non positive value"
        return False
    pkgIndex = buildPackageIndex()
    if len(pkgIndex.values()) > 0:
        for pkg in pkgIndex.values():
            cmd = ['rm', '-rf', pkg]
            if not utils.execCommand(cmd):
                print "cleanRepo: return since utils.execCommand exit with non positive value"
                return False
            path = c.DIRS[8]
            for link in glob.glob(path+'*.tar.gz'):
                if os.path.exists(link):
                    cmd = ['unlink', link]
                    if not utils.execCommand(cmd):
                        print "cleanRepo: return since utils.execCommand exit with non positive value"
                        return False
    return True

def downloadPackage(proj=None):
    print "Starting to download %s" %proj
    lines = []
    rpm = None
    if proj and proj in c.PKGS.keys():
        idNum = c.PKGS[proj]

        for line in commands.getoutput(''.join(['curl ', c.SITE, idNum])).split('\n'):
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
        url = ''.join([c.BASE,proj,'/',majorVer,'/',minorVer,'/',src])
        cmd = ['wget', '-r', '-l1', '-H', '-t1', '-nd', '-N', '-q','-np', '-A.rpm', '-erobots=off', url, '--directory-prefix=/root/rpmbuild/RPMS/x86_64']
        return utils.execCommand(cmd)
    else:
        url = ''.join([c.BASE,proj,'/',majorVer,'/',minorVer,'/',POSTFIX])
        cmd = ['wget', '-r', '-l1', '-H', '-t1', '-nd', '-N', '-q','-np', '-A.rpm', '-erobots=off', url, '--directory-prefix=/root/rpmbuild/RPMS/x86_64']
        return utils.execCommand(cmd)

def buildLatestPackages(skip='', projList=None, exclude=[]):
    toBuild = c.PROJECT_DICT.keys()
    if exclude:
        exclude = exclude.split(',')
    else:
        exclude = []
    if cleanRepo():
        gitStatus = refreshGitRepo(projList=projList, exclude=exclude)
        if projList:
            toBuild = [ proj for proj in c.PROJECT_DICT.keys() if proj in projList]
        for proj in toBuild:
            if c.PROJECT_DICT[proj]['buildFromGit'] == 'yes' and not skip == 'skip-git' and proj not in exclude:
                path = c.PROJECT_DICT[proj]['dir']
                print "buildLatestPackages: Building needed packages for %s" % proj
                if gitStatus[proj] == 'updated' and proj in ('qemu', 'vdsm'):
                    cmds = {'qemu': (['./configure'],['make', '--directory='+path, '-j20'],['make' , '--directory='+path, 'install']),
                            'vdsm': (['./autogen.sh', '--system'],['./configure'],['make', '--directory='+path, 'rpm'])}
                    if not utils.execCommands(proj, cmds[proj]):
                        print "buildLatestPackages: return since utils.execCommands exit with non positive value"
                        return False
                elif gitStatus[proj] == 'updated' and proj in ('libvirt'):
                    cmds = (['./autogen.sh', '--system'],['make','--directory='+path],
                            ['make', '--directory='+path, 'dist'])
                    if utils.execCommands(proj, cmds):
                        cmds = (['ln', '-sf', max(glob.glob(path+'*tar.gz')), c.DIRS[11]],
                                ['rpmbuild', '-ba', path+'/libvirt.spec'])
                        if not utils.execCommands(proj, cmds):
                            print "buildLatestPackages: return since utils.execCommands exit with non positive value"
                            return False
            elif not skip == 'skip-web':
                to_download = [pkg for pkg in c.PKGS.keys() if pkg not in exclude]
                for pkg in to_download:
                    if not downloadPackage(pkg):
                        print "buildLatestPackages: return since downloadPackage exit with non positive value"
                        return False

def installNeededPackages():
    to_install = []
    for pkg in c.NEEDED_PCKGS:
        o = commands.getoutput('rpm -q %s' % pkg)
        if  'not installed' in o:
            to_install.append(pkg)
    if to_install:
        print "Installing Needed packages:\n%s" %', '.join(to_install)
        cmd = ['/usr/bin/yum', 'install', '-y'] + to_install
        if not utils.execCommand(cmd):
            print "installNeededPackages: return since utils.execCommand exit with non positive value"
            return False

def refreshGitRepo(projList=None, exclude=[]):
    gitStatus = {}
    if not exclude:
        exclud = []
    if projList:
        projList = projList.split(',')
    else:
        projList = c.PROJECT_DICT.keys()
    for name, build in c.PROJECT_DICT.iteritems():
        if build['buildFromGit'] == 'yes' and name in projList:
            if name not in exclude:
                try:
                    git = c.PROJECT_DICT[name]
                    path = git['dir']
                    cmd = ['git', 'stash']
                    utils.execCommand(cmd, path)
                    cmd = ['git', 'pull']
                    utils.execCommand(cmd, path)
                    gitStatus[name] = 'updated'
                except OSError:
                    print "ERROR: Unable to refresh GIT repos; consider running --build-git first"
                    sys.exit(1)
    return gitStatus

def checkIfGitExists(projList=None):
    if projList:
        projList = projList.split(',')
    else:
        projList = c.PROJECT_DICT.keys()
    to_clone = []
    for name in projList:
        if c.PROJECT_DICT[name]['dir']:
            git = c.PROJECT_DICT[name]
            gitConfig = ''.join(git['dir'] + '/.git')
            if not os.path.exists(gitConfig):
                to_clone.append(name)
    return to_clone

def createGitRepos(projList=None, exclude=None):
    if projList:
        projList = projList.split(',')
    else:
        projList = c.PROJECT_DICT.keys()
    if exclude:
        excludeList = exclude.split(',')
    else:
        exclude = []
    to_clone = checkIfGitExists()
    if len(to_clone) > 0:
        neededProjs = [ proj for proj in to_clone if proj in projList and proj not in exclude ]
        for proj in neededProjs:
            print "Cloning GIT repo for %s" %proj
            cmd = ['git', 'clone','-q', c.PROJECT_DICT[proj]['url'], c.PROJECT_DICT[proj]['dir']]
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
   utils.createDirIfNotExists()
   installNeededPackages()
   return True

def runAllPhases():
    if not mandatoryPhases():
        print "mandatoryPhases: return since mandatoryPhases exit with non positive value"
    createGitRepos()
    buildLatestPackages(skip='')
    createRepo()

def parser():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option('--build-all', dest='build_all',
            action='store_true', help='Clone projects upstream GITs, build rpms, fetch latest packages from KOJI server, and create local Yum repo')
    parser.add_option('--build-git', dest='build_git',
            action='store_true', help='Clone projects upstream upstream GIT - Can be used with --exclude or --projects options')
    parser.add_option('--projects', dest='projList',
            nargs=1, help='')
    parser.add_option('--install', dest='install',
            action='store_true', help='Install needed packages allowing compile, build and deploy needed packages')
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
    parser.add_option('--create-repo', dest='createRepo',
           action='store_true',help='Display a list of current packages in yum repository')
    options, args = parser.parse_args()
    if not True in set(options.__dict__.values()):
        parser.print_help()
    main(options, args)

def checkIfRoot():
    import getpass
    if os.getuid() != 0:
        print "Error: insufficient permissions for user %s, you must run with user root" %getpass.getuser()
        sys.exit(1)

def main(options, args=None):
    skip = ''
    projList = None
    exclude = None
    checkIfRoot()
    if options.build_all:
        runAllPhases()
    if options.build_git:
        if options.projList:
            projList = options.projList
        if options.exclude:
            exclude = options.exclude
        if not mandatoryPhases():
            print "buildGitFailed: return since mandatoryPhases exit with non positive value"
        createGitRepos(projList=projList, exclude=exclude)
    if options.install:
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
        createRepo()
    if options.deploy:
        hosts = None
        if options.hosts:
            hosts = options.hosts
        deployRepoToHost(hosts=hosts)
    if options.createRepo:
        createRepo()
    if options.listPorjects:
        print "\n---------------------------"
        print "List of supported Projects:"
        print "---------------------------"
        for proj in c.PROJECT_DICT.keys():
            print "   Project: %s" % proj
        print "--------------------------"

if __name__ == '__main__':
    parser()






