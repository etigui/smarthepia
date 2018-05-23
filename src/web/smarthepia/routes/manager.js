var express = require('express');
var router = express.Router();
var User = require('../models/userss');
var g = require('../models/tt');


// GET manager index
router.get('/', function(req, res, next) {
    if( g.guards(2, req.session.userId)){
        console.log("manager");
        return res.render('manager', { username: req.session.username });
    }else{
        console.log("//");
        return res.redirect('/');
    }
    next();
    /*

    // Check if userId session exist in the database
    User.findById(req.session.userId).exec(function (error, user) {

        // Check if error
        if (error) {
            return next(error);
        } else {

            // Check if user exist
            if (user){
                console.log(user);
                res.render('manager', { username: req.session.username });
            }else{
                return res.redirect('/');
            }
            //var err = new Error('Not authorized! Go back!');
            //err.status = 400;
            //return next(err);

        }
    });
    // TODO error if user not found or not setted => do function isAuthentified()
    //res.send('respond with a resource');

    */
});

 function testtt(permissions, userId) {
    var st = false;

    // Check if userId session exist in the database
    User.findById(userId).exec(function (error, user) {


        //console.log(req.session.userId);
        // Check if error
        if (error) {
            console.log("error");
            st = false;
        } else {

            // Check if user exist
            if (user) {

                // Check if user can access to the route
                if (permissions === user.permissions) {
                    //if(2 === 2){
                    //console.log(user.permissions);
                    console.log("ok");
                    st = true;
                    console.log("dsfsfs");
                }else{
                    st = false;
                }
            }else{
                st = false;
            }
        }
        console.log("st=" + st);
        console.log("other");
        return st;
    });
    console.log("st=" + st);
    console.log("other");
    return st;
}


module.exports = router;