# AWS RDS Database Running Schedule

[![GitHub](https://img.shields.io/github/license/gammarers/aws-rds-database-running-schedule-stack?style=flat-square)](https://github.com/gammarers/aws-rds-database-running-schedule-stack/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarer/aws-rds-database-running-schedule-stack?style=flat-square)](https://www.npmjs.com/package/@gammarer/aws-rds-database-running-schedule-stack)
[![PyPI](https://img.shields.io/pypi/v/gammarer.aws-rds-database-running-schedule-stack?style=flat-square)](https://pypi.org/project/gammarer.aws-rds-database-running-schedule-stack/)
[![Nuget](https://img.shields.io/nuget/v/Gammarer.CDK.AWS.RdsDatabaseRunningScheduleStack?style=flat-square)](https://www.nuget.org/packages/Gammarers.CDK.AWS.RdsDatabaseRunningScheduler/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/gammarers/aws-rds-database-running-schedule-stack/release.yml?branch=main&label=release&style=flat-square)](https://github.com/gammarers/aws-rds-database-running-schedule-stack/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/gammarers/aws-rds-database-running-schedule-stack?sort=semver&style=flat-square)](https://github.com/gammarers/aws-rds-database-running-schedule-stack/releases)

This AWS CDK Construct Stack controls the starting and stopping of RDS DB instances and clusters based on specified tags, ensuring they only run during working hours. It uses EventBridge Scheduler to trigger a StepFunctions State Machine at the start and end of the working hours(default 07:50(UTC) - 21:10(UTC)), which then starts or stops the databases depending on the mode.

## Fixed

* RDS Aurora Cluster
* RDS Instance

## Resources

This construct creating resource list.

* EventBridge Scheduler execution role
* EventBridge Scheduler
* StepFunctions StateMahcine (star or stop controle)
* StepFunctions StateMahcine execution role

## Install

### TypeScript

#### install by npm

```shell
npm install @gammarers/aws-rds-database-running-schedule-stack
```

#### install by yarn

```shell
yarn add @gammarers/aws-rds-database-running-schedule-stack
```

#### install by pnpm

```shell
pnpm add @gammarers/aws-rds-database-running-schedule-stack
```

#### install by bun

```shell
bun add @gammarers/aws-rds-database-running-schedule-stack
```

### Python

```shell
pip install gammarers.aws-rds-database-running-schedule-stack
```

### C# / .NET

```shell
dotnet add package Gammarers.CDK.AWS.RdsDatabaseRunningScheduleStack
```

## Example

```python
import { RdsDatabaseRunningScheduler, DatabaseType } from '@gammarer/aws-rds-database-running-schedule-stack';

new RdsDatabaseRunningScheduleStack(stack, 'RdsDatabaseRunningScheduleStack', {
  targetResource: {
    tagKey: 'WorkHoursRunning', // already tagging to rds instance or cluster
    tagValues: ['YES'], // already tagging to rds instance or cluster
  },
  enableScheduling: true,
  startSchedule: {
    timezone: 'Asia/Tokyo',
    minute: '55',
    hour: '8',
    week: 'MON-FRI',
  },
  stopSchedule: {
    timezone: 'Asia/Tokyo',
    minute: '5',
    hour: '19',
    week: 'MON-FRI',
  },
});
```

## License

This project is licensed under the Apache-2.0 License.
