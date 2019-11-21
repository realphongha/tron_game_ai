const express = require("express");
const appConfig = require("../configs/app");

module.exports = () => {
  let router = express.Router();

  router.get("/display", (req, res) => {
    res.render("display.html", {
      table_size : appConfig.map
    });
  });
  return router;
}
