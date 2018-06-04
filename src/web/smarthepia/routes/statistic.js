var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');

// GET /statistic
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getUser())){
        return res.render('pages/statistic', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "statistic" });
    }else{
        return res.redirect('/');
    }
});

module.exports = router;