var mongoose = require('mongoose');

var StatisticSchema = new mongoose.Schema({
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
    temp: {
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
    }
});


var Statistic = mongoose.model('Statistic', StatisticSchema);
module.exports = Statistic;