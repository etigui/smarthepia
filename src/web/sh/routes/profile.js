var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var User = require('../models/user');
var dateFormat = require('dateformat');
var bcrypt = require('bcrypt-nodejs');

// GET /profile
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){
        return res.render('pages/profile', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "profile", firstname: req.session.firstname, email: req.session.email});
    }else{
        return res.redirect('/');
    }
});

// GET profile load => /profile/load
router.get('/load', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){
        res.type('json');
        let toRemove = {__v: false, _id: false, password : false, lastConnection: false, enable: false, permissions: false};
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

// POST profile edit password => /profile/edit/password
router.post('/edit/password', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){

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

// POST profile edit user => /profile/edit/user
router.post('/edit/user', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){

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

module.exports = router;