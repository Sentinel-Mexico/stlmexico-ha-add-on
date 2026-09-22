# Vikunja Home Assistant Add-on

## What it does

Vikunja is a self-hosted, open-source task and project management application.
It is a lightweight alternative to Todoist, Trello, and Microsoft To Do. You
can manage tasks, create lists and kanban boards, set due dates and reminders,
share projects with family members, and sync across all your devices.

Everything runs locally on your Home Assistant instance.

## Getting started

Once the add-on is running, click **Vikunja** in the Home Assistant sidebar
to open the web interface. Create your first account, then start organizing
your tasks.

You can also access Vikunja directly at:

```
http://<YOUR_HA_IP>:3456
```

## Mobile and desktop apps

Vikunja works with several clients:

- **Web interface** — built-in, accessible from the sidebar or direct URL
- **Mobile apps** — third-party apps available for iOS and Android that
  support the Vikunja API
- **DAV sync** — sync tasks with any CalDAV-compatible app (Apple Reminders,
  Thunderbird, GNOME Calendar, etc.)

When connecting a client, use the server URL `http://<YOUR_HA_IP>:3456`.

## Configuration

### Service secret

Used internally to sign authentication tokens. The add-on auto-generates
one on first start and persists it. Only set this if migrating from an
existing Vikunja instance.

### Frontend URL

If you access Vikunja from outside your network (via a domain and reverse
proxy), set this to the full URL (e.g. `https://tasks.example.com`). This
ensures email links and sharing URLs point to the right place.

### Allow registration

Enabled by default so you can create your first account. **Disable this**
once all household members have accounts.

### Database

By default Vikunja uses **SQLite**, which requires no extra setup. The database
file is stored in the add-on's persistent storage.

If you prefer to use an external **MySQL** or **MariaDB** server, change the
database type to `mysql` and fill in the connection details:

| Setting           | Description                                    |
| ----------------- | ---------------------------------------------- |
| Database type     | `sqlite` (default) or `mysql`                  |
| Database host     | Hostname or IP of your MySQL/MariaDB server    |
| Database port     | Port number (default `3306`)                   |
| Database name     | Name of the database (e.g. `vikunja`)          |
| Database user     | Username for the database connection           |
| Database password | Password for the database connection           |

Make sure the database and user exist before starting the add-on. For example
in MySQL/MariaDB:

```sql
CREATE DATABASE vikunja CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'vikunja'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON vikunja.* TO 'vikunja'@'%';
FLUSH PRIVILEGES;
```

### Email (SMTP)

Configure SMTP to enable email notifications, password resets, task
reminders, and team invitations. Without SMTP, users can still log in and
use Vikunja, but email-dependent features will not work.

## Data and backups

All data is stored in `/data/vikunja/` inside the add-on's persistent
storage:

- `vikunja.db` — the SQLite database (only when using SQLite)
- `files/` — uploaded file attachments

Back up the entire directory regularly. The Home Assistant backup feature
includes add-on data automatically. If using MySQL/MariaDB, back up the
external database separately.

## Support

- [Vikunja Website](https://vikunja.io)
- [Vikunja Documentation](https://vikunja.io/docs)
- [Vikunja GitHub](https://github.com/go-vikunja/vikunja)
- [Vikunja Community](https://community.vikunja.io)
