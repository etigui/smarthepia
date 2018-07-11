'use strict';

// Module dependencies
var  passport = require('passport');
var  config = require('../configs/config');
var User = require('../models/user');

// Module variables
var  host = config.host;
var  LocalStrategy = require('passport-local').Strategy;

// Configuration and Settings
passport.serializeUser(function(user, done) {
  done(null, user.id);
});

passport.deserializeUser(function(id, done) {
  User.findById(id, function(err, user) {
    if(err) {
      console.error('There was an error accessing the records of user with id: ' + id);
      return done(err);
    }
    return done(null, user);
  })
});

// Local strategy signup
passport.use('local-signup', new LocalStrategy({
    usernameField : 'emailCreate',
    passwordField : 'passwordCreate',
    passReqToCallback : true
  },
  function(req, email, password, done) {
      User.findOne({email: email}, function(err, user) {
          if(err) {
            console.error(err);
            return done(err);
            }
          if(user) {
            return done(null, false, {message: 'Email must be unique'});
          }
          else {

              var firstname = req.body.firstnameCreate;
              var lastname = req.body.lastnameCreate;
              var email = req.body.emailCreate;
              var password = req.body.passwordCreate;
              var cpassword = req.body.cpasswordCreate;
              var active = req.body.activeCreate;
              var permission = req.body.permissionCreate;

              // Check if user info are not empty or null
              if(firstname && lastname && email && password && cpassword && active && permission) {

                  // Check email validation
                  var re = /^(?:[a-z0-9!#$%&amp;'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&amp;'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$/;
                  if(re.test(email)){

                      // Check if password are the same
                      if(password === cpassword){

                            // Modify perm by name
                            if(permission === "admin"){
                                permission = 2;
                            }else if(permission === "manager"){
                                permission = 1;
                            }else{
                                permission = 0;
                            }

                            // Create new user
                            var newUser = new User();
                            newUser.firstName = firstname;
                            newUser.lastName = lastname;
                            newUser.enable = active;
                            newUser.permissions = permission;
                            newUser.email = email;
                            newUser.password = newUser.generateHash(password);
                            newUser.save(function(err, user) {
                              if(err) {
                                  if(err.message === 'User validation failed') {
                                      return done(null, false, {message: 'Please fill all fields'});
                                  }
                                  console.error(err);
                                  return done(err);
                              }
                              return done(null, user, {message: 'User account has been successfully created'});
                            });
                      }else{
                          return done(null, false, {message: 'Password must match'});
                      }
                  }else{
                      return done(null, false, {message: 'Email not valid'});
                  }
              }else{
                  return done(null, false, {message: 'All field must be filled'});
              }
          }
    });
}));

// Local strategy login
passport.use('local-login', new LocalStrategy({
    usernameField : 'email',
    passwordField : 'password'
  },
  function(email, password, done) {
    User.findOne({email: email}, function(err, user) {
        if(err) {
            return done(err);
        }
        if(!user) {
            return done(null, false, {message: 'User does not exist'});
        }
        if(!user.validPassword(password)) {
            return done(null, false, {message: 'Invalid password try again'});
        }
        if(user.enable === false){
            return done(null, false, {message: 'User disabled'});
        }
        return done(null, user);
    });
  })
);

// Export Module
module.exports = passport;

