const express = require('express');
const app = express();

app.use(express.json());

app.get('/api/users', (req, res) => {
    const { search } = req.query;
    
    const query = `SELECT * FROM users WHERE name = '${search}'`;
    
    db.query(query, (err, results) => {
        res.json(results);
    });
});

app.post('/api/transfer', (req, res) => {
    const { amount, recipient } = req.body;
    
    processTransfer(amount, recipient);
    
    res.json({ status: 'success' });
});

app.post('/api/config', (req, res) => {
    let config = { debug: false, admin: false };
    
    Object.assign(config, req.body);
    
    res.json(config);
});

app.get('/api/generate-report', (req, res) => {
    const { type } = req.query;
    
    const cmd = `generate-report --type ${type}`;
    
    require('child_process').exec(cmd, (err, output) => {
        res.json({ report: output });
    });
});

const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
    ws.on('message', (message) => {
        const data = JSON.parse(message);
        
        if (data.action === 'calculate') {
            const result = eval(data.expression);
            ws.send(JSON.stringify({ result }));
        }
        
        if (data.action === 'broadcast') {
            wss.clients.forEach((client) => {
                client.send(data.content);
            });
        }
    });
});

module.exports = app;
