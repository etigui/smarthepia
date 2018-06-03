var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');
var User = require('../models/users');
var Dependency = require('../models/dependency');
var Devices = require('../models/devices');
var validation = require('../controllers/validation');
var bcrypt = require('bcrypt');




//<editor-fold desc="Register routes">
// GET manager register => /manager/register
router.get('/register', function(req, res, next) {
    if(auth.checkAuth(req, 0)){
        return res.render('pages/register', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "register" });
    }else{
        return res.redirect('/');
    }
});

router.get('/register/devices/location/list', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        res.type('json');
        let toRemove = {__v: false, _id: false, value: false, itemStyle: false, comment: false, dependency: false, group: false, rules: false, orientation: false, enable: false};
        Devices.find({}, toRemove, function(err, location) {
            if (err) {
                return next(error);
            }
            return res.json({"data": location});
        });

    }else{
        return res.redirect('/');
    }
});

router.get('/register/devices/dependency/list', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        res.type('json');
        let toRemove = {__v: false, _id: false, devices: false};
        Dependency.find({}, toRemove, function(err, dependency) {
            if (err) {
                return next(error);
            }
            return res.json({"data": dependency});
        });

    }else{
        return res.redirect('/');
    }
});


// GET manager register => /manager/register
router.post('/register/location/create', function(req, res, next) {
    if(auth.checkAuth(req, 2)){

        // Check if the dependency name already exist
        //validation.checkUniqueLocation(locName, function (matchLocation) {

        //});


    //{color:
        // var newLocation = {name: "Building A", type: "Building", parent: 0, comment: "No comment", dependency: "KNX",group: "group", rules: "Default", orientation: "North", enable: true};
        var newLocation = {name: "Room 1", type: "Room", parent: 4, enable: true};

        Devices.create(newLocation, function (error, user) {
            if (error) {
                console.log(error);
                return next(error);
            }
            return res.send("Hello");
        });


    }else{
        return res.redirect('/');
    }
});

// POST register dependency=> /manager/register/dependency
router.post('/register/create/dependency', function(req, res, next) {
    if(auth.checkAuth(req, 2)){

        var dictionary = req.body;
        var args = Object.keys(dictionary).length;
        var depName = dictionary.depName;
        var max = Object.keys(dictionary).length -1;

        if(depName && args >= 5 && ((max % 4) === 0)){

            // Check if the dependency name already exist
            validation.checkUniqueDependency(depName, function (matchDependency) {
                if(matchDependency){

                    // Empty array to store dependency device
                    var newDevice = [];

                    // Add dico data to list
                    var length = max / 4;
                    for (var i = 0; i < length; i++){
                        newDevice.push({name: dictionary['dependency['+i+'][depdName]'], ip: dictionary['dependency['+i+'][depdIp]'], port: dictionary['dependency['+i+'][depdPort]'], comment: dictionary['dependency['+i+'][depdComment]']});
                    }
                    var newDependency = {depname: depName, devices: newDevice};

                    Dependency.create(newDependency, function (error, user) {
                        if (error) {
                            console.log(error);
                            return next(error);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Dependency has been successfully created"});
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Dependency name must be unique"});
                }
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }

    }else{
        return res.redirect('/');
    }
});




//</editor-fold>

//<editor-fold desc="Manager routes">
// GET manager => /manager
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, 0)){
        return res.render('pages/manager', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "home" });
    }else{
        return res.redirect('/');
    }
});

router.get('/list', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        res.type('json');
        let toRemove = {__v: false, _id: false};
        Devices.find({}, toRemove, function(err, devices) {
            if (err) {
                return next(error);
            }
            return res.json({data: devices});
        });

    }else{
        return res.redirect('/');
    }
});
//</editor-fold>


//<editor-fold desc="Profile routes">
// GET profile => /manager/profile
router.get('/profile', function(req, res, next) {
    if(auth.checkAuth(req, 0)){
        return res.render('pages/profile', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "profile", firstname: req.session.firstname, email: req.session.email});
    }else{
        return res.redirect('/');
    }
});

