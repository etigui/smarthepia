var express = require('express');
var router = express.Router();
var User = require('../models/users');
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');

// GET home page
router.get('/', function(req, res, next) {
    if( auth.checkAuth(req, auth.getUser())){
        return res.redirect('/home');
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
                return res.redirect('/home');
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