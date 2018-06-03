var mongoose = require('mongoose');
var ai = require('mongoose-auto-increment');

var DevicesSchema = new mongoose.Schema({

    id: {type:Number, unique: true, required: true},
    name: {
        type: String,
        required: true,
    },
    type: {
        type: String,
        required: true,
    },value: {type: Number, default: 1},
    itemStyle: {
        color: { type: String, default: "#34a046"}
    },
    parent: {
        type: Number,
        required: true,
    },
    comment: {
        type: String,
        default: "No comment"
    },
    dependency:{
        type: String,
    },group: {
        type: String
    },rules: {
        type: String,
        default: "Default"

    },orientation: {
        type: String
    }
    ,enable: {
        type: Boolean,
        default: true,
    }
});

DevicesSchema.plugin(ai.plugin, { model: 'Devices', field: 'id', startAt: 1});
var Devices = mongoose.model('Devices', DevicesSchema);
module.exports = Devices;