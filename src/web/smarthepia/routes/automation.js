var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');

// GET /automation
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, auth.getManager())){
        return res.render('pages/automation', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy"),permission: req.session.permissions, page: "automation" });
    }else{
        return res.redirect('/');
    }
});

module.exports = router;