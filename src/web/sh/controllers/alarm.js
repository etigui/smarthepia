var express = require('express');
var Alarm = require('../models/alarm');
var router = express.Router();

module.exports = {
    alarmNotify: function (callback) {

        // Get what type of alarm, not ack
        Alarm.aggregate([{$match: {ack: 0}},{$group: {_id: null, minType: {$min: "$atype"}}}], function (err, alarmMin) {
            if (err) {
                return callback(false, err);
            }

            // Get number of alarm, not ack
            Alarm.count({ack: 0}, function (err, alarmNumber) {
                if (err) {
                    return callback(false, err);
                }

                // If atype == -1 or count == -1 => no alarm not ack
                if(alarmNumber !== 0) {
                    return callback(true, {"atype": alarmMin[0].minType, "count": alarmNumber});
                }else{
                    return callback(true, {"atype": -1, "count": -1});
                }
            });
        });
    }
};