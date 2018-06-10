'use strict';

// Module dependencies
var mongoose = require('mongoose');
var bcrypt = require('bcrypt-nodejs');


// Define user schema
// Permissions:
// - 0 => normal user (read only)
// - 1 => manager (consign, device)
// - 2 => admin (all)
var UserSchema = new mongoose.Schema({
    firstName: {
        type: String,
        required: true,
        trim: true
    },
    lastName: {
        type: String,
        required: true,
        trim: true
    },
    email: {
        type: String,
        unique: true,
        required: true,
        trim: true
    },
    password: {
        type: String,
        required: true,
    },
    lastConnection: {
        type: Date,
        default: Date.now(),
    },
    enable: {
        type: Boolean,
        required: true,
        default: true,
    },
    permissions:{
        type: Number,
        required: true,
        default: 0,
    }
});

// Create schema methods
UserSchema.methods.generateHash = function(password) {
    return bcrypt.hashSync(password, bcrypt.genSaltSync(10), null);
};

UserSchema.methods.validPassword = function(password) {
    return bcrypt.compareSync(password, this.password);
};

// Declare Schema plugins

// Create and export user model
var UserModel = mongoose.model('User', UserSchema);
module.exports = UserModel;