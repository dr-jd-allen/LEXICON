const { app, BrowserWindow, Menu, Tray, dialog, shell, ipcMain, Notification } = require('electron');
const { autoUpdater } = require('electron-updater');
const Store = require('electron-store');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs').promises;
const os = require('os');

// Configure store for settings
const store = new Store({
  defaults: {
    firstRun: true,
    apiKeys: {},
    dataPath: path.join(os.homedir(), 'Documents', 'LEXICON'),
    autoBackup: true,
    theme: 'professional',
    dockerPath: 'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'
  }
});

let mainWindow = null;
let tray = null;
let dockerProcess = null;
let setupWindow = null;

// Application icon
const iconPath = path.join(__dirname, 'assets', 'icon.ico');

// Check if running for first time
async function checkFirstRun() {
  if (store.get('firstRun')) {
    return await showSetupWizard();
  }
  return true;
}

// Setup wizard for first run
async function showSetupWizard() {
  return new Promise((resolve) => {
    setupWindow = new BrowserWindow({
      width: 800,
      height: 600,
      icon: iconPath,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
      },
      resizable: false,
      frame: false
    });

    setupWindow.loadFile('setup.html');

    ipcMain.once('setup-complete', (event, config) => {
      store.set('apiKeys', config.apiKeys);
      store.set('dataPath', config.dataPath);
      store.set('firstRun', false);
      setupWindow.close();
      resolve(true);
    });

    ipcMain.once('setup-cancel', () => {
      setupWindow.close();
      resolve(false);
    });
  });
}

// Check Docker status
async function checkDocker() {
  return new Promise((resolve) => {
    exec('docker info', (error) => {
      resolve(!error);
    });
  });
}

// Start Docker if not running
async function startDocker() {
  const dockerPath = store.get('dockerPath');
  
  if (!await checkDocker()) {
    const notification = new Notification({
      title: 'LEXICON',
      body: 'Starting Docker Desktop...',
      icon: iconPath
    });
    notification.show();

    try {
      dockerProcess = spawn(dockerPath, [], { detached: true });
      
      // Wait for Docker to start (max 60 seconds)
      let attempts = 0;
      while (!await checkDocker() && attempts < 60) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      }

      if (attempts >= 60) {
        throw new Error('Docker failed to start');
      }

      return true;
    } catch (error) {
      dialog.showErrorBox('Docker Error', 
        'Failed to start Docker Desktop. Please start it manually and restart LEXICON.');
      return false;
    }
  }
  
  return true;
}

// Start LEXICON services
async function startLexicon() {
  const notification = new Notification({
    title: 'LEXICON',
    body: 'Starting LEXICON services...',
    icon: iconPath
  });
  notification.show();

  return new Promise((resolve, reject) => {
    const projectPath = path.join(__dirname, '..');
    const deployScript = process.platform === 'win32' ? 'deploy-local.bat' : './deploy-local.sh';
    
    const deploy = spawn(deployScript, [], {
      cwd: projectPath,
      shell: true
    });

    deploy.stdout.on('data', (data) => {
      console.log(`LEXICON: ${data}`);
    });

    deploy.stderr.on('data', (data) => {
      console.error(`LEXICON Error: ${data}`);
    });

    deploy.on('close', (code) => {
      if (code === 0) {
        const successNotification = new Notification({
          title: 'LEXICON Ready',
          body: 'Click here to open LEXICON in your browser',
          icon: iconPath
        });
        
        successNotification.on('click', () => {
          shell.openExternal('http://localhost');
        });
        
        successNotification.show();
        resolve(true);
      } else {
        reject(new Error(`Deployment failed with code ${code}`));
      }
    });
  });
}

// Stop LEXICON services
async function stopLexicon() {
  return new Promise((resolve) => {
    exec('docker-compose -f docker-compose-local.yml down', {
      cwd: path.join(__dirname, '..')
    }, (error) => {
      if (!error) {
        const notification = new Notification({
          title: 'LEXICON',
          body: 'Services stopped',
          icon: iconPath
        });
        notification.show();
      }
      resolve(!error);
    });
  });
}

