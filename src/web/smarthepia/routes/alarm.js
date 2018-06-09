var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');

// GET /alarm
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){

        // Require package.json like a regular module
        var packageInfo = require('../package.json');

        // Do something with the version
        console.log('VERSION: ' + packageInfo.dependencies.ejs);

        return res.render('pages/alarm', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "alarm" });
    }else{
        return res.redirect('/');
    }
});

module.exports = router;