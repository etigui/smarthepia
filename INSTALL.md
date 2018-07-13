
# Update/upgrade
 sudo apt-get update && sudo apt-get upgrade

# Install ssh
    sudo apt-get install openssh-server -y

# Gen and install ssh key
# ssh-keygen -b 4096
# Enter
# passphrase: #!smarthepia_pass_ssh_2018!#
# passphrase: #!smarthepia_pass_ssh_2018!#


# Add public key to autorised host (to connect to smarthpia)
#cat ssh_public_key.ppk >> ~/.ssh/authorized_keys
# chmod 600 ~/.ssh/authorized_keys

# Creat root smarthepia
    mkdir ~/bin

# Install net tool => ifconfig commande
    sudo apt install net-tools -y

# Install KNX simulator and REST server
	sudo apt-get install python3-setuptools -y
	sudo apt-get install python3-pip -y
	sudo apt-get install git -y
	sudo apt-get install python3-pyqt5 -y

# Clone or copy smarthepia repo (GitHub)
	sudo apt-get install git
	git clone https://username:password@github.com/raccoonmaster/smarthepia.git

# Install KNX and simulateur lib
    sudo pip3 install flask
    sudo pip3 install jsonify
    sudo pip3 install request
    sudo pip3 install pymongo
    
# Install knxnet and lib
cd ~/bin/smarthepia/knx/knxnet_iot
sudo python3 setup.py install

# Lunch KNX simulator
cd ~/bin/smarthepia/knx/actuasim_iot
    python3 actuasim.py &

# Lunch and install lib KNX REST server (debug mode)
    cd ~/bin/smarthepia/knx

    python3 KNX_REST_Server.py

# For smarthepia automation
    sudo pip3 install psutil


# Mongodb python 3.6 lib
	sudo pip3 install pymongo==3.7.0

# Install nodjs & npm
	sudo apt-get install nodejs -y
	sudo apt-get install npm -y

# Install Ngnix and config
	sudo apt-get install nginx -y

	sudo nano /etc/nginx/sites-available/default
	 location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }


	sudo nginx -t
	sudo systemctl restart nginx

# Install Mongodb
	sudo apt-get install mongodb -y

# Install githcraken easy manage git repo
	wget https://release.gitkraken.com/linux/gitkraken-amd64.deb
	sudo dpkg -i gitkraken-amd64.deb
	rm -f gitkraken-amd64.deb


# Automation package

	sudo pip3 install pysolar
	sudo pip3 install simple-pid
	sudo pip3 install python-dateutil

# Ngnix self-signed cert
 https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04

# Run at first Smarthepia
cd ~/bin/smarhepia/web
npm install
npm start
test to => https://localhost
