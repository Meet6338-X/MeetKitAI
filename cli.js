#!/usr/bin/env node

const { Command } = require('commander');
const fs = require('fs-extra');
const path = require('path');
const { version } = require('./package.json');

// ANSI color codes - zero dependencies, works everywhere
const colors = {
  reset: '\x1b[0m',
  blue: '\x1b[34m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  gray: '\x1b[90m',
  bold: '\x1b[1m',
};

const log = {
  info: (msg) => console.log(`${colors.blue}${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✔ ${msg}${colors.reset}`),
  warn: (msg) => console.log(`${colors.yellow}⚠ ${msg}${colors.reset}`),
  error: (msg) => console.error(`${colors.red}✖ ${msg}${colors.reset}`),
  gray: (msg) => console.log(`${colors.gray}${msg}${colors.reset}`),
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
    const targetDir = path.resolve(options.path);
    const agentSourceDir = path.join(__dirname, '.agent');
    const agentTargetDir = path.join(targetDir, '.agent');

    log.info(`Initializing MeetKit AI in: ${targetDir}`);

    try {
      // Check if source .agent folder exists
      if (!await fs.pathExists(agentSourceDir)) {
        log.error('Source .agent directory not found in the package.');
        log.gray('This might be a packaging issue. Please reinstall the package.');
        process.exit(1);
      }

      // Check if target .agent folder exists
      if (await fs.pathExists(agentTargetDir) && !options.force) {
        log.warn('.agent directory already exists.');
        log.gray('Use --force to overwrite: meetkit-ai init --force');
        return;
      }

      log.gray('Copying templates...');
      await fs.copy(agentSourceDir, agentTargetDir, { overwrite: true });

      log.success('MeetKit AI initialized successfully!');
      log.info('You can now use the agents and workflows in your project.');
      log.gray(`Installed to: ${agentTargetDir}`);

    } catch (err) {
      log.error(`Error initializing MeetKit AI: ${err.message}`);
      process.exit(1);
    }
  });

program
  .command('update')
  .description('Update the .agent folder to the latest version')
  .option('-p, --path <targetPath>', 'Target path where .agent folder exists', '.')
  .action(async (options) => {
    const targetDir = path.resolve(options.path);
    const agentSourceDir = path.join(__dirname, '.agent');
    const agentTargetDir = path.join(targetDir, '.agent');

    log.info(`Updating MeetKit AI in: ${targetDir}`);

    try {
      if (!await fs.pathExists(agentTargetDir)) {
        log.error('.agent directory not found. Run "meetkit-ai init" first.');
        process.exit(1);
      }

      if (!await fs.pathExists(agentSourceDir)) {
        log.error('Source .agent directory not found in the package.');
        process.exit(1);
      }

      log.gray('Updating templates...');
      await fs.copy(agentSourceDir, agentTargetDir, { overwrite: true });

      log.success('MeetKit AI updated successfully!');
      log.gray(`Updated: ${agentTargetDir}`);

    } catch (err) {
      log.error(`Error updating MeetKit AI: ${err.message}`);
      process.exit(1);
    }
  });

program
  .command('info')
  .description('Show information about the installed MeetKit AI')
  .option('-p, --path <targetPath>', 'Target path to check', '.')
  .action(async (options) => {
    const targetDir = path.resolve(options.path);
    const agentTargetDir = path.join(targetDir, '.agent');

    console.log(`\n${colors.bold}MeetKit AI v${version}${colors.reset}\n`);

    if (await fs.pathExists(agentTargetDir)) {
      log.success(`Installed at: ${agentTargetDir}`);

      // Count agents and skills
      const agentsDir = path.join(agentTargetDir, 'agents');
      const skillsDir = path.join(agentTargetDir, 'skills');
      const workflowsDir = path.join(agentTargetDir, 'workflows');

      const countItems = async (dir) => {
        if (!await fs.pathExists(dir)) return 0;
        const items = await fs.readdir(dir);
        return items.length;
      };

      const agentCount = await countItems(agentsDir);
      const skillCount = await countItems(skillsDir);
      const workflowCount = await countItems(workflowsDir);

      log.gray(`  Agents: ${agentCount}`);
      log.gray(`  Skills: ${skillCount}`);
      log.gray(`  Workflows: ${workflowCount}`);
    } else {
      log.warn('MeetKit AI is not initialized in this directory.');
      log.gray('Run "meetkit-ai init" to get started.');
    }

    console.log('');
  });

program.parse();
