var express = require('express');
var router = express.Router();
var User = require('../models/users');
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');

// GET home page
router.get('/', function(req, res, next) {
    if( auth.checkAuth(req, 0)){
        return res.redirect('/manager');
    }
    return res.render('pages/index');
});

// POST home page
router.post('/', function(req, res, next) {

    // Check if user and pass are defined and not null
    if (validation.checkLoginInput(req.body.email) && validation.checkLoginInput(req.body.password)){

        // Check user login
        User.authenticate(req.body.email, req.body.password, function (error, user) {

            // Check if no error and if user and pass match
            if (!error && user) {
                req.session.userId = user._id;
                req.session.email = user.email;
                req.session.lastname = user.lastname;
                req.session.firstname = user.firstname;
                req.session.permissions = user.permissions;
                return res.redirect('manager');
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


// Create user
router.post('/create', function(req, res, next) {

    var userData = {
        email: "2@gmail.com",
        username: "2",
        password: "admin",
        lastConnection: new Date(),
        enable: true,
        permissions: 2
    };

    User.create(userData, function (error, user) {
        if (error) {
            return next(error);
        }
        return res.render('pages/index', { type: 'success', message: 'User created' });
    });
});

// GET for logout logout
router.get('/logout', function (req, res, next) {
    if (req.session) {

        // Delete session object
        req.session.destroy(function (err) {

            // Redirect to index
            if (err) return next(err);
            return res.redirect('/');
        });
    }
});

module.exports = router;