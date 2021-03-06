var express = require('express');
var router = express.Router();

var _user = 0;
var _manager = 1;
var _admin = 2;

module.exports = {
    checkPermission: function (req, permission) {

        // Check if session id is setted
        if (req.session.userId) {

            // Check session permission
            if (req.session.permissions >= permission) {
                return true;
            }
        }
        return false;
    },getUser: function(){
        return _user;
    },getManager: function(){
        return _manager;
    },getAdmin: function(){
        return _admin;
    }
};