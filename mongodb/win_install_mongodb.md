# Install MongoDB on windows as service
	https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/

### Downlaod here:
	https://www.mongodb.com/download-center?&_ga=2.2405104.1152351854.1525903551-720515316.1525903551#production


### Check if path exist:
	C:\Program Files\MongoDB\Server\3.6\

### Set root mongo db path: 
	"C:\Program Files\MongoDB\Server\3.6\bin\mongod.exe" --dbpath "c:\mongo\data"

### Create log and db path
	mkdir c:\mongo\data\db
	mkdir c:\mongo\data\log
	
### Create config file and add log and db path
	C:\Program Files\MongoDB\Server\3.6\bin\mongod.cfg

	systemLog:
		destination: file
		path: c:\mongo\data\log\mongod.log
	storage:
		dbPath: c:\mongo\data\db
	# Listen on all interfaces (accept remote access)
	net:
	  port: 27017
	  bindIp: 0.0.0.0
		
	
### Install MongoDB as Windows service
	"C:\Program Files\MongoDB\Server\3.6\bin\mongod.exe" --config "C:\Program Files\MongoDB\Server\3.6\bin\mongod.cfg" --install
	
### Run MongoDB service
	net start MongoDB
	
### Connect to MongoDB
	"C:\Program Files\MongoDB\Server\3.6\bin\mongo.exe"
	
### Stop MongoDB service
	net stop MongoDB
	
### Remove MongoDB service
	"C:\Program Files\MongoDB\Server\3.6\bin\mongod.exe" --remove
