/**
 * MUESTRAS VULNERABLES - JAVASCRIPT
 * Ejemplos reales de vulnerabilidades para pruebas exhaustivas
 */

// ============================================================================
// 1. XSS - VULNERABILIDADES REALES
// ============================================================================

// XSS_1: innerHTML directo
function displayUserProfile(userData) {
    document.getElementById('profile').innerHTML = userData.bio;
}

// XSS_2: insertAdjacentHTML
function addComment(comment) {
    const commentDiv = document.getElementById('comments');
    commentDiv.insertAdjacentHTML('beforeend', '<p>' + comment + '</p>');
}

// XSS_3: document.write
function renderPage(userInput) {
    document.write('<h1>' + userInput + '</h1>');
}

// XSS_4: Template literals inseguras
function buildHTML(title, content) {
    return `<div class="container"><h1>${title}</h1><p>${content}</p></div>`;
}

// XSS_5: eval con input del usuario
function executeUserCode(code) {
    eval(code);
}

// XSS_6: jQuery html()
function setUserContent(content) {
    $('#content').html(content);
}

// XSS_7: dangerouslySetInnerHTML en React
const UserProfile = ({ userData }) => (
    <div dangerouslySetInnerHTML={{ __html: userData.bio }} />
);


// ============================================================================
// 2. SQL INJECTION - VULNERABILIDADES REALES (Node.js + Database)
// ============================================================================

// SQL_1: Query concatenation
function getUserByIdVulnerable(userId) {
    const query = "SELECT * FROM users WHERE id = " + userId;
    return database.query(query);
}

// SQL_2: Template literals en SQL
function searchUsers(searchTerm) {
    const query = `SELECT * FROM users WHERE name LIKE '%${searchTerm}%'`;
    return database.execute(query);
}

// SQL_3: Format string
function getEmailVulnerable(email) {
    const query = `SELECT * FROM users WHERE email = '${email}'`;
    return db.query(query);
}

// SQL_4: Object key injection
function filterByField(field, value) {
    const query = `SELECT * FROM users WHERE ${field} = '${value}'`;
    return database.query(query);
}


// ============================================================================
// 3. COMMAND INJECTION - VULNERABILIDADES REALES
// ============================================================================

// CMD_1: exec con child_process
function pingServer(hostname) {
    const { exec } = require('child_process');
    exec('ping -c 1 ' + hostname, (error, stdout, stderr) => {
        console.log(stdout);
    });
}

// CMD_2: system call
function runCommand(cmd) {
    const { execSync } = require('child_process');
    return execSync(cmd).toString();
}

// CMD_3: spawn con shell
function executeScript(scriptName) {
    const { spawn } = require('child_process');
    const child = spawn('bash', ['-c', 'python ' + scriptName]);
}

// CMD_4: shell=true equivalent
function checkService(serviceName) {
    const { execFileSync } = require('child_process');
    return execFileSync('sh', ['-c', 'systemctl status ' + serviceName]);
}


// ============================================================================
// 4. PATH TRAVERSAL - VULNERABILIDADES REALES
// ============================================================================

// PATH_1: Archivo desde parámetro directo
function readFile(filename) {
    const fs = require('fs');
    return fs.readFileSync(filename, 'utf8');
}

// PATH_2: Path concatenation
function getUserFile(userId, filename) {
    const path = require('path');
    const filePath = './uploads/' + userId + '/' + filename;
    return require('fs').readFileSync(filePath, 'utf8');
}

// PATH_3: join sin validación
function serveFile(baseDir, userPath) {
    const path = require('path');
    const fullPath = path.join(baseDir, userPath);
    return require('fs').readFileSync(fullPath, 'utf8');
}

// PATH_4: Express request.params directo
app.get('/file/:filename', (req, res) => {
    const file = './downloads/' + req.params.filename;
    res.sendFile(file);
});

// PATH_5: URL parameter
app.get('/view', (req, res) => {
    const filepath = req.query.path;
    res.sendFile(filepath);
});


// ============================================================================
// 5. INSECURE DESERIALIZATION - VULNERABILIDADES REALES
// ============================================================================

// DESER_1: JSON.parse de untrusted source
function parseUserData(jsonString) {
    const data = JSON.parse(jsonString);
    eval(data.code);  // VULNERABLE
    return data;
}

// DESER_2: unserialize (si usando librería)
function loadSession(sessionData) {
    const result = unserialize(sessionData);
    return result;
}

// DESER_3: Function constructor
function executeCode(codeString) {
    const func = new Function(codeString);
    return func();
}


// ============================================================================
// 6. UNSAFE EVAL - VULNERABILIDADES REALES
// ============================================================================

// EVAL_1: eval directo
function calculateExpression(expression) {
    return eval(expression);
}

// EVAL_2: setTimeout con string
function delayedExecution(code) {
    setTimeout(code, 1000);
}

// EVAL_3: setInterval con string
function repeatedExecution(code) {
    setInterval(code, 5000);
}

// EVAL_4: Function constructor
function dynamicFunction(funcBody) {
    return new Function(funcBody);
}


// ============================================================================
// 7. PROTOTYPE POLLUTION - VULNERABILIDADES REALES
// ============================================================================

// PP_1: Object assign desde untrusted
function mergeConfig(userConfig) {
    const defaultConfig = { safe: true };
    Object.assign(defaultConfig, userConfig);
    return defaultConfig;
}

// PP_2: Recursive merge
function deepMerge(target, source) {
    for (let key in source) {
        if (typeof source[key] === 'object') {
            deepMerge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
}


// ============================================================================
// 8. OPEN REDIRECT - VULNERABILIDADES REALES
// ============================================================================

// REDIRECT_1: Redirect directo
function redirectUser(redirectUrl) {
    window.location = redirectUrl;
}

// REDIRECT_2: Express redirect
app.get('/redirect', (req, res) => {
    const url = req.query.url;
    res.redirect(url);
});

// REDIRECT_3: href assignment
function goToPage(page) {
    window.location.href = '/page?redirect=' + page;
}


// ============================================================================
// EJEMPLOS SEGUROS (para comparación)
// ============================================================================

// SAFE_1: innerHTML with escape
function displayUserProfileSafe(userData) {
    const div = document.createElement('div');
    div.textContent = userData.bio;
    document.getElementById('profile').appendChild(div);
}

// SAFE_2: Parameterized query
function getUserByIdSafe(userId) {
    const query = "SELECT * FROM users WHERE id = ?";
    return database.query(query, [userId]);
}

// SAFE_3: spawn without shell
function pingServerSafe(hostname) {
    const { spawn } = require('child_process');
    const child = spawn('ping', ['-c', '1', hostname]);
}

// SAFE_4: Path validation
function readFileSafe(filename) {
    const path = require('path');
    const allowedDir = path.resolve('./safe_uploads');
    const fullPath = path.resolve(path.join(allowedDir, filename));
    
    if (!fullPath.startsWith(allowedDir)) {
        throw new Error('Invalid path');
    }
    return require('fs').readFileSync(fullPath, 'utf8');
}

// SAFE_5: JSON.parse sin eval
function parseUserDataSafe(jsonString) {
    return JSON.parse(jsonString);
}
