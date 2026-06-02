const logger = require("./logger");

async function sendOrderConfirmation(data) {
  // Production mein: Nodemailer / SendGrid use karo
  // Ab ke liye: structured log jo email simulate kare
  logger.info("EMAIL SENT", {
    to:      data.user_email,
    subject: `Order #${data.order_id} Confirmed`,
    body:    `Your order of $${data.total} has been confirmed.`,
  });
}

async function sendOrderCancellation(data) {
  logger.info("EMAIL SENT", {
    to:      data.user_email,
    subject: `Order #${data.order_id} Cancelled`,
    body:    `Your order #${data.order_id} has been cancelled.`,
  });
}

module.exports = { sendOrderConfirmation, sendOrderCancellation };
