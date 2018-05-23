var express = require('express');
var router = express.Router();
var User = require('../models/userss');

// GET home page
router.get('/', function(req, res, next) {
    res.render('index', { title: 'smarthepia' });
});

// POST home page
router.post('/', function(req, res, next) {

    // Check if user and pass are defined and not null
    if (checkInput(req.body.username) && checkInput(req.body.password)){

        // Check user login
        User.authenticate(req.body.username, req.body.password, function (error, user) {

            // Check if no error and if user and pass match
            if (!error || user) {
                req.session.userId = user._id;
                req.session.email = user.email;
                req.session.username = user.username;
                req.session.permissions = user.permissions;
                return res.redirect('/manager');
            }else {
                var err = new Error('Wrong email or password.');
                err.status = 401;
                return next(err);
            }
        });
    }else{
        var err = new Error('Username, password error');
        err.status = 400;
        return next(err);
    }
});

// Check input
function checkInput(value){
    if (typeof(value) !== "undefined" && value){
      return true;
    }
    return false;
}

// Create user
router.post('/create', function(req, res, next) {

    var userData = {
        email: "test@gmail.com",
        username: "test",
        password: "admin",
        lastConnection: new Date(),
        enable: true,
        permissions: 2
    };

    User.create(userData, function (error, user) {
        if (error) {
            return next(error);
        }
        return res.render('index', { type: 'success', message: 'User created' });
    });
});

// GET for logout logout
router.get('/logout', function (req, res, next) {
    if (req.session) {

        // Delete session object
        req.session.destroy(function (err) {

            // Redirect to index
            if (err) {
                return next(err);
            } else {
                return res.redirect('/');
            }
        });
    }
});

module.exports = router;