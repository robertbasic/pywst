A Python script for automating the steps required to setup a web project environment on my local dev machine that runs on Ubuntu. Called it pywst: Python, Web, Svn, Trac. That’s the best I could do, sorry :P

The main steps for setting up a new project are:
  * Create a virtual host
  * Add it to /etc/hosts
  * Enable the virtual host
  * Import the new project to the SVN repository
  * Checkout the project to /var/www
  * Create a TRAC environment for the project
  * Restart Apache

After these steps I have http://projectName.lh/ which points to /var/www/projectName/public/, SVN repo under http://localhost/repos/projectName/ and the TRAC environment under http://localhost/trac/projectName/.