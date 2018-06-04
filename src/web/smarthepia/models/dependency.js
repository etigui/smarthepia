var mongoose = require('mongoose');

var Device = new mongoose.Schema({
    name : {type: String, required: true},
    ip : {type: String, required: true},
    port : {type: Number, required: true},
    comment: {type: String, default: "No comment"}
});


var DependencySchema = new mongoose.Schema({
    depname: {
        type: String,
        unique: true,
        required: true,
    },
    devices: [Device],
    action: {
        type: String,
        default: "",
    }
});



var Dependency = mongoose.model('Dependency', DependencySchema);
module.exports = Dependency;