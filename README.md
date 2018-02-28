Relational Social Media Search Engine

1) Download the source code using:
   git clone https://github.com/indervirbanipal/relational-social-media-search-engine.git
2) Install MongoDB from:
   https://treehouse.github.io/installation-guides/mac/mongo-mac.html.
   Create /data/db with sudo while installing MongoDB. 
3) Go through db_restore.sh and restore db (first get the mongodb dump at a destined location) using ./db_restore.sh. 
4) Start the database in a new terminal using ./mongo.sh.
5) Some commands before running server:
   pip --version.
   curl -O https://bootstrap.pypa.io/get-pip.py.
   sudo python get-pip.py.
   sudo pip install Django.
   sudo pip install mongoengine.
   sudo pip install bs4.
   sudo pip install requests.
   sudo pip install xlrd.
   sudo pip install pyexcel.
   sudo pip install facebook.
   sudo pip install mechanize.
6) Start ./server.sh
<<<<<<< HEAD
7) While running the program you might encounter problems in py module six which can be rectified by
   sudo pip install --ignore-installed six
=======
7) Visit http://localhost:8000/testApp/combined/
8) Deploy on some cloud service like AWS and use a URL like http://xx.xxx.xx.xxx:8000/testApp/combined/.
>>>>>>> 43e4536a5f1a34064e17d136ea585b3a56f2d4ce
   
OLD READ ME:

###########################################################################
AWS INSTRUCTIONS (Configurations for proper running on Amazon Web Services)
###########################################################################

1. Configure a new instance. (mail@university.edu accounts have one free.)
2. Select Ubuntu machine for setup.
3. Set all the required Python, MongoDB and required packages listed as below.
4. In AWS console :
        a. Go to https://us-west-2.console.aws.amazon.com/vpc.
        b. Here you will see the VPC for your instance listed. Select the VPC.
        c. Notice the DHCP Options Set column, this is the name of the DNS configured.
        d. Now go to the navigation pane on left > DHCP options Set.
        e. Create DHCP Options Set (click).
        f. Give a name, and in the second set of columns, just fill 8.8.8.8,8.8.4.4 in
                the Domain Name Servers textbox.
        g. Now > Yes, Create. This creates a new DHCP configuration for you.
        h. Now go back to Your VPCs option from navigation pane.
        i. Right click on the VPC and select Edit DHCP Configuration. Select the one you created right now.
        j. So, your system will now point to this DNS always (This is required as LinkedIn will not refuse connections          from Google servers.)
        k. Along with this if you have created any proxy like the one I already created at http://notional-sign-110911.appspot.com/, you can set that inside the program in SignAndSearch.py code.
        l. Now the accesses to the LinkedIn are all anonymous and random.
5. Re-Boot the instance from AWS console. Right click on the instance and click connect to get the
        method for the ssh connection to the server.
6. Now you can check that the project runs.

        This command works in AWS :

                python manage.py runserver 0:8000
~                                                                                                                                            
