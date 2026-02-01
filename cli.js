#!/usr/bin/env node

const { Command } = require('commander');
const fs = require('fs-extra');
const path = require('path');
const chalk = require('chalk');
const { version } = require('./package.json');

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

    console.log(chalk.blue(`Initializing MeetKit AI in: ${targetDir}`));

    try {
      // Check if source .agent folder exists
      if (!await fs.pathExists(agentSourceDir)) {
        console.error(chalk.red('Error: Source .agent directory not found in the package.'));
        process.exit(1);
      }

      // Check if target .agent folder exists
      if (await fs.pathExists(agentTargetDir) && !options.force) {
        console.warn(chalk.yellow('Warning: .agent directory already exists. Use --force to overwrite.'));
        return;
      }

      console.log(chalk.gray('Copying templates...'));
      await fs.copy(agentSourceDir, agentTargetDir, { overwrite: true });

      console.log(chalk.green('✔ MeetKit AI initialized successfully!'));
      console.log(chalk.blue('You can now use the agents and workflows in your project.'));
      console.log(chalk.gray(`Installed to: ${agentTargetDir}`));

    } catch (err) {
      console.error(chalk.red('Error initializing MeetKit AI:'), err.message);
      process.exit(1);
    }
  });

program.parse();
