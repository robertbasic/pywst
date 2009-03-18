#!/usr/bin/python

__author__ = 'Robert Basic contactme@robertbasic.com'
__version__ = '0.0.1'
__license__ = 'MIT http://www.opensource.org/licenses/mit-license.php'

import sys
import os
import shutil

class pywst():
    '''pywst creates web project environments.'''

    def __init__(self, projectName):
        '''Initialize variables'''
        # The name of the project for which we're creating the environment
        self.projectName = projectName
        # The user that started the script with sudo powers
        self.user = os.environ['SUDO_USER']
        # The configuration file for the virtual host
        self.vhostFile = '/etc/apache2/sites-available/' + self.projectName
        # The server's name
        self.serverName = self.projectName + '.lh'
        # Path to the project's www folder
        self.wwwFolder = '/var/www/' + self.projectName
        # Path to the project's public folder under the www folder
        self.wwwPublicFolder = self.wwwFolder + '/public/'
        # Path for the backup file, it's backed up in the user's home directory
        self.backupFile = '/home/' + self.user + '/hosts.bak'
        # We need two temporary folders, which are imported to svn repo
        self.tempWwwFolder = '/tmp/' + self.projectName
        self.tempWwwPublicFolder = self.tempWwwFolder + '/public'
        # The path to which the temporary folders are imported to
        self.svnImportPath = 'file:///var/svn/repos/' + self.projectName + '/trunk/'
        # The path from where the project is checked out
        self.svnCoPath = 'http://localhost/repos/' + self.projectName + '/trunk/'
        # The path to the project's repository
        self.svnRepoPath = '/var/svn/repos/' + self.projectName
        # The path to the project's Trac environment
        self.tracPath = '/var/trac/sites/' + self.projectName

        '''Call up the setup steps'''
        self.makeVHost()
        self.enableVHost()
        self.backupHostsFile()
        self.addToHostsFile()
        self.makeTempFolders()
        self.makeFirstSvnImport()
        self.checkoutProjectFromSvn()
        self.makeTracEnvironment()
        self.restartApache()
        self.deleteTempFolders()

    def makeVHost(self):
        '''Make the virtual host file /etc/apache2/sites-available/projectName
        <VirtualHost *:80>
            ServerName projectName.lh
            DocumentRoot /var/www/projectName/public
            <Directory /var/www/projectName/public>
                Options Indexes FollowSymlinks MultiViews
                AllowOverride All
                Order allow,deny
                Allow from all
            </Directory>
        </VirtualHost>
        '''
        print 'Making virtual host...'
        try:
            vhostFile = open(self.vhostFile, 'w')
            vhostFile.write('<VirtualHost *:80>\n\tServerName ' + self.serverName + '\n\tDocumentRoot ' + self.wwwPublicFolder)
            vhostFile.write('\n\n\t<Directory ' + self.wwwPublicFolder + '>\n\t\tOptions Indexes FollowSymlinks MultiViews')
            vhostFile.write('\n\t\tAllowOverride All\n\t\tOrder allow,deny\n\t\tAllow from all\n\t</Directory>\n</VirtualHost>')
            vhostFile.close()
        except IOError:
            print 'Can not write to %s. Exitting pywst...' % self.vhostFile
            self.rollback()

    def enableVHost(self):
        '''Enable the virtual host'''
        os.system('a2ensite ' + self.projectName)

    def backupHostsFile(self):
        '''Backup the /etc/hosts just to be sure'''
        print 'Backing up /etc/hosts file to /home/%s/hosts.bak' % self.user
        try:
            shutil.copy('/etc/hosts', '/home/' + self.user + '/hosts.bak')
        except IOError:
            print 'Can not create backup file of /etc/hosts. Exitting pywst...'
            self.rollback()

    def addToHostsFile(self):
        '''Add the new virtual host at 127.0.0.1'''
        print 'Adding to /etc/hosts file as %s on 127.0.0.1' % self.serverName
        try:
            hostsFile = open('/etc/hosts', 'a')
            hostsFile.write('\n# Next line written by pywst...\n')
            hostsFile.write('127.0.0.1\t' + self.serverName + '\n')
            hostsFile.close()
        except IOError:
            print ''
            self.rollback()

    def makeTempFolders(self):
        '''Create temporary folders'''
        print 'Making temporary folders %s and %s' % (self.tempWwwFolder, self.tempWwwPublicFolder)
        try:
            os.mkdir(self.tempWwwFolder)
            os.mkdir(self.tempWwwPublicFolder)
        except OSError:
            print 'Can not create temporary folders. Exitting pywst...'
            self.rollback()

    def makeFirstSvnImport(self):
        print 'Making first import into the repository...'
        os.system('svn import -m "First import with pywst..." ' + self.tempWwwFolder + ' ' + self.svnImportPath)

    def checkoutProjectFromSvn(self):
        print 'Checking out project from repository to %s' % self.wwwFolder
        os.system('svn checkout ' + self.svnCoPath + ' ' + self.wwwFolder)
        os.system('chown -R ' + self.user + ':' + self.user + ' ' + self.wwwFolder)

    def makeTracEnvironment(self):
        print 'Making Trac environment under %s' % self.tracPath 
        os.system('trac-admin ' + self.tracPath + ' initenv ' + projectName + ' sqlite:db/trac.db svn ' + self.svnRepoPath)
        os.system('chown -R www-data ' + self.tracPath)

    def restartApache(self):
        print 'Restarting Apache'
        os.system('/etc/init.d/apache2 restart')

    def deleteTempFolders(self):
        print 'Deleting temporary folders %s and %s' % (self.tempWwwFolder, self.tempWwwPublicFolder)
        os.rmdir(self.tempWwwPublicFolder)
        os.rmdir(self.tempWwwFolder)

    def rollback(self):
        sys.exit()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "You have not provided a name for the project"
    elif os.environ['USER'] != 'root':
        print "You must be root to run pywst"
    else:
        projectName = sys.argv[1]
        print 'Provided <%s> as project name' % projectName
        print 'Setting up...'
        p = pywst(projectName)
        print 'Done. Now try browsing http://%s.lh/ & http://localhost/repos/%s & http://localhost/trac/%s' % (projectName, projectName, projectName)
