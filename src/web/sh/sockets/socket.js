'use strict';

// Module Dependencies
var User = require('../models/user');
var io = require('socket.io')();

// Module variables
var userSockets = {};

// Client connected
io.on('connection', function (socket) {
    console.log('A client has connected');
    //console.log('the socket session object', socket.request.session);
    console.log('the actual serialized user from passport', socket.request.session.passport.user);

    // Get and store _id of connected user in order to access it easily
    // from other modules e.g. from router
    var ID = socket.request.session.passport.user;
    userSockets[ID] = socket;

    // Get user permission to let only authorized user to talk (even normally the other can't)
    var userPermission = -1;

    // Check if current user exist and get user info
    // passport id most match with => _id
    User.findOne({_id: ID}, function (err, user) {
        if(err) {
            console.error(err);
            throw(err);
        }
        userPermission = user.permissions;
        return socket.emit('welcom', "coucou");
    });

    // Client disconnected
    socket.on('disconnect', function () {
        delete userSockets[ID];
        return console.log('The client has disconnected');
    });

    // Received from client (message)
    socket.on('message', function (data) {

        // Only admin cas send message
        if(userPermission > 0) {
            console.log(data);
            socket.broadcast.emit('alarmModified', data);
        }
    });
});

// Export module
module.exports = { io: io, userSockets: userSockets};