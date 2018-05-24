var express = require('express');
var router = express.Router();
var User = require('../models/users');

module.exports = {
    checkAuth: function (req, permission) {

        // Check if session id is setted
        if (req.session.userId) {

            // Check session permission
            if (req.session.permissions >= permission) {
                return true;
            }
        }
        return false;
    }
};