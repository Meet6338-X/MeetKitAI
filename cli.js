#!/usr/bin/env node

const { Command } = require('commander');
const fs = require('fs-extra');
const path = require('path');
const { version } = require('./package.json');

// ANSI color codes - zero dependencies
const colors = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  italic: '\x1b[3m',
  underline: '\x1b[4m',

  // Foreground colors
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  gray: '\x1b[90m',
};

const ui = {
  banner: () => {
    console.log(`\n${colors.cyan}${colors.bold}`);
    console.log(`    __  __           _   _  ___ _      _   _ ___ `);
    console.log(`   |  \\/  |___ ___ _| |_| |/ (_) |_   /_\\ |_ _/ |`);
    console.log(`   | |\\/| / -_) -_)  _| ' <| | |  _| / _ \\ | || |`);
    console.log(`   |_|  |_\\___\\___|\\__|_|\\_\\_|_|\\__|/_/ \\_\\___|_|`);
    console.log(`${colors.reset}${colors.gray}             Powered by Advanced Agentic Coding${colors.reset}\n`);
  },

  heading: (msg) => console.log(`${colors.bold}${colors.white}${msg}${colors.reset}`),

  status: (type, msg) => {
    const icons = {
      info: `${colors.blue}ℹ${colors.reset}`,
      success: `${colors.green}✔${colors.reset}`,
      warn: `${colors.yellow}⚠${colors.reset}`,
      error: `${colors.red}✖${colors.reset}`,
      wait: `${colors.cyan}▹${colors.reset}`,
    };
    console.log(`${icons[type] || ''} ${msg}`);
  },

  box: (title, lines, color = colors.cyan) => {
    const width = Math.max(title.length, ...lines.map(l => l.length)) + 4;
    const horizontal = '─'.repeat(width);

    console.log(`${color}┌─ ${colors.bold}${title} ${colors.reset}${color}${'─'.repeat(width - title.length - 2)}┐${colors.reset}`);
    lines.forEach(line => {
      const padding = ' '.repeat(width - line.length);
      console.log(`${color}│  ${colors.reset}${line}${padding}${color}  │${colors.reset}`);
    });
    console.log(`${color}└${horizontal}┘${colors.reset}`);
  }
};

const getStats = async (agentTargetDir) => {
  const countItems = async (dir) => {
    try {
      if (!await fs.pathExists(dir)) return 0;
      const items = await fs.readdir(dir);
      return items.filter(item => !item.startsWith('.')).length;
    } catch { return 0; }
  };

  return {
    agents: await countItems(path.join(agentTargetDir, 'agents')),
    skills: await countItems(path.join(agentTargetDir, 'skills')),
    workflows: await countItems(path.join(agentTargetDir, 'workflows')),
  };
};

const program = new Command();

program
  .name('meetkit-ai')
  .description('MeetKit AI Agent templates - Skills, Agents, and Workflows')
  .version(version);

program
  .command('init')
  .description('Install the .agent folder into your project')
  .option('-p, --path <targetPath>', 'Target path to install .agent folder', '.')
  .option('-f, --force', 'Overwrite existing .agent folder')
  .action(async (options) => {
    ui.banner();

    const targetDir = path.resolve(options.path);
    const agentSourceDir = path.join(__dirname, '.agent');
    const agentTargetDir = path.join(targetDir, '.agent');

    ui.status('wait', `Initializing In: ${colors.dim}${targetDir}${colors.reset}`);

    try {
      if (!await fs.pathExists(agentSourceDir)) {
        ui.status('error', 'Source directory not found. Please clean install MeetKit AI.');
        process.exit(1);
      }

      if (await fs.pathExists(agentTargetDir) && !options.force) {
        ui.status('warn', `.agent directory already exists at this location.`);
        console.log(`${colors.gray}  Hint: Use --force to overwrite: ${colors.reset}meetkit-ai init --force\n`);
        return;
      }

      ui.status('wait', 'Assembling AI templates...');
      await fs.copy(agentSourceDir, agentTargetDir, { overwrite: true });

      const stats = await getStats(agentTargetDir);

      console.log('');
      ui.box('Deployment Successful', [
        `Version:   ${colors.bold}${version}${colors.reset}`,
        `Agents:    ${colors.bold}${stats.agents}${colors.reset}`,
        `Skills:    ${colors.bold}${stats.skills}${colors.reset}`,
        `Workflows: ${colors.bold}${stats.workflows}${colors.reset}`,
        ``,
        `${colors.italic}${colors.gray}Installed to: ${agentTargetDir}${colors.reset}`
      ], colors.green);

      console.log(`\n${colors.cyan}Next Steps:${colors.reset}`);
      console.log(`${colors.gray}• Open ARCHITECTURE.md to explore the system`);
      console.log(`${colors.gray}• Use /orchestrate or /plan in your chat interface`);
      console.log(`${colors.gray}• Check .agent/workflows for specific commands\n`);

    } catch (err) {
      ui.status('error', `Initialization Failed: ${err.message}`);
      process.exit(1);
    }
  });

program
  .command('update')
  .description('Update the .agent folder to the latest version')
  .option('-p, --path <targetPath>', 'Target path where .agent folder exists', '.')
  .action(async (options) => {
    ui.banner();

    const targetDir = path.resolve(options.path);
    const agentSourceDir = path.join(__dirname, '.agent');
    const agentTargetDir = path.join(targetDir, '.agent');

    ui.status('wait', `Synchronizing: ${colors.dim}${agentTargetDir}${colors.reset}`);

    try {
      if (!await fs.pathExists(agentTargetDir)) {
        ui.status('error', '.agent directory not found. Please run "meetkit-ai init" first.');
        process.exit(1);
      }

      ui.status('wait', 'Updating core patterns...');
      await fs.copy(agentSourceDir, agentTargetDir, { overwrite: true });

      const stats = await getStats(agentTargetDir);

      console.log('');
      ui.box('Sync Complete', [
        `Updated to: ${colors.bold}v${version}${colors.reset}`,
        `Current Toolkit:`,
        `  ↳ ${stats.agents} Specialists`,
        `  ↳ ${stats.skills} Core Skills`,
        `  ↳ ${stats.workflows} Smart Workflows`
      ], colors.blue);
      console.log('');

    } catch (err) {
      ui.status('error', `Update Failed: ${err.message}`);
      process.exit(1);
    }
  });

program
  .command('info')
  .description('Show information about the installed MeetKit AI')
  .option('-p, --path <targetPath>', 'Target path to check', '.')
  .action(async (options) => {
    ui.banner();

    const targetDir = path.resolve(options.path);
    const agentTargetDir = path.join(targetDir, '.agent');

    if (await fs.pathExists(agentTargetDir)) {
      const stats = await getStats(agentTargetDir);
      ui.box(`MeetKit AI System Info`, [
        `Status:    ${colors.green}Active${colors.reset}`,
        `Version:   ${colors.bold}${version}${colors.reset}`,
        `Location:  ${colors.dim}${agentTargetDir}${colors.reset}`,
        ``,
        `${colors.underline}Capability Map:${colors.reset}`,
        `  - ${colors.bold}${stats.agents}${colors.reset} Domain Agents`,
        `  - ${colors.bold}${stats.skills}${colors.reset} Functional Skills`,
        `  - ${colors.bold}${stats.workflows}${colors.reset} Task Workflows`
      ]);
    } else {
      ui.status('warn', 'MeetKit AI is not initialized in this directory.');
      console.log(`${colors.gray}  Run: ${colors.reset}npx meetkit-ai init\n`);
    }
    console.log('');
  });

program.parse();
