var createError = require('http-errors');
var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var config = require('./configs/config');
var bParser = require('body-parser');
var session = require('express-session');
var compression = require('compression');
// var ejsLayout = require('express-ejs-layouts');
var mongoose = require('mongoose');
var mongoStore = require('connect-mongo')(session);

// Import app modules security
var helmet = require('helmet');
var xssFilter = require('x-xss-protection');


// Internal require
var io = require('./sockets/socket').io;

// Create express app instance
var app = express();

// Module vars
var port = process.env.PORT || 3000;
var env = config.env;
var host = config.host;
var dbUrl = config.dbUrl;
var sessionSecret = config.sessionSecret;
var sessionStore;
var db;
app.locals.errMsg = app.locals.errMsg || null;

// App config and settings
require('clarify');
app.disable('x-powered-by');
app.set('port', port);
app.set('env', env);
app.set('host', host);

// Helmet secure express apps by setting various HTTP headers
//app.use(helmet());

// X-XSS-Protection HTTP header is a basic protection against XSS
//app.use(xssFilter({ setOnOldIE: true }));

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
// app.set('layout', 'layout');
//app.use(express.static(path.join(__dirname, 'public')));


// MongoDB connection
mongoose.connect(dbUrl);
db = mongoose.connection;
db.on('error', function (err) {
    console.error('There was a db connection error');
    return  console.error(err.message);
});
db.once('connected', function () {
    return console.log('Successfully connected to ' + dbUrl);
});
db.once('disconnected', function () {
    return console.error('Successfully disconnected from ' + dbUrl);
});
process.on('SIGINT', function () {
    mongoose.connection.close(function () {
        console.error('dBase connection closed due to app termination');
        return process.exit(0);
    });
});
sessionStore = new mongoStore({mongooseConnection: mongoose.connection, touchAfter: 24 * 3600});

// Middleware stack
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

/*
Extracting the session midddleware into a variable allows us to pass it to
'io', this then allows socket.io access to the 'id' of the user for that
session and consequently, 'io' can access that user by querying the
dBase
*/
var sharedMWSesssion =  session({
    name: 'socialify.sess',
    store: sessionStore,
    secret: sessionSecret,
    resave: false,
    saveUninitialized: true,
    cookie: {maxAge: 1000 * 60 * 60 * 24}});
/*
The following idiom directs 'io' to use the same session midddleware
as the base express app immediatly after a client has connected. We can do this
here because the 'io' object is exposed via the 'singleton' pattern
and is thus the same thoughout the app!
*/
app.use(sharedMWSesssion);
io.use(function (socket, next) {
    sharedMWSesssion(socket.request, socket.request.res, next);
});


// Define routes file
var indexRouter = require('./routes/index');
var homeRouter = require('./routes/home');
var statisticRouter = require('./routes/statistic');
var automationRouter = require('./routes/automation');
var userRouter = require('./routes/user');
var alarmRouter = require('./routes/alarm');
var deviceRouter = require('./routes/device');
var locationRouter = require('./routes/location');
var dependencyRouter = require('./routes/dependency');
var profileRouter = require('./routes/profile');

// app.use(ejsLayout);
app.use(compression());
app.use(favicon(path.join(__dirname, 'public', 'images/favicon.ico')));
app.use(express.static(path.join(__dirname, 'public')));

// Set route path(url) to route file
app.use('/', indexRouter);
app.use('/home', homeRouter);
app.use('/statistic', statisticRouter);
app.use('/automation', automationRouter);
app.use('/user', userRouter);
app.use('/alarm', alarmRouter);
app.use('/device', deviceRouter);
app.use('/location', locationRouter);
app.use('/dependency', dependencyRouter);
app.use('/profile', profileRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// Error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('pages/error');
});

// Export Module
module.exports = app;
