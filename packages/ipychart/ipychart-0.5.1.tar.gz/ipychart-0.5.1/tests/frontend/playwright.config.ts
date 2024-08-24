const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

module.exports = {
    ...baseConfig,
    timeout: 240000,
    webServer: {
        command: 'jlpm start --allow-root',
        port: '8888',
        timeout: 120 * 1000,
        reuseExistingServer: !process.env.CI,
    },
    retries: 1,
};
