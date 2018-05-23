// Define express as server
var express = require('express');
var app = express();

// Import app modules
var mongoose = require('mongoose');
var createError = require('http-errors');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var favicon = require('serve-favicon');
var session = require('express-session');
var MongoStore = require('connect-mongo')(session);
var URL = require('url-parse');

// MongoDB init and connection
var mdbUrl = 'mongodb://10.10.5.110/smarthepia';
mongoose.connect(mdbUrl).then(() =>  console.log('connection succesful to: ' + mdbUrl)).catch((err) => console.error(err));
var db = mongoose.connection;


if(app.get('env') === 'production'){

    // Truse first proxy (NGNIX)
    app.set('trust proxy', 1)


    var sessionConfig = {
        secret: 'PoKhqJR0uCPnvp0Q1x9jnIAFsBTmNo5i',
        resave: true,
        saveUninitialized: false,
        store: new MongoStore({
            mongooseConnection: db
        }),
        cookie: {secore: true}
    }
}else{

}

// Use sessions for tracking logins
app.use(session({
    secret: 'work hard',
    resave: true,
    saveUninitialized: false,
    store: new MongoStore({
        mongooseConnection: db
    })
}));




// Define routes file
var indexRouter = require('./routes/index');
var managerRouter = require('./routes/manager');

// View engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Set app infos
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(favicon(path.join(__dirname, 'public', 'images/favicon.ico')))

// Set route path(url) to route file
app.use('/', indexRouter);
app.use('/manager', managerRouter);

// Catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// Error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // Render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
