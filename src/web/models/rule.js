var mongoose = require('mongoose');

var RuleSchema = new mongoose.Schema({

    name: {
        type: String,
        required: true,
        unique: true
    }, active: {
        type: Number,
        default: 0
    },dt: {
        type: String,
        default: "08:00"
    },nt: {
        type: String,
        default: "22:00"
    },temp: {
        type: Number,
        default: 20
    },humidity: {
        type: Number,
        default: 45
    },vdnr: {
        type: Number,
        default: 0
    },bdr: {
        type: Number,
        default: 0
    },bnr: {
        type: Number,
        default: 0
    }
});


var Rule = mongoose.model('Rule', RuleSchema);
module.exports = Rule;