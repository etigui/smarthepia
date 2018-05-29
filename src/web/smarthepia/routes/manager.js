var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');
var User = require('../models/users');
var validation = require('../controllers/validation');

// GET manager => /manager
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, 0)){
        return res.render('pages/manager', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "home" });
    }else{
        return res.redirect('/');
    }
});

// GET profile => /manager/profile
router.get('/profile', function(req, res, next) {
    if(auth.checkAuth(req, 0)){
        return res.render('pages/profile', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "profile" });
    }else{
        return res.redirect('/');
    }
});

// GET users => /manager/users
router.get('/users', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        return res.render('pages/users', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "users" });
    }else{
        return res.redirect('/');
    }
});

// GET users list => /manager/users/list
router.get('/users/list', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        res.type('json');
        var toRemove = {__v: false, _id: false, password : false, lastConnection: false};
        User.find({}, toRemove, function(err, user) {
            if (err) throw err;
            return res.json({"data": user});
        });
    }else{
        return res.redirect('/');
    }
});


// POST users create => /manager/users/create
router.post('/users/create', function(req, res, next) {
    if(auth.checkAuth(req, 2)){

        var firstname = req.param('firstnameCreate');
        var lastname = req.param('lastnameCreate');
        var email = req.param('emailCreate');
        var password = req.param('passwordCreate');
        var cpassword = req.param('cpasswordCreate');
        var active = req.param('activeCreate');
        var permission = req.param('permissionCreate');


        // Check if user info are not empty or null
        if(firstname && lastname && email && password && cpassword && active && permission){

            // Check email validation
            var re = /^(?:[a-z0-9!#$%&amp;'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&amp;'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$/;
            if(re.test(email)){

                // Check if password are the same
                if(password === cpassword){
                    if(validation.CheckUniqueEmail(email)){

                        // Modify perm by name
                        if(permission === "Admin"){
                            permission = 2;
                        }else if(permission === "manager"){
                            permission = 1;
                        }else{
                            permission = 0;
                        }

                        if(active === "true"){
                            active = true;
                        }else{
                            active = false;
                        }

                        var userData = {
                            firstname: firstname,
                            lastname: lastname,
                            email: email,
                            password: password,
                            lastConnection: new Date(),
                            enable: active,
                            permissions: permission,
                            action: ""
                        };

                        User.create(userData, function (error, user) {
                            if (error) {
                                return next(error);
                            }
                            return res.redirect('/manager/users');
                        });
                    }else{
                        //TODO email already existe
                        return res.send("email already existe");
                    }
                }else{
                    //TODO error not same password
                    return res.send("not same password");
                }
            }else{
                //TODO error email
                return res.send("email regex");
            }
        }else{
            //TODO error not all file are filled
            return res.send("not all file are filled");
        }
    }else{
        return res.redirect('/');
    }
});

/*
// GET manager index
router.post('/users', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        return res.send('Modify user ?');
    }else{
        return res.redirect('/');
    }
});
*/
module.exports = router;