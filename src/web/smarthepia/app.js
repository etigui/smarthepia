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
var mdbUrl = 'mongodb://10.10.0.51/smarthepia'; //192.168.1.111 10.10.5.110 10.10.0.51
mongoose.connect(mdbUrl).then(() =>  console.log('connection succesful to: ' + mdbUrl)).catch((err) => console.error(err));
var db = mongoose.connection;

// Autoincrement module for mongodb
var ai = require('mongoose-auto-increment');
ai.initialize(db);


// Init session params
var sessionParams = {

    // Use to sign session ID
    secret: 'PoKhqJR0uCPnvp0Q1x9jnIAFsBTmNo5i',
    resave: true,
    saveUninitialized: false,
    store: new MongoStore({
        mongooseConnection: db
    }),
    cookie: {}
};

// Check server mode (dev, prod)
// Use sessions for tracking logins
if(app.get('env') === 'production'){

    // Trust first proxy (NGNIX)
    app.set('trust proxy', 1);

    // Serve secure cookie
    sessionParams.cookie.secure = true;
    app.use(session(sessionParams));
}else{
    app.use(session(sessionParams));
}

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


// View engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Set app infos
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(favicon(path.join(__dirname, 'public', 'images/favicon.ico')));

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
  res.render('pages/error');
});

module.exports = app;
