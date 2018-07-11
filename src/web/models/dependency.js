var mongoose = require('mongoose');

var DependencyDevice = new mongoose.Schema({
    name : {type: String, required: true},
    ip : {type: String, required: true},
    port : {type: Number, required: true},
    method: {type: String, required: true},
    comment: {type: String, default: "No comment"}
});


var DependencySchema = new mongoose.Schema({
    depname: {
        type: String,
        unique: true,
        required: true,
    },
    devices: [DependencyDevice]
});



var Dependency = mongoose.model('Dependency', DependencySchema);
module.exports = Dependency;