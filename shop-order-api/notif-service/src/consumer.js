const Redis  = require("ioredis");
const logger = require("./logger");
const mailer = require("./mailer");
const config = require("./config");

const subscriber = new Redis(config.redisUrl);

async function handleEvent(event, data) {
  switch (event) {
    case "order_created":
      await mailer.sendOrderConfirmation(data);
      break;
    case "order_cancelled":
      await mailer.sendOrderCancellation(data);
      break;
    default:
      logger.warn("Unknown event receive", { event });
  }
}

function startConsumer() {
  subscriber.subscribe("order_events", (err, count) => {
    if (err) {
      logger.error("Failed to subscribe to Redis channel", { error: err.message });
      process.exit(1);
    }
    logger.info(`Subscribed to ${count} Redis channel(s)`);
  });

  subscriber.on("message", async (channel, message) => {
    try {
      const { event, data } = JSON.parse(message);
      logger.info("Event received", { channel, event });
      await handleEvent(event, data);
    } catch (err) {
      logger.error("Failed to process message", { error: err.message });
    }
  });

  subscriber.on("error", (err) => {
    logger.error("Redis connection error", { error: err.message });
  });
}

module.exports = { startConsumer };
