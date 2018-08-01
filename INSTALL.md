
## Update/upgrade
 	sudo apt-get update && sudo apt-get upgrade

## Install Openssh server
 	sudo apt-get install openssh-server -y
	
## Install python (3.6)
	sudo apt-get install python3.6

## Install net tool => ifconfig command
	sudo apt install net-tools -y

## Install KNX simulator and REST server
	sudo apt-get install python3-setuptools -y
	sudo apt-get install python3-pip -y
	sudo apt-get install git -y
	sudo apt-get install python3-pyqt5 -y

## Creat *Smarthepia* root folder
	mkdir ~/bin

## Clone *Smarthepia* repo (GitHub)
	sudo apt-get install git
	cd ~/bin/
	mkdir tmp
	mkdir smarthepia
	cd ~/bin/tmp/
	git clone https://username:password@github.com/raccoonmaster/smarthepia.git
	mv ~/bin/tmp/smarthepia/src/* ~/bin/smarthepia/
	rm -rf ~/bin/tmp/
	
## Mongodb python 3.6 lib
	sudo pip3 install pymongo==3.7.0
	
## Install KNX and simulator lib
	sudo pip3 install flask
	sudo pip3 install jsonify
	sudo pip3 install request

## Install *Smarthepia* automation lib
	sudo pip3 install psutil
	sudo pip3 install pysolar
	sudo pip3 install simple-pid
	sudo pip3 install python-dateutil

## Install Nodejs & npm
	sudo apt-get install nodejs -y
	sudo apt-get install npm -y

## Install Ngnix and config
https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04

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

## Install Mongodb
https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-18-04

	sudo apt-get install mongodb -y
	sudo systemctl start mongod
Verify Mongodb status:    

	sudo systemctl status mongodb
Change Mongodb conf:    

	sudo nano /etc/mongodb.conf
## Ngnix self-signed cert
https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04

## Install knxnet
	cd ~/bin/smarthepia/knx/knxnet_iot
	sudo python3 setup.py install
	
## Install web server
	cd ~/bin/smarhepia/web
	rm -rf node_modules
	rm package-lock.json
	npm install

## Install PM2 (not done yet)
https://www.digitalocean.com/community/tutorials/how-to-set-up-a-node-js-application-for-production-on-ubuntu-18-04
	
	sudo npm install pm2@latest -g

## Run KNX simulator (new win/term)
	cd ~/bin/smarthepia/knx/actuasim_iot
	python3 actuasim.py

## Run KNX REST server (debug mode) (new win/term)
	cd ~/bin/smarthepia/knx
	python3 KNX_REST_Server.py

## Run web server (without PM2) (new win/term)
	cd ~/bin/smarhepia/web
	npm start

## Run automation (new win/term)
	cd ~/bin/smarhepia/automation
	python3 smarthepia.py
