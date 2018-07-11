var mongoose = require('mongoose');

var StatSchema = new mongoose.Schema({
    address: {
        type: String,
        required: true
    },
    dependency: {
        type: String,
        required: true
    },
    parent: {
        type: Number,
        required: true
    },
    battery: {
        type: Number,
        required: true
    },
    temperature: {
        type: Number,
        required: true
    },
    humidity: {
        type: Number,
        required: true
    },
    luminance: {
        type: Number,
        required: true
    },
    motion: {
        type: Boolean,
        required: true
    },
    updatetime: {
        type: Date,
        default: Date.now()
    },
    reftime:{
        type: Date,
        default: Date.now()
    }, name: {
        type: String,
        required: true
    }
});


var Stat = mongoose.model('Stat', StatSchema);
module.exports = Stat;