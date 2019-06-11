
(async function () {
    const _ = require('./screeps-server-mockup/node_modules/lodash');
    const { ScreepsServer, TerrainMatrix } = require('./screeps-server-mockup');
    const tickbot = require('./tick-bot')
    const server = new ScreepsServer();

    try {
        // Initialize server
        await server.world.reset(); // reset world but add invaders and source keepers bots
        await server.world.stubWorld();

        // Add a bot in W0N1
        const modules = {
            main: `module.exports.loop = ${tickbot.main.toString()}`,
        }

        const bot1 = await server.world.addBot({ username: 'bot1', room: 'W0N1', x: 25, y: 25, modules });
       
        // Print console logs every tick
        bot1.on('console', (logs, results, userid, username) => {
            _.each(logs, line => console.log(`[console|${username}]`, line));
        });

        // Start server and run several ticks
        await server.start();
        for (let i = 0; i < 10; i += 1) {
            console.log('[tick]', await server.world.gameTime);
            await server.tick();
        }
    } catch (err) {
        console.error(err);
    } finally {
        // Stop server and disconnect storage
        server.stop();
        //process.exit(); // required as there is no way to properly shutdown storage :(
    }
}());
