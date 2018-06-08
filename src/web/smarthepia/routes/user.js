var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var dateFormat = require('dateformat');
var User = require('../models/users');
var bcrypt = require('bcrypt');

// GET /user
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getAdmin())){
        return res.render('pages/user', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "user", type:  req.query.type, message:  req.query.message});
    }else{
        return res.redirect('/');
    }
});

// GET users list => /users/list
router.get('/list', function(req, res, next) {
    if(auth.checkAuth(req, auth.getAdmin())){
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
router.post('/create', function(req, res, next) {
    if(auth.checkAuth(req, auth.getAdmin())){

        let firstname = req.body.firstnameCreate;
        let lastname = req.body.lastnameCreate;
        let email = req.body.emailCreate;
        let password = req.body.passwordCreate;
        let cpassword = req.body.cpasswordCreate;
        let active = req.body.activeCreate;
        let permission = req.body.permissionCreate;

        // Check if user info are not empty or null
        if(firstname && lastname && email && password && cpassword && active && permission){

            // Check email validation
            let re = /^(?:[a-z0-9!#$%&amp;'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&amp;'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$/;
            if(re.test(email)){

                // Check if password are the same
                if(password === cpassword){

                    // Check if email is unique
                    validation.checkUniqueEmail(email, function (emailUnique) {
                        if(emailUnique){
                            // Modify perm by name
                            if(permission === "admin"){
                                permission = 2;
                            }else if(permission === "manager"){
                                permission = 1;
                            }else{
                                permission = 0;
                            }

                            // Create user in the DB
                            let newUser = {firstname: firstname, lastname: lastname, email: email, password: password, enable: active, permissions: permission};
                            User.create(newUser, function (error, user) {
                                if (error) {
                                    return next(error);
                                }
                                res.type('json');
                                return res.json({status: "success", message: "User account successfully created"});
                            });
                        }else{
                            res.type('json');
                            return res.json({status: "error", message: "Email already exist"});
                        }
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Password must match"});
                }
            }else{
                res.type('json');
                return res.json({status: "error", message: "Email not valid"});
            }
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

// POST users delete => /users/delete
router.post('/delete', function(req, res, next) {
    if(auth.checkAuth(req, auth.getAdmin())){
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
router.post('/edit', function(req, res, next) {
    if(auth.checkAuth(req, auth.getAdmin())){

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
            console.log(typeof reqEnable)

            // Update user
            User.findOneAndUpdate({email: reqMail}, {$set: {permissions: reqPermission, enable: reqEnable}}, function (err, user) {
                if (err) {
                    return next(error);
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