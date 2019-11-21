var express = require("express");
var app = express();
var server = require("http").createServer(app);
server.listen(3000);
app.get("/p/:sa", function(req, res){
	res.send("Bach Tran")
});