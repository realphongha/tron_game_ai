var express = require("express");
var app = express();
app.set("views","./views");
var server = require("http").Server(app);
var io = require("socket.io")(server);
server.listen(3000);
console.log("hay");
io.on("connection", function(socket){
	console.log("Co nguoi connection: "+socket.id);


	socket.on("disconnect", function(){
		console.log(socket.id+" disconnected");
	});

	socket.on("Moving",  function(data){
		console.log(data);
		io.sockets.emit("Change_turn", data);
		socket.emit("Change_turn", data); // send return
		socket.broadcast.emit("Change_turn", data); //send another 
		//io.to("socketid").emit()... solo
	});
});
