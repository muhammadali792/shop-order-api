const express        = require("express");
const logger         = require("./logger");
const { startConsumer } = require("./consumer");
const config         = require("./config");

const app = express();
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "notif-service" });
});

startConsumer();

app.listen(config.port, () => {
  logger.info(`Notification service running on port ${config.port}`);
});

module.exports = app;
