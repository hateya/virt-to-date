#! /usr/bin/python


DIRS = ('/usr/local/','/usr/local/git/','/usr/local/git/vdsm/',
        '/usr/local/git/ovirt-engine/','/usr/local/git/lvm2/',
        '/usr/local/git/multipath/','/usr/local/git/libvirt/',
        '/usr/local/git/qemu-kvm/','/var/www/html/upstream-repo/',
        '/root/rpmbuild/RPMS/x86_64/','/root/rpmbuild/RPMS/noarch/',
        '/root/rpmbuild/SOURCES/')

PROJECT_DICT = { 'vdsm':{'url':'git://gerrit.ovirt.org/vdsm','dir':'/usr/local/git/vdsm/', 'buildFromGit': 'yes'},
                 'libvirt':{'url':'git://libvirt.org/libvirt.git','dir':'/usr/local/git/libvirt/', 'buildFromGit': 'yes'},
                 'qemu':{'url':'git://git.kernel.org/pub/scm/virt/kvm/kvm.git','dir':'/usr/local/git/qemu-kvm/', 'buildFromGit': 'no'},
                 'multipath':{'url':'http://git.opensvc.com/multipath-tools/.git','dir':'/usr/local/git/multipath/', 'buildFromGit': 'yes'},
                 'lvm2':{'url':'git://sourceware.org/git/lvm2','dir':'/usr/local/git/lvm2', 'buildFromGit': 'no'},
                 'ovirt-engine':{'url':'git://gerrit.ovirt.org/ovirt-engine','dir':'/usr/local/git/ovirt-engine/','buildFromGit': 'yes'}}

NEEDED_PCKGS = ['make','createrepo', 'dwarves','tree' ,'gdb', 'gcc', 'autofs', 'samba-common','wget',
                'automake', 'git', 'pyflakes', 'rpm-build', 'redhat-rpm-config',
                'httpd','libtool','gettext-devel','glibc','libxml2-python', 'libxml2-devel','gnutls-devel',
                'python-devel','libnl-devel','xhtml1-dtds','createrepo','httpd','readline-devel',
                'ncurses-devel', 'augeas', 'libudev-devel', 'libpciaccess-devel', 'yajl-devel', 'sanlock-devel',
                'libpcap-devel', 'avahi-devel', 'parted-devel' ,'device-mapper-devel', 'numactl-devel', 'libcap-ng-devel',
                'libssh2-devel', 'libblkid-devel','libselinux-devel','cyrus-sasl-devel', 'xen-devel','qemu-img','dnsmasq','poolkit','iscsi-initiator-utils',
                'netcf-devel', 'libcurl-devel', 'libwsman-devel', 'audit-libs-devel', 'systemtap-sdt-devel','radvd','ebtables']

HOSTS = []
REPO_NAME = 'upstream.repo'
REPO_PATH = DIRS[8]

PKGS = {'sanlock':'11619','systemd':'10477',
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
        'telnet':'690','vgabios':'7853','seabios':'9765','seabios-bin':'9765','sgabios':'13001','sgabios-bin':'13001',
        'OpenIPMI':'568','gpxe':'8390', 'gdbm':'1042', 'spice':'10623', 'spice-protocol':'10624'}

SITE = 'http://koji.fedoraproject.org/koji/packageinfo?packageID='
BASE = 'http://kojipkgs.fedoraproject.org/packages/'
POSTFIX = '/x86_64/'
SLASH = '/'

