var app = require("express")();

var http = require('http').Server(app);
var bodyParser = require('body-parser');
const { ScreepsServer, TerrainMatrix } = require('./screeps-server-mockup');
const _ = require('./screeps-server-mockup/node_modules/lodash');
const server = new ScreepsServer();
var bot_logs = []
var bots = []

//const tickbot = require('./tick-bot')
//const mainbot = require('./main')

app.use(bodyParser.json())
app.post('/',function(req,res){
	var msg=req.body.msg;
	console.log("python: " + msg);
	res.json({ msg: msg })
});

app.post('/reset',async function(req,res){
	console.log("Resetting world.");
	bots = []
	try{
		await server.world.reset();
	}
	catch(error){
		res.status(500).json({"error":error})
	}
	res.status(200).send()
});

app.post('/make_stub',async function(req,res){
	console.log("Making Stub world.");
	var result
	try{
		await server.world.stubWorld();
		res.status(200).send()
	}
	catch(error){
		res.status(500).json({"error":error})
	}
});

app.get('/world/load',async function(req,res){
	var data = await server.world.load()
	console.log("Getting world.load()");
	res.json(data)
});

app.get('/driver/getAllRooms',async function(req,res){
	var data = await server.driver.getAllRooms()
	console.log("Getting driver.getAllRooms()");
	res.json(data)
});

app.post('/world/addRoom',async function(req,res){
	console.log("Making room "+req.body.msg);
	try{
		await server.world.addRoom(req.body.msg)
		res.status(201).send()
	}
	catch(error){
		console.log(error)
		res.status(500).json({"error":error})
	}
});

app.post('/world/addRoom/simple',async function(req,res){
	room = req.body.msg
	console.log("Making simple room as ",room);
	
	try{
		const terrain = new TerrainMatrix();
		const walls = [[10, 10], [10, 40], [40, 10], [40, 40]];
		_.each(walls, ([x, y]) => terrain.set(x, y, 'wall'));

		//Create a new room with terrain and basic objects
		await server.world.addRoom(room);
		await server.world.setTerrain(room, terrain);
		await server.world.addRoomObject(room, 'controller', 10, 10, { level: 0 });
		await server.world.addRoomObject(room, 'source', 10, 40, { energy: 1000, energyCapacity: 1000, ticksToRegeneration: 300 });
		await server.world.addRoomObject(room, 'mineral', 40, 40, { mineralType: 'H', density: 3, mineralAmount: 3000 });
		res.status(201).send()
	}
	catch(error){
		console.log(error)
		res.status(500).json({"error":error})
	}
});

app.post('/start_server',async function(req,res){
	console.log("Starting server");
	try{
		await server.start()
		res.status(200).send()
	}
	catch(error){
		console.log(error)
		res.status(500).json({"error":error})
	}
});

app.post('/tick',async function(req,res){

	return_log = []

	const num_ticks = req.body.msg.ticks;

	console.log("ticking for ",num_ticks)
	
	try{
	
		for (tick = 0; tick < num_ticks; tick++ ){

			bot_logs = {};
			notification_logs = {};
			memory_logs = {};
		
			_.forEach(bots, function(bot){
				bot_logs[bot.username] = [];
			});

			await server.tick();
			
			console.log('Tick '+ await server.world.gameTime);
			
			for (const bot of bots){
				notifications = [];
				_.forEach(await bot.newNotifications, ({ message }) => notifications.push('[notification]', message));
				notification_logs[bot.username] = notifications;
				memory_logs[bot.username] = JSON.parse(await bot.memory);
			};
			return_log[tick] = {'bot_logs': bot_logs, 'notification_logs': notification_logs, 'memory_logs': memory_logs, 'gametime': await server.world.gameTime -1, 'users': await server.driver.getAllUsers(), 'rooms': await server.world.roomObjects()}
		}
		res.status(200).json(return_log)	
	}
	catch(error){
		console.log(error)
		res.status(500).json({"error":error})
	}

});

app.post('/stop',async function(req,res){
	console.log("Stoping server /stop");
	try{
		await server.stop()
		res.status(200).send()
	}
	catch(error){
		res.status(500).json({"error":error})
	}
	process.exit()
});

app.post('/world/addBot',async function(req,res){
	const username = req.body.msg.username;
	const room = req.body.msg.room;
	const x = parseInt(req.body.msg.x);
	const y = parseInt(req.body.msg.y);
	const modules = {
		main: "module.exports.loop = " + req.body.msg.main,
		//main: `module.exports.loop = ${mainbot.loop.toString()}`,
		//main: `module.exports.loop = ${tickbot.main.toString()}`,
	}

	console.log("Adding bot: "+ username+" "+room+" "+x+" "+y);
	try{
		bot = await server.world.addBot({username: username, room: room, x: x, y: y, modules: modules});
		bot.on('console', (logs, results, userid, username) => {
            _.each(logs, line => bot_logs[username].push(`[console|${username}] ${line}`));
		});
		bots.push(bot)
		res.status(201).send()
	}
	catch(error){
		console.log(error)
		res.status(500).json({"error":error})
	}
});

http.listen(3000, function(){
	console.log('listening...');
	          });
