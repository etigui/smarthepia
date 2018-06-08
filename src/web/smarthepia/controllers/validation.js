var express = require('express');
var router = express.Router();
var User = require('../models/users');
var Dependency = require('../models/dependency');
var Devices = require('../models/devices');
var Automation = require('../models/automation');
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
    },
    checkUniqueDependency: function CheckCD(value, callback){
        Dependency.find({ depname: value }).exec(function (err, dependency) {
            if (err) {
                return callback(err)
            } else if(dependency.length > 0){
                return callback(false);
            }else {
                return callback(true);
            }
        });
    }, /*checkUniqueLocation: function CheckCL(value, callback){
        Devices.find({ name: value }).exec(function (err, dependency) {
            if (err) {
                return callback(err)
            } else if(dependency.length > 0){
                return callback(false);
            }else {
                return callback(true);
            }
        });
    },*/checkUniqueAutomation: function CheckUA(value, callback){
        Automation.find({ name: value }).exec(function (err, automation) {
            if (err) {
                return callback(err)
            } else if(automation.length > 0){
                return callback(false);
            }else {
                return callback(true);
            }
        });
    },checkUniqueLocation : function CheckUR(name, parent, callback){
        Devices.find({$and: [{name: name},  {parent: parent}]}).exec(function (err, devices) {
            if (err) {
                return callback(err)
            } else if(devices.length > 0){
                return callback(false);
            }else {
                return callback(true);
            }
        });
    },checkUniqueDevice : function CheckUR(parent, name, address,dependency, callback){
    Devices.find({ $or: [{$and: [{address: address}, {dependency: dependency}]},{$and: [{name: name}, {parent: parent}]}]}).exec(function (err, devices) {
        if (err) {
            return callback(err)
        } else if(devices.length > 0){
            return callback(false);
        }else {
            return callback(true);
        }
    });
}
};