// Publish an agent update message to RabbitMQ
// Usage: node rabbitmq_publish_agent_update.js

const amqp = require('amqplib');

const QUEUE = process.env.AGENT_UPDATES_QUEUE || 'agent_updates';
const RABBIT_URL = process.env.RABBITMQ_URL || 'amqp://guest:guest@localhost:5672/';

(async () => {
  try {
    const conn = await amqp.connect(RABBIT_URL);
    const ch = await conn.createChannel();
    await ch.assertQueue(QUEUE, { durable: true });

    const cid = process.env.TEST_CONVERSATION_ID || 'demo-conv';
    const payload = {
      conversation_id: cid,
      event: 'agent:update',
      status: 'running',
      agent_id: 'agent-demo',
      data: { progress: 0.2, ts: Math.floor(Date.now() / 1000) },
    };

    const body = Buffer.from(JSON.stringify(payload));
    ch.sendToQueue(QUEUE, body, { contentType: 'application/json', persistent: true });
    console.log(`Published to ${QUEUE}:`, payload);
    await ch.close();
    await conn.close();
  } catch (err) {
    console.error('Publish failed:', err);
    process.exit(1);
  }
})();
