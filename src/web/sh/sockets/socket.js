'use strict';

// Module Dependencies
var UserModel = require('../models/user');
var io = require('socket.io')();

// Module variables
var userSockets = {};

// Config socket connection
io.on('connection', function (socket) {
    console.log('A client has connected');
    console.log('the socket session object', socket.request.session);
    console.log('the actual serialized user from passport', socket.request.session.passport.user);
    //store '_id' of connected user in order to access it easily
    var ID = socket.request.session.passport.user;
    var userPermission = -1;
    //store actual socket of connected user in order to access it easily
    //from other modules e.g. from router
    userSockets[ID] = socket;

    UserModel.findOne({_id: ID}, function (err, user) {
        if(err) {
            console.error(err);
            throw(err);
        }
        var data = {
            firstName: user.firstName,
            lastName: user.lastName
        };
        userPermission = user.permissions;
        console.log('sending additional data to dashboard', data);
        return socket.emit('welcome', data);
    });
    //on disconnect
    socket.on('disconnect', function () {
        delete userSockets[ID];
        return console.log('The client has disconnected');
    });

    socket.on('message', function (data) {

        // Only admin cas send message
        if(userPermission > 0) {
            socket.broadcast.emit('alarmModified', data);
        }
    });
});

// Export module
module.exports = { io: io, userSockets: userSockets};