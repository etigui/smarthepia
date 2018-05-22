var express = require('express');
var router = express.Router();


// GET route for reading data
router.get('/', function (req, res, next) {
  return res.send('test');
});

module.exports = router;
