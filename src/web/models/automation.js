var mongoose = require('mongoose');

var AutomationSchema = new mongoose.Schema({

    hpstartday: {
        type: Number,
        required: true
    }, hpstartmonth: {
        type: Number,
        required: true
    },hpstopday: {
        type: Number,
        required: true
    },hpstopmonth: {
        type: Number,
        required: true
    },hptempmin: {
        type: Number,
        required: true
    },hptempmax: {
        type: Number,
        required: true
    },nhptempmin: {
        type: Number,
        required: true
    },nhptempmax: {
        type: Number,
        required: true
    },outtempmin: {
        type: Number,
        required: true
    },outsummax: {
        type: Number,
        required: true
    },kp: {
        type: Number,
        required: true
    },ki: {
        type: Number,
        required: true
    },kd: {
        type: Number,
        required: true
    },intempmin: {
        type: Number,
        required: true
    }
});


var Automation = mongoose.model('Automation', AutomationSchema);
module.exports = Automation;