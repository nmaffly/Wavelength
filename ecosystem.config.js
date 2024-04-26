module.exports = {
  apps : [{
    name: "app",
    script: "gunicorn",
    interpreter: "none",
    args: "-w 4 -b 0.0.0.0:4000 app:app",
    autorestart: true, // Ensure this is true, although true is the default value
    watch: false // Set to true if you want PM2 to restart your app when files change
  }]
};
