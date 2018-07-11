var mongoose = require('mongoose');

var StatAcSchema = new mongoose.Schema({
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
    value: {
        type: Number,
        required: true
    },

    updatetime: {
        type: Date,
        default: Date.now()
    },
    name: {
        type: String,
        required: true
    },
    type: {
        type: String,
        required: true
    },
    subtype: {
        type: String,
        required: true
    },
    id: {
    type: String,
        required: true
}
});


var StatsAc = mongoose.model('statsac', StatAcSchema);
module.exports = StatsAc;