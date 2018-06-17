'use strict';

// Module Dependencies
var User = require('../models/user');
var Alarm = require('../models/alarm');
var io = require('socket.io')();
var auth = require('../controllers/auth');

var Notify = require('../controllers/alarm');

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

    // Check if current user exist and get user info
    // passport id most match with => _id
    User.findOne({_id: ID}, function (err, user) {
        if(err) {
            console.error(err);
            throw(err);
        }
        userPermission = user.permissions;

        // Only manager, admin can use this message
        if(userPermission > auth.getManager()) {

            // Get number of alarm not ack and the type
            Notify.alarmNotify(function (sucess, json) {
                if (sucess) {
                    socket.emit('welcome', json);
                }
            });

            // Get what type of alarm, not ack
            /*Alarm.aggregate([{$match: {ack: 0}},{$group: {_id: null, minType: {$min: "$atype"}}}], function (err, alarmMin) {
                if (err) {
                    console.error(err);
                    throw(err);
                }

                // Get number of alarm, not ack
                Alarm.count({ack: 0}, function (err, alarmNumber) {
                    if (err) {
                        console.error(err);
                        throw(err);
                    }
                    var json = null;
                    if(alarmNumber !== 0) {
                        json = {"atype": alarmMin[0].minType, "count": alarmNumber};
                    }else{
                        json = {"atype": -1, "count": -1};
                    }
                    socket.emit('welcome', json);
                });
            });*/
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
        if(userPermission > auth.getUser()) {
            console.log('Receive graphChange');
            socket.broadcast.emit('graphChange', "");
        }
    });

    // Received from client => alarm notify (modified)
    socket.on('alarmNotify', function (data) {

        // Only manager, admin can use this message
        if(userPermission > auth.getManager()) {
            console.log('Receive alarmNotify');

            // Get number of alarm not ack and the type
            Notify.alarmNotify(function (sucess, json) {
                if (sucess) {
                    socket.broadcast.emit('alarmNotify', json);
                }
            });

            // Get what type of alarm, not ack
            /*Alarm.aggregate([{$match: {ack: 0}},{$group: {_id: null, minType: {$min: "$atype"}}}], function (err, alarmMin) {
                if(err) {
                    console.error(err);
                    throw(err);
                }
                // Get number of alarm, not ack
                Alarm.count({ack: 0}, function (err, alarmNumber) {
                    if(err) {
                        console.error(err);
                        throw(err);
                    }
                    var json = null;
                    if(alarmNumber !== 0) {
                        json = {"atype": alarmMin[0].minType, "count": alarmNumber};
                    }else{
                        json = {"atype": -1, "count": -1};
                    }
                    socket.broadcast.emit('alarmNotify', json);
                });
            });*/
        }
    });
});

// Export module
module.exports = { io: io, userSockets: userSockets};