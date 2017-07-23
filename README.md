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
7) While running the program you might encounter problems in py module six which can be rectified by
   sudo pip install --ignore-installed six
   

