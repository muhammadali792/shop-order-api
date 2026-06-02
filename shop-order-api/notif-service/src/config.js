require("dotenv").config();

module.exports = {
  redisUrl: process.env.REDIS_URL  || "redis://localhost:6379",
  port:     process.env.PORT       || 3000,
  appEnv:   process.env.APP_ENV    || "development",
};
