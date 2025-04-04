const fs = require('fs');
const path = require('path');

// Create build directory if it doesn't exist
const buildDir = path.join(__dirname, 'build');
if (!fs.existsSync(buildDir)) {
  fs.mkdirSync(buildDir);
  console.log('Created build directory');
}

// Create public directory inside build if it doesn't exist
const publicDir = path.join(buildDir, 'public');
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir);
  console.log('Created public directory');
}

// Create a simple index.html file
const indexHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Golf League Manager</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
  <script src="config.js"></script>
  <style>
    body {
      margin: 0;
      font-family: 'Roboto', sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      background-color: #f9f9f9;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
    }
    .header {
      background-color: #1e5631;
      color: white;
      padding: 1rem 2rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .card {
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      padding: 2rem;
      margin-bottom: 2rem;
    }
    .button {
      background-color: #1e5631;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 500;
      transition: background-color 0.3s;
    }
    .button:hover {
      background-color: #163f23;
    }
    .login-form {
      max-width: 400px;
      margin: 2rem auto;
    }
    .form-group {
      margin-bottom: 1rem;
    }
    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
    }
    .form-group input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 1rem;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>Golf League Manager</h1>
  </div>
  <div class="container">
    <div class="card login-form">
      <h2>Login</h2>
      <p>Please sign in to access the Golf League Manager.</p>
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" placeholder="Enter your username" />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" placeholder="Enter your password" />
      </div>
      <button class="button" id="login-button">Sign In</button>
      <p id="error-message" style="color: red; display: none;"></p>
    </div>
    <div class="card">
      <h2>Welcome to Golf League Manager</h2>
      <p>This application helps you manage your golf league schedule, player swaps, scoring, and communications.</p>
      <p>Please sign in to access the features.</p>
    </div>
  </div>
  <script>
    document.getElementById('login-button').addEventListener('click', function() {
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      
      if (!username || !password) {
        const errorMessage = document.getElementById('error-message');
        errorMessage.textContent = 'Please enter both username and password';
        errorMessage.style.display = 'block';
        return;
      }
      
      // In a real application, this would connect to Cognito
      // For now, just show a message
      alert('Authentication functionality will be implemented when connected to AWS Cognito.');
    });
  </script>
</body>
</html>
`;

fs.writeFileSync(path.join(buildDir, 'index.html'), indexHtml);
console.log('Created index.html');

// Create a placeholder config.js file
const configJs = `
window.config = {
  region: "us-east-1",
  userPoolId: "PLACEHOLDER_USER_POOL_ID",
  userPoolWebClientId: "PLACEHOLDER_USER_POOL_CLIENT_ID",
  apiEndpoint: "PLACEHOLDER_API_ENDPOINT"
};
`;

fs.writeFileSync(path.join(buildDir, 'config.js'), configJs);
console.log('Created config.js');

console.log('Build completed successfully!');
