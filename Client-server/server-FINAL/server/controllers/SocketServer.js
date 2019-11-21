
const express = require("express");
const server = require('http').Server(express);
const io = require('socket.io')(server);
const userModel = require('../models/User');
const pointModel =  require('../models/Point');
const appConfig = require("../configs/app");
var seedrandom = require('seedrandom');
var mapInfor = new Array(appConfig.map.row_nums);
let allUsers = [];
let trap = appConfig.map.trap;
var tisoX  = 0;
var tisoO  = 0;
const TEAMX=1;
const TEAMO=2;
const ZERO=0;
var Connected_X = "0";
var Connected_O = "0" ;
var Connected_Display = "0";



var time_out = appConfig.time_out;
var count_time = 0 ;
var team_time_out = ""
var interval;

// các biên cho nước danh tiep theo
var xold;
var oold;
var turn;
var match_number =1;
var inGame = true;
time_out  = time_out*10;
seedrandom('hello.', { global: true });
function countdownTimer(){
  if(count_time > 0)
  {
    count_time =  count_time - 1;
  }
}

function countDown(){
  clearInterval(interval);
  count_time = time_out;
  interval = setInterval(function(){
    countdownTimer();
    io.sockets.emit("countDown", {"turn": turn, "countTime": count_time});
    if (count_time==0){
      if(inGame){
        if (turn=="X"){
          io.sockets.emit("time_Out", {"team": "X", "round": match_number });
          tisoO+=1;
        }else{
          io.sockets.emit("time_Out", {"team": "O", "round": match_number });
          tisoX+=1;
        }
        match_number+=1;
        emitRound();
        emitScore();
      }
      clearInterval(interval);
    }
  }, 100); //Dem 0.1s 
}

function emitRound(){
  io.emit("round", {"round": match_number });
}

function emitScore(){
  io.emit("score",{"X": tisoX, "O": tisoO,  });
}

// giá trị 0 là chưa ai đi, 1 là X đã đi qua, 2 là O đã đi qua và 3 là chướng ngại vật
function resetMap(){
  let ncol = appConfig.map.row_nums;
  let z=0;
  let x=1;
  let o=2
  let t=3
  mapInfor = new Array(ncol);
  for (let i = 0; i < ncol; i++) {
    mapInfor[i] = new Array(ncol);
  } 
  for (let i = 0; i < ncol; i++) {
    for (let j = 0;j< ncol; j++) {
      mapInfor[i][j]=z;
    }
  }
  let zero = 0
  mapInfor[zero][zero] = x;
  mapInfor[ncol-1][ncol-1] = o;
  for(let i=0; i<trap; i++){
    let x =Math.floor(Math.random()*((ncol+1)/2-1)+1);
    let y =Math.floor(Math.random()*(ncol-1) +1);
    mapInfor[x][y] = t;
    mapInfor[ncol-x-1][ncol-y-1] = t;
  }
  xold = pointModel.newPoint(zero,zero,"X");
  oold = pointModel.newPoint(ncol-1, ncol-1,"O");
}

function emitMap(){
  io.emit("new_Map",{"map": mapInfor, "ncol": appConfig.map.row_nums, "X": xold, "O": oold  });
}

function convertNumbertoTeam(name){
  if (name == 1){
    return "X";
  }else if (name == 2){
    return "O";
  }
}
function convertTeamtoNumber(name){
  if (name == "X"){
    return TEAMX;
  }else if (name == "O"){
    return TEAMO;
  }
}
// Kiem tra nuoc di co thoa man khong
function checkPoint(point){
  let result = 0;
  let team = convertTeamtoNumber(point.type);
  if (mapInfor[point.x][point.y]==0){
    mapInfor[point.x][point.y]=team;
  }else{
    result = team;
  }
  return result;
}


