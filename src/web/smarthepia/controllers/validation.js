var express = require('express');
var router = express.Router();
var User = require('../models/users');

module.exports = {

    // Check login input
    checkLoginInput: function checkInput(value){
            if (typeof(value) !== "undefined" && value){
                return true;
            }
            return false;
    },
    CheckUniqueEmail: async function CheckEmail(value){
        await User.find({email: value}, function(err, user) {
            if (err) throw err;
            if(user){
                return false;
            }
            return true;
        });
    }
};