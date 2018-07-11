'use strict';

function isAuth(req, res, next) {
    if(req.isAuthenticated()) {
        return next();
    }
    return res.redirect('/');
}
module.exports = isAuth;
