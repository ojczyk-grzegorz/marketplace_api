fastapi
uv
ruff
pydantic
sqlmodel
sqlalchemy
starlette exceptions
pytest
duckdb
httpx

<!-- https://stackoverflow.com/questions/11919391/postgresql-error-fatal-role-username-does-not-exist -->
sudo -u postgres createuser owning_user

`sudo -u` allows you to run a command as a specific user instead of root.

So sudo -u postgres createuser owning_user runs the createuser command as the postgres user (rather than as root, which would be the default with just sudo). This is necessary because PostgreSQL commands typically need to be run as the postgres system user.




`sudo -u postgres -i`
opens an interactive login shell as the postgres user.

The -i flag simulates an initial login, which means:

It starts a login shell as the postgres user
Sets up the environment as if postgres had logged in directly
Allows you to run multiple PostgreSQL commands without prefixing each one with sudo -u postgres
This is useful when you need to run several postgres commands in succession - you can just type createuser owning_user, createdb marketplace, etc. directly instead of sudo -u postgres createuser owning_user each time.

To exit back to your regular user, just type exit.