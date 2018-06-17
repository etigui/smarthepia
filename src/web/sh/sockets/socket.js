'use strict';

// Module Dependencies
var User = require('../models/user');
var Alarm = require('../models/alarm');
var io = require('socket.io')();
var auth = require('../controllers/auth');

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
    var alarmType = 0;

    var email = socket.request.session.email;

    // Check if current user exist and get user info
    // passport id most match with => _id
    User.findOne({_id: ID}, function (err, user) {
        if(err) {
            console.error(err);
            throw(err);
        }
        userPermission = user.permissions;

        // Only manager, admin can use this message
        if(userPermission => auth.getManager()) {
            socket.emit('welcome', "");
        }
    });

    // Client disconnected
    socket.on('disconnect', function () {
        delete userSockets[ID];
        console.log('Client has disconnected');
    });

    // Received from client => graph changed
    socket.on('graphChange', function (data) {

        // Only user, manager, admin can use this message
        if(userPermission => auth.getUser()) {
            console.log('Receive graphChange');
            socket.broadcast.emit('graphChange', "");
        }
    });

    // Received from client => alarm notify (modified)
    socket.on('alarmNotify', function (data) {

        // Only manager, admin can use this message
        if(userPermission => auth.getManager()) {
            console.log('Receive alarmNotify');
            socket.broadcast.emit('alarmNotify', "");
            socket.emit('alarmNotify', "");
        }
    });
});

// Export module
module.exports = { io: io, userSockets: userSockets};