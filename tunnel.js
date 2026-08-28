const localtunnel = require('localtunnel');
const fs = require('fs');

(async () => {
  try {
    const tunnel = await localtunnel({ port: 8080 });
    console.log('====================================================');
    console.log('PUBLIC_URL: ' + tunnel.url);
    console.log('====================================================');
    fs.writeFileSync('public_url.txt', tunnel.url);

    tunnel.on('close', () => {
      console.log('Tunnel closed');
    });
    tunnel.on('error', (err) => {
      console.error('Tunnel error:', err);
    });
  } catch (e) {
    console.error('Failed to create tunnel:', e);
  }
})();
