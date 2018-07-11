var mongoose = require('mongoose');

var StatusSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true
    },
    status: {
        type: String,
        default: ""
    },
    updatetime: {
        type: String,
        default: ""
    },
    color: {
        type: Number,
        default: 3
    }
});

var Status = mongoose.model('Status', StatusSchema);
module.exports = Status;