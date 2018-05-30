var express = require('express');
var router = express.Router();
var User = require('../models/users');
var bcrypt = require('bcrypt');

module.exports = {

    // Check login input
    checkLoginInput: function checkInput(value){
            if (typeof(value) !== "undefined" && value){
                return true;
            }
            return false;
    },
    checkUniqueEmail: function CheckEmail(value, callback){
        User.find({email: value}, function(err, user) {
            if (err) {
                return next(error);
            }
            if(user.length > 0){
                callback(false);
            }else {
                callback(true);
            }
        });
    },
    checkCurrentPassword: function CheckCP(userId, password, callback){
        User.findOne({ _id: userId }).exec(function (err, user) {
            if (err) {
                return callback(err)
            }
            else if (!user) {
                return callback(false);
            }
            bcrypt.compare(password, user.password, function (err, result) {
                if (result === true) {
                    return callback(true);
                } else {
                    return callback(false);
                }
            });
        });
    }
};