var mongoose = require('mongoose');
var ai = require('mongoose-auto-increment');
ai.initialize(mongoose.connection);

var DevicesSchema = new mongoose.Schema({

    id: {
        type:Number,
        unique: true,
        required: true
    },
    name: {
        type: String,
        required: true,
    },
    address: {
        type: String,
        default: ""
    },
    type: {
        type: String,
        required: true,
    },
    subtype: {
        type: String,
        default: ""
    },
    value: {
        type: Number,
        default: 1},
    itemStyle: {
        color: { type: String, default: "#34a046"}
    },
    parent: {
        type: Number,
        required: true,
    },
    comment: {
        type: String,
        default: ""
    },
    dependency:{
        type: String,
        default: "-"
    },group: {
        type: String,
        default: "-"
    },rules: {
        type: String,
        default: "Default"
    },orientation: {
        type: Number,
        default: 0
    }
    ,enable: {
        type: Boolean,
        default: true,
    },derror:{
        type: Array
    }
});

// Autoincrement module for mongodb
DevicesSchema.plugin(ai.plugin, { model: 'Devices', field: 'id', startAt: 1});
var Devices = mongoose.model('Devices', DevicesSchema);
// module.exports = Devices;

module.exports = Devices;