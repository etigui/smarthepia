var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');


// GET manager index
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, 0)){
        return res.render('pages/manager', { username: req.session.username });
    }else{
        return res.redirect('/');
    }
});

// GET manager index
router.get('/users', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        return res.send('Modify user ?');
    }else{
        return res.redirect('/');
    }
});

module.exports = router;