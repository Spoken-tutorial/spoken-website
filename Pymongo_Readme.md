# Installation on Server
MongoDB

#Add User to MongoDB admin
use admin
db.createUser(
   {
     user: "username" ,
     pwd: "password" , 
     roles: [ { role: "root"  , db: "admin"  } ]
   }
 )

#Now try to login to with these username password
mongo --port 27017 -u "username" -p "password" --authenticationDatabase "admin"

#Check data
# for analytics data is stored in userslogs table
use userslogs
db.getCollectionNames() #to get list of collections present in the db
db.getCollectionNames().map( (name) => ({[name]: db[name].find().toArray().length}) ) # this will list all collections along with the length of data

#Installation on python environment
pymongo from requirements-dev(pymongo==3.10.1)

#Config parameters
Please add the following parameters in config file
MONGO_PORT, MONGO_USER, MONGO_PASS, MONGO_HOST