// GET profile load => /manager/profile/load
router.get('/profile/load', function(req, res, next) {
    if(auth.checkAuth(req, 0)){
        res.type('json');
        let toRemove = {__v: false, _id: false, password : false, lastConnection: false, enable: false, permissions: false, action: false};
        User.findOne({_id: req.session.userId}, toRemove, function(err, user) {
            if (err) {
                return next(error);
            }
            if(user){
                res.type('json');
                return res.json(user);
            }else{
                //TODO return error cause no user could be loaded
            }

        });
    }else{
        return res.redirect('/');
    }

});

// POST profile edit password => /manager/profile/edit/password
router.post('/profile/edit/password', function(req, res, next) {
    if(auth.checkAuth(req, 0)){

        let cpass = req.body.cpass;
        let npass = req.body.npass;
        let cnpass = req.body.cnpass;

        if(cpass && npass && cnpass && req.session.userId){

            // Check if current password match with the one on the db
            validation.checkCurrentPassword(req.session.userId, cpass, function (matchCurrentPass) {
                if(matchCurrentPass){

                    // Check if the new and confirm new password match
                    if(npass === cnpass){

                        // Hash the new pass
                        bcrypt.hash(npass, 10, function (err, hash) {
                            if (err) {
                                return next(err);
                                // TODO error 500
                            }

                            // Update user password
                            User.findOneAndUpdate({_id: req.session.userId}, {$set: {password: hash}}, function (err, user) {

                                if (err) {
                                    return next(err);
                                }
                                res.type('json');
                                return res.json({status: "success", message: "Password has been successfully changed"});
                            });
                        })
                    }else{
                        res.type('json');
                        return res.json({status: "error", message: "New and confirm password not match"});
                    }
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Wrong current password"});
                }
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

// POST profile edit user => /manager/profile/edit/user
router.post('/profile/edit/user', function(req, res, next) {
    if(auth.checkAuth(req, 0)){

        let mailUser = req.body.email;
        let firstnameUser = req.body.firstname;
        let lastnameUser = req.body.lastname;

        if(mailUser && firstnameUser && lastnameUser && req.session.email){

            // At this point we at least want to chnage the email
            // So we must check if it is not already exist
            if(mailUser !== req.session.email) {
                validation.checkUniqueEmail(mailUser, function (emailUnique) {
                    // Check if email unique
                    if(emailUnique){

                        // Update user info
                        User.findOneAndUpdate({_id: req.session.userId}, {$set: {email: mailUser, firstname: firstnameUser, lastname: lastnameUser}}, function (err, user) {
                            if (err) {
                                console.log("FE3 " + mailUser);
                                return next(error);
                            }

                            // Change lastname is session cause maybe new one
                            req.session.lastname = lastnameUser;
                            req.session.email = mailUser;
                            res.type('json');
                            return res.json({status: "success", message: "Personal informations have been successfully changed"});
                        });
                    }else{
                        res.type('json');
                        return res.json({status: "error", message: "Email already exist"});
                    }
                });
            }else{
                // Update user info
                User.findOneAndUpdate({_id: req.session.userId}, {$set: { firstname: firstnameUser, lastname: lastnameUser}}, function (err, user) {
                    if (err) {
                        console.log("FE3 " + mailUser);
                        return next(error);
                    }

                    // Change lastname is session cause maybe new one
                    req.session.lastname = lastnameUser;
                    res.type('json');
                    return res.json({status: "success", message: "Personal informations have been successfully changed"});
                });
            }
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

//</editor-fold >

//<editor-fold desc="User routes">
// GET users => /manager/users
router.get('/users', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        return res.render('pages/users', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "users", type:  req.query.type, message:  req.query.message});
    }else{
        return res.redirect('/');
    }
});

// GET users list => /manager/users/list
router.get('/users/list', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
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


// POST users create => /manager/users/create
router.post('/users/create', function(req, res, next) {
    if(auth.checkAuth(req, 2)){

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

// POST users delete => /manager/users/delete
router.post('/users/delete', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
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
router.post('/users/edit', function(req, res, next) {
    if(auth.checkAuth(req, 2)){

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
//</editor-fold>

module.exports = router;