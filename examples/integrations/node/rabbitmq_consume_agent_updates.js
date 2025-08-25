// Consume agent update messages from RabbitMQ
// Usage: node rabbitmq_consume_agent_updates.js

const amqp = require('amqplib');

const QUEUE = process.env.AGENT_UPDATES_QUEUE || 'agent_updates';
const RABBIT_URL = process.env.RABBITMQ_URL || 'amqp://guest:guest@localhost:5672/';

(async () => {
  try {
    const conn = await amqp.connect(RABBIT_URL);
    const ch = await conn.createChannel();
    await ch.assertQueue(QUEUE, { durable: true });
    await ch.prefetch(10);

    console.log(`[*] Waiting for messages on ${QUEUE}. Press CTRL+C to exit.`);
    await ch.consume(
      QUEUE,
      (msg) => {
        if (msg) {
          try {
            const payload = JSON.parse(msg.content.toString());
            console.log('[x] Received:', payload);
          } catch (e) {
            console.log('[x] Received (raw):', msg.content.toString());
          }
          ch.ack(msg);
        }
      },
      { noAck: false }
    );
  } catch (err) {
    console.error('Consume failed:', err);
    process.exit(1);
  }
})();
