// Define express as server
var express = require('express');
var app = express();

// Import app modules security
var helmet = require('helmet');
var xssFilter = require('x-xss-protection');

// Import app modules
var mongoose = require('mongoose');
var createError = require('http-errors');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var favicon = require('serve-favicon');
var session = require('express-session');
var mongoStore = require('connect-mongo')(session);
//var url = require('url-parse');

var connect = require('connect');

// Helmet secure express apps by setting various HTTP headers
app.use(helmet());

// X-XSS-Protection HTTP header is a basic protection against XSS
app.use(xssFilter({ setOnOldIE: true }));

// MongoDB init and connection
var mdbUrl = 'mongodb://localhost/smarthepia'; //192.168.1.111 10.10.5.110 10.10.0.51
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
    name: 'sess.sid',
    saveUninitialized: true,
    store: new mongoStore({
        mongooseConnection: db
    }),
    cookie: {
        domain: '.local.fi',
        maxAge: 1000 * 60 * 60 * 172800
    }
};

//////////////////////////////////////////
// Server init
var debug = require('debug')('smarthepia:server');
var http = require('http');
var port = normalizePort(process.env.PORT || '3000');
app.set('port', port);

/**
 * Create HTTP server.
 */
var server = http.createServer(app);
var io = require('socket.io')(server);


/////////////////////////////////////////






// Check server mode (dev, prod)
// Use sessions for tracking logins
/*if(app.get('env') === 'production'){

    // Trust first proxy (NGNIX)
    app.set('trust proxy', 1);

    // Serve secure cookie
    sessionParams.cookie.secure = true;

    sessionMiddleware = session(sessionParams);
    app.use(sessionMiddleware);
}else{
    sessionMiddleware = session(sessionParams);
    app.use(sessionMiddleware);
}*/

var sessionMiddleware = session(sessionParams);
app.use(sessionMiddleware);
io.use(function(socket, next) {
    sessionMiddleware(socket.request, socket.request.res, next)
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

var wsRouter = require('./routes/ws');


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

app.use('/ws', wsRouter);


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




io.on('connection', function(socket){

    console.log("Yessss", socket.request.session.userId);

    socket.on('message', function (data) {

        console.log(data);
        var json = JSON.parse(data);

        io.sockets.emit('message', json.name);

    });
});

/**
 * Listen on provided port, on all network interfaces.
 */
server.listen(port);
server.on('error', onError);
server.on('listening', onListening);

function normalizePort(val) {
    var port = parseInt(val, 10);

    if (isNaN(port)) {
        // named pipe
        return val;
    }

    if (port >= 0) {
        // port number
        return port;
    }

    return false;
}

/**
 * Event listener for HTTP server "error" event.
 */

function onError(error) {
    if (error.syscall !== 'listen') {
        throw error;
    }

    var bind = typeof port === 'string'
        ? 'Pipe ' + port
        : 'Port ' + port;

    // handle specific listen errors with friendly messages
    switch (error.code) {
        case 'EACCES':
            console.error(bind + ' requires elevated privileges');
            process.exit(1);
            break;
        case 'EADDRINUSE':
            console.error(bind + ' is already in use');
            process.exit(1);
            break;
        default:
            throw error;
    }
}

/**
 * Event listener for HTTP server "listening" event.
 */

function onListening() {
    var addr = server.address();
    var bind = typeof addr === 'string'
        ? 'pipe ' + addr
        : 'port ' + addr.port;
    debug('Listening on ' + bind);
}


module.exports = app;
