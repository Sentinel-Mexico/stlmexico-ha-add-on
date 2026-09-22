# Vikunja for Home Assistant

> Self-hosted task and project management.
> Open-source alternative to Todoist, Trello, and Microsoft To Do.

## What it does

Vikunja lets you manage tasks, lists, kanban boards, and calendars for your
household from within Home Assistant. It supports multiple users, shared
projects, labels, priorities, due dates, reminders, and CalDAV sync.

## Getting started

After installing the add-on, click **Start** and then open it from the sidebar.
You will be prompted to create your first account.

## Database

Vikunja supports two database options:

### SQLite (default)

No configuration needed. The database file is stored in the add-on's
persistent storage automatically. This is the simplest option for small
households.

### MariaDB (recommended for multiple users)

For better performance with multiple users or large amounts of data, use the
**MariaDB** add-on for Home Assistant:

1. Install the **MariaDB** add-on from the Home Assistant Add-on Store.
2. In the MariaDB add-on configuration, add a database and user:
   ```yaml
   databases:
     - vikunja
   logins:
     - username: vikunja
       password: YOUR_SECURE_PASSWORD
   rights:
     - username: vikunja
       database: vikunja
   ```
3. Start (or restart) the MariaDB add-on so it creates the database and user.
4. In this Vikunja add-on's configuration, set:
   - **database_type**: `mysql`
   - **database_password**: the password you chose in step 2
5. Restart Vikunja.

The host (`core-mariadb`), port (`3306`), database name (`vikunja`), and user
(`vikunja`) are already set by default — they match the HA MariaDB add-on. You
only need to change `database_type` to `mysql` and enter the password.

> **Important:** You must create the database and user in the MariaDB add-on
> configuration **before** starting Vikunja with MySQL mode. The add-on will
> try to auto-create the database, but this only works if the user has
> sufficient privileges.

## CalDAV

Vikunja supports CalDAV for syncing tasks with native calendar and reminder
apps. The CalDAV endpoint is:

```
http://<YOUR_HA_IP>:3456/dav/
```

## Email notifications

To enable email notifications, configure the mailer settings:

- **mailer_enabled**: `true`
- **mailer_host**: your SMTP server (e.g., `smtp.gmail.com`)
- **mailer_port**: usually `587` for TLS
- **mailer_username**: your email address
- **mailer_password**: your email password or app-specific password
- **mailer_from_email**: the "from" address for notifications

## Support

- [Vikunja documentation](https://vikunja.io/docs/)
- [This add-on's repository](https://github.com/go-vikunja/vikunja)
