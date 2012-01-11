#! /usr/bin/python

import subprocess
import sys
import os

import constants as c

def execCommand(cmd, cwd=None):
    print "execCommand: running command: %s" % cmd
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
        print "execCommands: path: %s, proj: %s" % (c.PROJECT_DICT[proj]['dir'], proj)
        if not execCommand(cmd, c.PROJECT_DICT[proj]['dir']):
            print "execCommands: execCommand return False"
            return False
    return True

def createDirIfNotExists():
    for path in c.DIRS:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                print "Failed to create %s - try manually" % path
                sys.exit(1)


