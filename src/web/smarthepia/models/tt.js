var express = require('express');
var router = express.Router();
var User = require('./userss');


module.exports = {
    guards:  function (permissions, userId) {

        if(!userId){
            return false
        }
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
};