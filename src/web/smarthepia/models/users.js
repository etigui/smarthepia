var mongoose = require('mongoose');
var bcrypt = require('bcrypt');


// Define user schema
// Permissions:
// - 0 => normal user (read only)
// - 1 => manager (consign, device)
// - 2 => admin (all)
var UserSchema = new mongoose.Schema({

    firstname: {
        type: String,
        required: true,
        trim: true
    },
    lastname: {
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
    },action: {
        type: String,
        default: "",
    }
});

// Authenticate input against database
UserSchema.statics.authenticate = function (email, password, callback) {
    User.findOne({ email: email })
        .exec(function (err, user) {
            if (err) {
                return callback(err)
            } else if (!user) {
                var err = new Error('User not found.');
                err.status = 401;
                return callback(err);
            }
            bcrypt.compare(password, user.password, function (err, result) {
                if (result === true) {
                    return callback(null, user);
                } else {
                    return callback();
                }
            })
        });
}

// Hashing a password before saving it to the database
UserSchema.pre('save', function (next) {
    var user = this;
    bcrypt.hash(user.password, 10, function (err, hash) {

        if (err) {
            console.log("c");
            return next(err);
        }
        user.password = hash;
        next();
    })
});


var User = mongoose.model('User', UserSchema);
module.exports = User;