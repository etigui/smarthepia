var express = require('express');
var router = express.Router();
var auth = require('../controllers/auth');
var dateFormat = require('dateformat');
var echarts = require('echarts')

// GET manager index
router.get('/', function(req, res, next) {
    if(auth.checkAuth(req, 0)){
        return res.render('pages/manager', { username: req.session.username, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy") });
    }else{
        return res.redirect('/');
    }
});

router.get('/json', function(req, res, next) {

    if(auth.checkAuth(req, 0)){
        return res.json({"data": [
            {"firstname": "Etienne", "lastname": "Guignard", "email": "0@gmail.com", "enable": "true", "perm": "user", "action": ""},
            {"firstname": "Geatan", "lastname": "Ringot", "email": "1@gmail.com", "enable": "true", "perm": "manager", "action": ""},
            {"firstname": "Quentin", "lastname": "Zeller", "email": "2@gmail.com", "enable": "false", "perm": "admin", "action": ""}]});
    }else{
        return res.redirect('/');
    }



});


// Get users manage
// GET manager index
router.get('/users', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        return res.render('pages/users', { username: req.session.username, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy") });

        //return res.send('lol');
    }else{
        return res.redirect('/');
    }
});

// Get users manage
// GET manager index
router.get('/profile', function(req, res, next) {
    if(auth.checkAuth(req, 0)){
        return res.render('pages/profile', { username: req.session.username, dateTime: dateFormat(new Date(), "hh:MM:ss dd-mm-yyyy") });

        //return res.send('lol');
    }else{
        return res.redirect('/');
    }
});


/*
// GET manager index
router.post('/users', function(req, res, next) {
    if(auth.checkAuth(req, 2)){
        return res.send('Modify user ?');
    }else{
        return res.redirect('/');
    }
});
*/
module.exports = router;