var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var User = require('../models/users');
var bcrypt = require('bcrypt');

// GET /user
router.get('/', function(req, res, next) {

    return res.render('pages/ws');

});

module.exports = router;