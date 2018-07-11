'use strict';
/**
 *Module Dependencies
 */
//-----------------------------------------------------------------------------
var
    express = require('express'),
    passport = require('../config/passport'),
    config = require('../config/config'),
    UserModel = require('../models/users');
//==============================================================================
/**
 *Create Router instance
 */
//-----------------------------------------------------------------------------
var router = express.Router();
//==============================================================================
/**
 *Module variables
 */
//-----------------------------------------------------------------------------
var isLoggedIn = require('../utils/isLoggedIn');
//=============================================================================
/**
 *Middleware
 */
//-----------------------------------------------------------------------------
router.use(passport.initialize());
router.use(passport.session());
//==============================================================================
/**
 *Routes
 */
//-----------------------------------------------------------------------------
//---------------------------Login routes--------------------------------------
router.get('/', function (req, res) {
    return res.status(302).redirect('/login');
});
router.route('/login').
get(function (req,res) {
    return res.status(200).render('pages/login');
}).
post(function(req, res, next) {
    passport.authenticate('local-login', function(err, user, info) {
        if(err) {
            console.error(err);
            return next(err); // will generate a 500 error
        }
        if(!user) {
            return res.status(409).render('pages/login', {errMsg: info.errMsg});
        }
        req.login(user, function(err){
            if(err){
                console.error(err);
                return next(err);
            }
            return res.status(302).redirect('/dashboard');
        });
    })(req, res, next);
});
//---------------------------Signup routes-------------------------------------
router.route('/signup').
get(function (req, res) {
    return res.status(200).render('pages/signup', {errMsg: null});
}).
post(function(req, res, next) {
    passport.authenticate('local-signup', function(err, user, info) {
        if(err) {
            return next(err); // will generate a 500 error
        }
        if(!user) {
            return res.status(409).render('pages/signup', {errMsg: info.errMsg});
        }
        req.login(user, function(err){
            if(err){
                console.error(err);
                return next(err);
            }
            return res.status(302).redirect('/dashboard');
        });
    })(req, res, next);
});
//---------------------------Frontend routes-----------------------------------
router.get('/dashboard', isLoggedIn, function (req, res) {
    var
        user = req.user,
        userdata = {
            username: user.username,
            email: user.email
        };
    console.log('user data sent to dashboard on login', userdata);
    console.log('the request session object', req.session);
    console.log('the serialized user from passport', req.user);

    return res.status(200).render('pages/dashboard', {userdata: userdata});
});
//---------------------------Logout route--------------------------------------
router.get('/logout', function (req, res) {
    req.logout();
    req.session.destroy();
    return res.redirect('/login');
});
//=============================================================================
/**
 *Export Module
 */
//---------------------------------------------------------------------------
module.exports = router;
//=============================================================================