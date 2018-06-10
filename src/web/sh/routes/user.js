var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var passport = require('../controllers/passport');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var User = require('../models/user');
var bcrypt = require('bcrypt');

// Module variables
var isAuth = require('../controllers/isAuth');

// Middleware
router.use(passport.initialize());
router.use(passport.session());

// GET /user
router.get('/', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getAdmin())){
        return res.render('pages/user', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "user", type:  req.query.type, message:  req.query.message});
    }else{
        return res.redirect('/');
    }
});

// GET users list => /users/list
router.get('/list', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getAdmin())){
        res.type('json');
        let toRemove = {__v: false, _id: false, password : false, lastConnection: false};
        User.find({}, toRemove, function(err, user) {
            if (err) {
                return next(error);
            }
            return res.json({"data": user});
        });
    }else{
        return res.redirect('/');
    }
});


// POST users create => /users/create
router.post('/create', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getAdmin())){
        passport.authenticate('local-signup', function(err, user, info) {
            if(err) {
                return next(err); // will generate a 500 error
            }
            if(!user) {
                res.type('json');
                return res.json({status: "error", message: info.message});
            }else{
                res.type('json');
                return res.json({status: "success", message: info.message});
            }
        })(req, res, next);
    }else{
        return res.redirect('/');
    }
});

// POST users delete => /users/delete
router.post('/delete', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getAdmin())){
        let reqMail = req.body.email;
        if(reqMail) {

            // Avoid self deletion
            if (reqMail !== req.session.email) {

                // Remove user db entree
                User.remove({email: reqMail}, function (err, user) {
                    if (err) {
                        return next(error);
                    }
                    res.type('json');
                    return res.json({status: "success", message: "User " + reqMail + " successfully deleted"});
                });
            }else {
                res.type('json');
                return res.json({status: "error", message: "You cannot delete yourself"});
            }
        }else{
            res.type('json');
            return res.json({status: "error", message: "User email undefined"});
        }
    }else{
        return res.redirect('/');
    }
});

// POST users edit => /manager/users/edit
router.post('/edit', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getAdmin())){

        let reqMail = req.body.email;
        let reqPermission = req.body.permissions;
        let reqEnable = req.body.enable;
        if(reqMail && reqPermission && reqEnable) {

            // Modify perm by name
            if(reqPermission === "admin"){
                reqPermission = 2;
            }else if(reqPermission === "manager"){
                reqPermission = 1;
            }else{
                reqPermission = 0;
            }

            if(reqEnable === "true"){
                reqEnable = true;
            }else{
                reqEnable = false;
            }

            // Update user
            User.findOneAndUpdate({email: reqMail}, {$set: {permissions: reqPermission, enable: reqEnable}}, function (err, user) {
                if (err) {
                    return next(err);
                }
                res.type('json');
                return res.json({status: "success", message: "User " + reqMail + " successfully edited"});
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "User info undefined"});
        }
    }else{
        return res.redirect('/');
    }
});

module.exports = router;