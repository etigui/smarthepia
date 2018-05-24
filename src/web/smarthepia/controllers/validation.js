var express = require('express');
var router = express.Router();

module.exports = {

    // Check login input
    checkLoginInput: function checkInput(value){
            if (typeof(value) !== "undefined" && value){
                return true;
            }
            return false;
    }
};