#!/usr/bin/env node

import { execSync, spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';

// CONFIGURATION
const REPO_URL = "https://github.com/VS251/engram-os.git"; 
const APP_DIR = path.join(process.cwd(), 'engram-core');

console.log(chalk.bold.blue('\n Engram Private OS Installer\n'));

async function main() {
  
  // --- CHECKS ---
  try { execSync('python3 --version', { stdio: 'ignore' }); } 
  catch (e) { console.error(chalk.red('Python 3 is missing.')); process.exit(1); }

  try { execSync('ollama --version', { stdio: 'ignore' }); } 
  catch (e) { console.warn(chalk.yellow('Warning: Ollama CLI not found.')); }

  // --- INSTALLATION ---
  if (!fs.existsSync(APP_DIR)) {
    const answer = await inquirer.prompt([{
      type: 'confirm', name: 'install', message: `Install Engram to ${APP_DIR}?`, default: true
    }]);
    if (!answer.install) process.exit(0);

    const spinner = ora('Downloading Source Code...').start();
    try {
      execSync(`git clone ${REPO_URL} ${APP_DIR}`, { stdio: 'ignore' });
      spinner.succeed('Downloaded.');
    } catch (error) { spinner.fail('Download failed.'); process.exit(1); }
  }

  // --- PYTHON SETUP ---
  const spinner = ora('Installing Python Dependencies...').start();
  try {
    const reqPath = path.join(APP_DIR, 'requirements.txt');
    if (fs.existsSync(reqPath)) {
        execSync(`pip3 install -r ${reqPath}`, { cwd: APP_DIR, stdio: 'ignore' });
        spinner.succeed('Dependencies ready.');
    } else {
        spinner.warn('No requirements.txt found.');
    }
  } catch (error) {
    spinner.fail('Pip install failed.');
  }

  const env = { 
    ...process.env, 
    QDRANT_HOST: '127.0.0.1',
    QDRANT_PORT: '6333',
    OLLAMA_HOST: 'http://127.0.0.1:11434'
  };

  console.log(chalk.green('\n Launching Engram OS...'));
  console.log(chalk.gray('   - Backend API: http://127.0.0.1:8000'));
  console.log(chalk.gray('   - UI Dashboard: http://localhost:8501'));
  console.log(chalk.yellow('\nPress Ctrl+C to stop everything.'));

  const command = `npx concurrently -n "BRAIN,UI" -c "blue,magenta" \
    "cd ${APP_DIR} && python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000" \
    "cd ${APP_DIR} && python3 -m streamlit run app.py"`;

  try {
    execSync(command, { stdio: 'inherit', env: env });
  } catch (e) {
    console.log(chalk.blue('Goodbye!'));
  }
}

main();