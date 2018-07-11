var mongoose = require('mongoose');

var AlarmSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
    },
    dtype: {
        type: String,
        required: true,
    },
    atype: {
        type: String,
        required: true,
    },
    aseverity: {
        type: Number,
        required: true,
    },
    amessage: {
        type: String,
        required: true,
    },
    comment: {
        type: String,
        default: ""
    },
    count: {
        type: Number,
        required: true,
    },
    dstart: {
        type: Date,
        required: true,
    },
    dend: {
        type: Date,
        required: true,
    },
    dlast: {
        type: Date,
        required: true,
    },
    ack: {
        type: Number,
        required: true,
    },
    postpone: {
        type: Date,
        required: true,
    },
    assign: {
        type: String,
        required: true,
    },
    detail: {
        type: Array,
        required: true,
    }
});

var Alarm = mongoose.model('Alarm', AlarmSchema);
module.exports = Alarm;