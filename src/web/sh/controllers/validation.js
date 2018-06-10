var express = require('express');
var router = express.Router();
var User = require('../models/user');
var Dependency = require('../models/dependency');
var Devices = require('../models/devices');
var Automation = require('../models/automation');
var bcrypt = require('bcrypt');

module.exports = {

    // Check login input
    checkLoginInput: function(value){
            if (typeof(value) !== "undefined" && value){
                return true;
            }
            return false;
    },
    checkUniqueEmail: function (value, callback){
        User.find({email: value}, function(err, user) {
            if (err) {
                return callback(error);
            }
            if(user.length > 0){
                callback(false);
            }else {
                callback(true);
            }
        });
    },
    checkCurrentPassword: function ssss(userId, password, callback){
        User.findOne({_id: userId}, function(err, user) {
            if(err) {
                return callback(err, false)
            }
            if(!user) {
                return callback(null, false);
            }
            bcrypt.compare(password, user.password, function(err, res) {
                if(err) {
                    return callback(err, false)
                }
                if (res === true) {
                    return callback(null, true);
                } else {
                    return callback(null, false);
                }
            });
        });
    },
    checkUniqueDependency: function (value, callback){
        Dependency.find({ depname: value }).exec(function (err, dependency) {
            if (err) {
                return callback(err)
            } else if(dependency.length > 0){
                return callback(false);
            }else {
                return callback(true);
            }
        });
    },checkUniqueAutomation: function(value, callback){
        Automation.find({ name: value }).exec(function (err, automation) {
            if (err) {
                return callback(err)
            } else if(automation.length > 0){
                return callback(false);
            }else {
                return callback(true);
            }
        });
    },checkUniqueLocation : function(name, parent, callback){
        Devices.find({$and: [{name: name},  {parent: parent}]}).exec(function (err, devices) {
            if (err) {
                return callback(err)
            } else if(devices.length > 0){
                return callback(false);
            }else {
                return callback(true);
            }
        });
    },checkUniqueDevice : function(parent, name, address,dependency, callback) {
        Devices.find({$or: [{$and: [{address: address}, {dependency: dependency}]}, {$and: [{name: name}, {parent: parent}]}]}).exec(function (err, devices) {
            if (err) {
                return callback(err)
            } else if (devices.length > 0) {
                return callback(false);
            } else {
                return callback(true);
            }
        });
    }
};