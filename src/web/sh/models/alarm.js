var mongoose = require('mongoose');

var AlarmSchema = new mongoose.Schema({

    name: {
        type: String,
        required: true,
        unique: true
    }
});


var Alarm = mongoose.model('Alarm', AlarmSchema);
module.exports = Alarm;