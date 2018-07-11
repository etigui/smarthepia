var express = require('express');
var router = express.Router();
var dateFormat = require('dateformat');
var Dependency = require('../models/dependency');
var auth = require('../controllers/auth');
var validation = require('../controllers/validation');
var Devices = require('../models/devices');

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
        var length = Object.keys(dictionary.dependency).length ;
        var depName = dictionary.depName;
        var deviceDependencyError = false;
        if(depName && length){

            // Check if the dependency name already exist
            validation.checkUniqueDependency(depName, function (matchDependency) {
                if(matchDependency){

                    // Empty array to store dependency device
                    var newDevice = [];

                    // !!!!!!! TO MODYFY HERE
                    // In the actual implementation you must add one REST/HTTP method
                    var checkMethodRest = [];

                    // Add dico data to list
                    dictionary.dependency.forEach(function(dep) {

                        if(dep.depdName && dep.depdIp && dep.depdMethod && dep.depdPort >= 0) {

                            // !!!!!!! TO MODYFY HERE
                            // In the actual implementation you must add one REST/HTTP method
                            if(dep.depdMethod === "REST/HTTP"){
                                checkMethodRest.push(dep.depdMethod);
                            }
                            newDevice.push({
                                name: dep.depdName,
                                ip: dep.depdIp,
                                port: dep.depdPort,
                                comment: dep.depdComment ? dep.depdComment : "",
                                method: dep.depdMethod
                            });
                        }else{
                            deviceDependencyError = true;
                        }
                    });

                    // !!!!!!! TO MODYFY HERE
                    // In the actual implementation you must add one REST/HTTP method
                    if(checkMethodRest.length === 1){

                        // Check if all dependency device are well added
                        if(deviceDependencyError){
                            res.type('json');
                            return res.json({status: "error", message: "All field must be filled"});
                        }else{
                            var newDependency = {depname: depName, devices: newDevice};
                            Dependency.create(newDependency, function (err, user) {
                                if (err) {
                                    return next(err);
                                }
                                res.type('json');
                                return res.json({status: "success", message: "Dependency " + depName + " has been successfully created"});
                            });
                        }
                    }else{
                        res.type('json');
                        return res.json({status: "error", message: "Due to the actual implementation you must add only one REST/HTTP method"});
                    }
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

// GET /dependency/list
router.get('/list', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false, _id: false, devices: false};
        Dependency.find({}, toRemove, function(err, dependency) {
            if (err) {
                return next(err);
            }
            return res.json({"data": dependency});
        });

    }else{
        return res.redirect('/');
    }
});

// GET /dependency/listall
router.get('/listall', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        res.type('json');
        let toRemove = {__v: false};
        Dependency.find({}, toRemove, function(err, dependency) {
            if (err) {
                return next(err);
            }
            return res.json({"data": createNewData(dependency)});
        });

    }else{
        return res.redirect('/');
    }
});

// To solve the sub dict
function createNewData(data){
    var newData = [];
    for (i = 0; i < data.length; i++) {
        for (j = 0; j < data[i].devices.length; j++) {
            newData.push({
                depName: data[i].depname,
                divName: data[i].devices[j].name,
                ip: data[i].devices[j].ip,
                port: data[i].devices[j].port,
                method: data[i].devices[j].method,
                comment: data[i].devices[j].comment,
                ddId: data[i].devices[j]._id,
                dId: data[i]._id,
            });
        }
    }
    return newData;
}

// POST /dependency/delete
router.post('/delete', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        var dDid = req.body.dDid;
        var dId = req.body.dId;
        var depName = req.body.name;

        console.log(depName);

        // Check not empty
        if(dDid && dId && depName){

            Dependency.findOne({_id: dId}, {}, function(err, div) {
            if (err) {
                return next(err);
            }

                // If rest one device dependency we can delete the whole dependency
                // Else just de device dependency
                if(div.devices.length === 1){

                    // Check if device depend to that dependency
                    Devices.find({dependency: depName}, function(err, deviceParent) {

                        // Check device by dependency
                        if(deviceParent.length > 0){
                            res.type('json');
                            return res.json({status: "error", message: "There are device which belong to that dependency. You must deleted them before to delete the dependency."});
                        }else{
                            Dependency.remove({_id: dId}, function(err, dependency) {
                                if (err) {
                                    return next(err);
                                }
                                res.type('json');
                                return res.json({status: "success", message: "Dependency has been successfully deleted"});
                            });
                        }
                    });
                }else{
                    Dependency.update({_id: dId},{ $pull: { 'devices': {_id: dDid } } }, function(err, dependency) {
                        if (err) {
                            console.log(err);
                            return next(err);
                        }
                        res.type('json');
                        return res.json({status: "success", message: "Device dependency has been successfully deleted"});
                    });
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

// POST /dependency/edit
router.post('/edit', isAuth, function(req, res, next) {
    if(auth.checkPermission(req, auth.getManager())){
        var editDeviceName = req.body.editDeviceName;
        var editIp = req.body.editIp;
        var editPort = req.body.editPort;
        var editComment = req.body.editComment;
        var editDdId = req.body.editDdId;
        var editDId = req.body.editDId;

        // Check if all data are not empty
        if(editDeviceName && editIp && editDdId && editDId){
            var set = {$set: {"devices.$.name": editDeviceName, "devices.$.ip": editIp, "devices.$.port": editPort, "devices.$.comment": editComment ? editComment : ""}};
            Dependency.findOneAndUpdate({_id: editDId, "devices._id": editDdId}, set, function(err, dependency) {
                if (err) {
                    return next(err);
                }
                res.type('json');
                return res.json({status: "success", message: "Dependency " + editDeviceName + " has been successfully edited"});
            });
        }else{
            res.type('json');
            return res.json({status: "error", message: "All field must be filled"});
        }
    }else{
        return res.redirect('/');
    }
});

module.exports = router;