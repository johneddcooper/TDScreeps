var app = require("express")();

var http = require('http').Server(app);
var bodyParser = require('body-parser');
const { ScreepsServer } = require('./screeps-server-mockup');
const _ = require('./screeps-server-mockup/node_modules/lodash');
const server = new ScreepsServer();
var bots = []
var bot_logs = []

const tickbot = require('./tick-bot')

app.use(bodyParser.json())
app.post('/',function(req,res){
	var msg=req.body.msg;
	console.log("python: " + msg);
	res.json({ msg: msg })
});

app.post('/reset',async function(req,res){
	console.log("Resetting world.");
	var result
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

app.post('/start_server',async function(req,res){
	bot_logs = []
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
	try{

		bots.forEach(bot => {
			bot.emit('console', ['log'], ['results'], bot.id, bot.username)
		});
		await server.tick()
		console.log('Tick '+ await server.world.gameTime)
		console.log("bot logs "+bot_logs)
		res.status(200).json({'logs': bot_logs, 'gametime': await server.world.gameTime})
	}
	catch(error){
		console.log(error)
		res.status(500).json({"error":error})
	}
});

app.post('/stop',async function(req,res){
	console.log("Stoping server");
	try{
		await server.stop()
		res.status(200).send()
	}
	catch(error){
		console.log(error)
		res.status(500).json({"error":error})
	}
	process.exit()
});

app.post('/world/addBot',async function(req,res){
	const username = req.body.msg.username;
	const room = req.body.msg.room;
	const x = req.body.msg.x;
	const y = req.body.msg.y;
	const modules = {
		//main: `module.exports.loop = ${req.body.msg.main}`,
		main: `module.exports.loop = ${tickbot.main.toString()}`,
	}

	console.log("Adding bot: "+ username+" "+room+" "+x+" "+y);
	try{
		bot = await server.world.addBot(username, room, x, y, modules);
		bot.on('console', (logs, results, userid, username) => {
			_.each(logs, line => console.log(`[console|${username}]`, line));
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