// Create system tray
function createTray() {
  tray = new Tray(iconPath);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open LEXICON',
      click: () => {
        shell.openExternal('http://localhost');
      }
    },
    {
      label: 'Open Documents Folder',
      click: () => {
        shell.openPath(store.get('dataPath'));
      }
    },
    { type: 'separator' },
    {
      label: 'Backup Now',
      click: async () => {
        exec('docker exec lexicon-backup-local /scripts/backup.sh', (error) => {
          const notification = new Notification({
            title: 'LEXICON Backup',
            body: error ? 'Backup failed' : 'Backup completed successfully',
            icon: iconPath
          });
          notification.show();
        });
      }
    },
    { type: 'separator' },
    {
      label: 'Services',
      submenu: [
        {
          label: 'Restart Services',
          click: async () => {
            await stopLexicon();
            await startLexicon();
          }
        },
        {
          label: 'Stop Services',
          click: stopLexicon
        },
        {
          label: 'View Logs',
          click: () => {
            const logsPath = path.join(__dirname, '..', 'logs');
            shell.openPath(logsPath);
          }
        }
      ]
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        createSettingsWindow();
      }
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Quick Start Guide',
          click: () => {
            shell.openPath(path.join(__dirname, 'Quick Start Guide.pdf'));
          }
        },
        {
          label: 'Support Website',
          click: () => {
            shell.openExternal('https://lexicon-support.com');
          }
        },
        { type: 'separator' },
        {
          label: 'About LEXICON',
          click: () => {
            dialog.showMessageBox({
              type: 'info',
              title: 'About LEXICON',
              message: 'LEXICON Legal AI System',
              detail: `Version: 1.0.0\nDeveloped for Allen Law Group\n\n5-Agent AI Architecture:\n• Claude Opus 4 (Orchestrator)\n• o3-pro-deep-research (Legal)\n• o4-mini-deep-research (Scientific)\n• gpt-4.5-research-preview (Writer)\n• Gemini 2.5 Pro (Editor)\n\n© 2024 Allen Law Group`,
              icon: iconPath,
              buttons: ['OK']
            });
          }
        }
      ]
    },
    { type: 'separator' },
    {
      label: 'Exit',
      click: async () => {
        const choice = dialog.showMessageBoxSync({
          type: 'question',
          buttons: ['Exit', 'Cancel'],
          defaultId: 1,
          title: 'Exit LEXICON',
          message: 'Are you sure you want to exit?',
          detail: 'This will stop all LEXICON services.',
          icon: iconPath
        });
        
        if (choice === 0) {
          await stopLexicon();
          app.quit();
        }
      }
    }
  ]);

  tray.setToolTip('LEXICON Legal AI System');
  tray.setContextMenu(contextMenu);
  
  tray.on('double-click', () => {
    shell.openExternal('http://localhost');
  });
}

// Create settings window
function createSettingsWindow() {
  const settingsWindow = new BrowserWindow({
    width: 600,
    height: 500,
    icon: iconPath,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    resizable: false
  });

  settingsWindow.loadFile('settings.html');
}

// Create splash screen
function createSplashScreen() {
  const splash = new BrowserWindow({
    width: 600,
    height: 400,
    frame: false,
    alwaysOnTop: true,
    transparent: true,
    icon: iconPath,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  splash.loadFile('splash.html');
  
  return splash;
}

// App event handlers
app.whenReady().then(async () => {
  // Show splash screen
  const splash = createSplashScreen();

  try {
    // Check first run
    if (!await checkFirstRun()) {
      app.quit();
      return;
    }

    // Check and start Docker
    splash.webContents.send('status-update', 'Checking Docker Desktop...');
    if (!await startDocker()) {
      splash.close();
      app.quit();
      return;
    }

    // Start LEXICON services
    splash.webContents.send('status-update', 'Starting LEXICON services...');
    await startLexicon();

    // Create tray icon
    createTray();

    // Close splash and show success
    setTimeout(() => {
      splash.close();
      
      // Open browser automatically on first run
      if (store.get('firstRun')) {
        shell.openExternal('http://localhost');
      }

      // Show ready notification
      const notification = new Notification({
        title: 'LEXICON Ready',
        body: 'LEXICON is running. Access it from the system tray.',
        icon: iconPath
      });
      notification.show();
    }, 2000);

  } catch (error) {
    splash.close();
    dialog.showErrorBox('LEXICON Error', `Failed to start: ${error.message}`);
    app.quit();
  }
});

app.on('window-all-closed', (event) => {
  // Prevent app from quitting when windows are closed
  event.preventDefault();
});

app.on('before-quit', async () => {
  // Clean shutdown
  await stopLexicon();
});

// Auto-updater
autoUpdater.on('update-available', () => {
  const notification = new Notification({
    title: 'LEXICON Update Available',
    body: 'A new version is available. Click to download.',
    icon: iconPath
  });
  
  notification.on('click', () => {
    autoUpdater.downloadUpdate();
  });
  
  notification.show();
});

autoUpdater.on('update-downloaded', () => {
  const choice = dialog.showMessageBoxSync({
    type: 'info',
    buttons: ['Restart Now', 'Later'],
    defaultId: 0,
    title: 'Update Ready',
    message: 'Update downloaded. Restart LEXICON to apply.',
    icon: iconPath
  });
  
  if (choice === 0) {
    autoUpdater.quitAndInstall();
  }
});

// Check for updates
app.whenReady().then(() => {
  autoUpdater.checkForUpdatesAndNotify();
});