const express   = require("express");
const nunjucks  = require("nunjucks");
const config = require("./configs/app");


let socketServer = require('./controllers/SocketServer');

let startHTTP = () => {
  return new Promise((resolve, reject) => {
    let app = express();
    nunjucks.configure("views", {
        autoescape: true,
        watch :  true,
        express: app
    });
    let mainController = require("./controllers/MainController")(express);
    app.use("/", mainController);
    app.use(express.static("public"));
    // app.use(session({
    //     saveUninitialized: true,
    //     resave: false,
    //     secret: "DEMOMVC",
    //     cookie: {maxAge: 2592000000, secure : false}, // equivalent to 1 month
    //     store: new MongoStore({
    //       url: config.dbConnectionString,
    //       autoRemove: 'interval',
    //       autoRemoveInterval: 10, // In minutes. Default
    //       collection : config.session_collection
    //     })
    // }));


    app.listen(8888, () => {
      console.log("[HTTP SERVER] Server is running in port 8888");
      resolve();
    })

  })
}

Promise.all([
  startHTTP(),
  socketServer()
]).then(() => {
  console.log("Application is running...")
}).catch(err => {
  console.log(err);
})
