// Module Dependencies
var express = require('express');
var passport = require('../controllers/passport');
var auth = require('../controllers/auth');
var config = require('../configs/config');
var UserModel = require('../models/user');

var router = express.Router();

// Module variables
var isAuth = require('../controllers/isAuth');

// Middleware
router.use(passport.initialize());
router.use(passport.session());


// GET home page
router.get('/', function(req, res, next) {
    if( auth.checkPermission(req, auth.getUser())){
        return res.status(200).redirect('/home');
    }
    return res.render('pages/index');
});

// POST home page
router.post('/', function(req, res, next) {
    passport.authenticate('local-login', function(err, user, info) {
        if(err) {
            console.error(err);
            return next(err); // will generate a 500 error
        }
        if(!user) {
            return res.status(409).render('pages/index', {status: "error", message: info.message});
        }
        req.login(user, function(err){
            if(err){
                console.error(err);
                return next(err);
            }

            // Update last connection
            var lastConnection = Date.now();
            UserModel.update({email: user.email}, {$set: {lastConnection: lastConnection}}, function (err, conn) {
                if (err) {
                    return next(err);
                }
                req.session.lastConnection = lastConnection;
                req.session.userId = user._id;
                req.session.email = user.email;
                req.session.lastname = user.lastName;
                req.session.firstname = user.firstName;
                req.session.permissions = user.permissions;
                return res.status(302).redirect('/home');
            });
        });
    })(req, res, next);
});


// GET for logout logout
router.get('/logout', function (req, res, next) {
    req.logout();
    req.session.destroy();
    return res.redirect('/');
});

module.exports = router;