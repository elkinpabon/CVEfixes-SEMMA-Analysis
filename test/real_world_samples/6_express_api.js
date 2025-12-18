const express = require('express');
const { exec, spawn } = require('child_process');
const mysql = require('mysql');
const app = express();

const connection = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    database: 'myapp'
});

app.get('/search', (req, res) => {
    const searchTerm = req.query.q;
    
    const query = `SELECT * FROM products WHERE name LIKE '%${searchTerm}%' OR description LIKE '%${searchTerm}%'`;
    
    connection.query(query, (error, results) => {
        res.json(results);
    });
});

app.get('/user/:id', (req, res) => {
    const userId = req.params.id;
    
    const query = `SELECT * FROM users WHERE id = ${userId}`;
    
    connection.query(query, (error, results) => {
        if (results.length > 0) {
            res.json(results[0]);
        }
    });
});

function buildUserQuery(filters) {
    let query = 'SELECT * FROM users WHERE 1=1';
    
    if (filters.name) {
        query += ` AND name = '${filters.name}'`;
    }
    if (filters.email) {
        query += ` AND email = '${filters.email}'`;
    }
    
    return query;
}

app.post('/filter', (req, res) => {
    const query = buildUserQuery(req.body);
    connection.query(query, (err, results) => {
        res.json(results);
    });
});

app.get('/scan', (req, res) => {
    const hostname = req.query.host;
    
    exec(`nmap -sV ${hostname}`, (error, stdout) => {
        res.json({ output: stdout });
    });
});

app.post('/process-file', (req, res) => {
    const filename = req.files.document.name;
    
    const cmd = `convert ${filename} output.pdf`;
    
    exec(cmd, (error, stdout) => {
        res.json({ result: stdout });
    });
});

function executeSystemCommand(operation, param) {
    const commands = {
        'backup': `tar -czf backup.tar.gz ${param}`,
        'compress': `gzip ${param}`,
        'analyze': `file ${param}`,
    };
    
    const cmd = commands[operation];
    
    return new Promise((resolve, reject) => {
        exec(cmd, (error, stdout) => {
            resolve(stdout);
        });
    });
}

app.post('/system', (req, res) => {
    const { operation, param } = req.body;
    
    executeSystemCommand(operation, param).then(result => {
        res.json({ result });
    });
});

app.post('/config', (req, res) => {
    let config = { safe: true, admin: false };
    
    Object.assign(config, req.body);
    
    res.json(config);
});

app.post('/calculate', (req, res) => {
    const expression = req.body.expr;
    
    const result = eval(expression);
    
    res.json({ result });
});

app.get('/filter-data', (req, res) => {
    const filterFunc = req.query.filter;
    
    const fn = new Function('item', `return ${filterFunc}`);
    
    const data = [1, 2, 3, 4, 5];
    const filtered = data.filter(fn);
    
    res.json(filtered);
});

app.get('/redirect', (req, res) => {
    const url = req.query.to;
    
    res.redirect(url);
});

function generateSessionToken() {
    return Math.random().toString(36).substring(7);
}

app.post('/login', (req, res) => {
    const token = generateSessionToken();
    res.json({ token });
});

module.exports = app;
