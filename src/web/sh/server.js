'use strict';

// Module dependencies
var app = require('./app');
var io = require('./sockets/socket').io;
var http = require('http');

// Create server instance
var server = http.createServer(app);

// Module variables
var debug = require('debug')('smarthepia:server');
var port = normalizePort(app.get('port'));
var env = app.get('env');
var host = app.get('host');

// Bind socket.io to server
io.listen(server);

// Listen on provided port, on all network interfaces.
server.listen(port);
server.on('error', onError);
server.on('listening', onListening);

// Normalise port
function normalizePort(val) {
    var port = parseInt(val, 10);

    // Named pipe
    if (isNaN(port)) {
        return val;
    }

    // Port number
    if (port >= 0) {
        return port;
    }
    return false;
}

// Event listener for HTTP server "error" event.
function onError(error) {
    if (error.syscall !== 'listen') {
        throw error;
    }

    var bind = typeof port === 'string' ? 'Pipe ' + port : 'Port ' + port;

    // Handle specific listen errors with friendly messages
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

// Event listener for HTTP server "listening" event
function onListening() {
    var addr = server.address();
    var bind = typeof addr === 'string' ? 'pipe ' + addr : 'port ' + addr.port;
    debug('Listening on ' + bind);
}

// Conditionally export module
if(require.main != module) {
    module.exports = server;
}