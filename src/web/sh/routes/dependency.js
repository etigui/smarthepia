var express = require('express');
var router = express.Router();
var dateFormat = require('dateformat');
var Dependency = require('../models/dependency');
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');

// Module variables
var isAuth = require('../controllers/isAuth');

// GET /dependency
router.get('/', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getUser())){
        return res.render('pages/dependency', { lastname: req.session.lastname, dateTime: dateFormat(new Date(), "HH:MM:ss mm-dd-yyyy"),permission: req.session.permissions, page: "dependency" });
    }else{
        return res.redirect('/');
    }
});

// POST /dependency/create
router.post('/create', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){

        var dictionary = req.body;
        var length = Object.keys(dictionary.dependency).length -2 ;
        var depName = dictionary.depName;
        //var max = Object.keys(dictionary.dependency).length -1;
        //console.log(args);
        //console.log(max);
        //console.log(dictionary);

        if(depName && length){

            // Check if the dependency name already exist
            validation.checkUniqueDependency(depName, function (matchDependency) {
                if(matchDependency){

                    // Empty array to store dependency device
                    var newDevice = [];

                    // Add dico data to list
                    //var length = max / 5;

                    dictionary.dependency.forEach(function(dep) {
                        console.log(dep.depdName);
                        newDevice.push({name: dep.depdName, ip: dep.depdIp, port: dep.depdPort, comment: dep.depdComment ? dep.depdComment : "", method: dep.depdMethod});
                    });

                    /*for (var i = 0; i < length; i++){
                        //console.log();
                        newDevice.push({name: dictionary['dependency['+i+'][depdName]'], ip: dictionary['dependency['+i+'][depdIp]'], port: dictionary['dependency['+i+'][depdPort]'], comment: dictionary['dependency['+i+'][depdComment]'], method: dictionary['dependency['+i+'][depdMethod]']});
                    }*/
                    var newDependency = {depname: depName, devices: newDevice};
                    Dependency.create(newDependency, function (error, user) {
                        if (error) {
                            console.log(error);
                            return next(error);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Dependency has been successfully created"});
                    });
                }else{
                    res.type('json');
                    return res.json({status: "error", message: "Dependency name must be unique"});
                }
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }

    }else{
        return res.redirect('/');
    }
});

router.get('/list', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, devices: false};
        Dependency.find({}, toRemove, function(err, dependency) {
            if (err) {
                return next(error);
            }
            return res.json({"data": dependency});
        });

    }else{
        return res.redirect('/');
    }
});

router.get('/listall', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false};
        Dependency.find({}, toRemove, function(err, dependency) {
            if (err) {
                return next(error);
            }
            return res.json({"data": createNewData(dependency)});
        });

    }else{
        return res.redirect('/');
    }
});

// To solve the sub dict
function createNewData(data){
    var newData = []
    for (i = 0; i < data.length; i++) {
        for (j = 0; j < data[i].devices.length; j++) {
            newData.push({
                depName: data[i].depname,
                divName: data[i].devices[j].name,
                ip: data[i].devices[j].ip,
                port: data[i].devices[j].port,
                method: data[i].devices[j].method,
                comment: data[i].devices[j].comment
            });
        }
    }
    return newData;
}

module.exports = router;