let socketServer = () => {
  return new Promise((resolve, reject) => {
    io.on('connection', (socket)  => {
      let team = socket.handshake.query.team;
      let idDisplay;
      var idX;
      var idO;
      if ((team=="X"||socket.handshake.headers.team=="X") && Connected_X==0){
        idX = socket.id;
        Connected_X = 1;
        io.sockets.emit("connected",{"team": "X"});
        console.log("Da ket noi team X");

      }else if((team=="O"||socket.handshake.headers.team=="O") && Connected_O==0){
        idO = socket.id;
        Connected_O = 1;
        io.sockets.emit("connected",{"team": "O"});
        console.log("Da ket noi team O");
      }else{
        Connected_Display = 1;
        idDisplay = socket.id;
        // resetMap();
        // emitMap();
        console.log("Da ket noi giao dien");
      }
      //Ngăt kết nối team
      socket.on("disconnected", function(data){
        let team = data.team;
        if (team == "X"){
          if (io.sockets.sockets[idX]){
            io.sockets.sockets[idX].disconnect();
          }
          Connected_X=0;
          console.log("Da ngat ket noi team X");
        }else if (team=="O") {
          if (io.sockets.sockets[idO]){
            io.sockets.sockets[idO].disconnect();
          }
            Connected_O=0;
            console.log("Da ngat ket noi team O");
        }
      })

      // Lấy thông tin đội 
      socket.on("Infor", function(data){
        try{
          data = JSON.parse(data)
        }catch(e){}
        console.log("Get infor from client");
        io.sockets.emit("Infor",data);
      });
      
      socket.on("restart", function(){
        seedrandom('hello.', { global: true });
        console.log("restart");
        match_number = 1;
        tisoX=0;
        tisoO=0;
        Connected_O=0;
        Connected_X=0;
        emitRound();
        emitScore();
      });

      // Bắt đầu trận đấu
      socket.on("start_Game", function(){
        console.log("Start new game: "+match_number);
        resetMap();
        emitMap();
        inGame=true;
        if (match_number==6){
          let end;
          if (tisoO>tisoX){
            end = TEAMO;
          }else{
            end = TEAMX;
          }
          io.sockets.emit("end_Game",{"team": end});
        }
        if (match_number%2==1){
          console.log("team X di");
          turn="X";
          io.emit("change_Turn", {"point": oold, "turn": turn, "result": "C"});
          countDown();
        }else{
          console.log("team O di");
          turn="O"
          io.emit("change_Turn", {"point": xold, "turn": turn, "result": "C"});
          countDown();
        }
      });

      // Nhan nuoc di
      socket.on("moving", function(point){

        try{
          point = JSON.parse(point)
        }catch(e){}
        console.log("moved "+point.x+" "+point.y+" "+point.type);
        turn = point.type;
        
        let result = checkPoint(point);
        if (result==ZERO){
          if (turn=="X"){
            turn="O";
            console.log("Den luot team O");
            io.sockets.emit("displayPoint", point);
            io.sockets.emit("change_Turn", {"point": point, "turn": turn, "result": "C"});
            countDown();
          }else if(turn=="O"){
            turn="X";
            console.log("Den luot team X");
            io.sockets.emit("displayPoint", point);
            io.sockets.emit("change_Turn", {"point": point, "turn": turn, "result": "C"});
            countDown();
          }
        }else{
          inGame=false
          io.sockets.emit("game_Over", {"result": convertNumbertoTeam(result), "round": match_number });
          if (result==TEAMX){
            console.log("Team x thua tran "+match_number);
            tisoO+=1;
          }else if(result==TEAMO){
            console.log("Team o thua tran "+match_number);
            tisoX+=1;
          }
          match_number+=1;
          emitRound()
          emitScore()
        }

      });

      // socket.on("score", function(data){
      //   io.sockets.emit("score", {
      //     X: tisoX,
      //     O: tisoO 
      //   });
      //   console.log(data);
      // });

    });



    server.listen(3000, () => {
      resolve();
    });
    server.on("error", (error) => {
      reject(error);
    })
  })
}

module.exports = socketServer;
