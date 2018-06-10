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
    usernameField : 'email',
    passwordField : 'password',
    passReqToCallback : true
  },
  function(req, email, password, done) {
      User.findOne({email: email}, function(err, user) {
      if(err) {
        console.error(err);
        return done(err);
        }
      if(user) {
        return done(null, false, {errMsg: 'email already exists'});
      }
      else {
          var newUser = new User();
          newUser.username = req.body.username;
          newUser.firstName = req.body.fname;
          newUser.lastName = req.body.lname;
          newUser.email = email;
          newUser.password = newUser.generateHash(password);
          newUser.save(function(err, user) {
            if(err) {
              if(err.message === 'User validation failed') {
                return done(null, false, {errMsg: 'Please fill all fields'});
              }
              console.error(err);
              return done(err);
              }
              console.log('new user successfully created', user);
            return done(null, user);
          });
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
          return done(null, false, {errMsg: 'User does not exist, please' +
          ' <a href="/signup">signup</a>'});
          }
        if(!user.validPassword(password)) {
          return done(null, false, {errMsg: 'Invalid password try again'});
          }
        return done(null, user);
    });
  })
);

// Export Module
module.exports = passport;

