import os
import subprocess
from pathlib import Path

from sqlalchemy import text
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlmodel import create_engine

from dw_blog.config import Settings


settings = Settings()
root_dir = settings.ROOT_DIR
sync_db_url = settings.DATABASE_URL_SYNC

environment = settings.ENVIRONMENT
fixture_files = [
    "users.sql",
    "categories.sql",
    "blogs.sql",
    "categoryblogs.sql",
    "blogauthors.sql",
    "bloglikes.sql",
    "blogsubscribers.sql",
    "tag.sql",
    "tagsubscribers.sql",
    "posts.sql",
    "tagposts.sql",
    "postauthors.sql",
    "postlikers.sql",
    "postfavourites.sql",
]

# Check if the environment is dev
if environment == "dev":
    sync_engine = create_engine(sync_db_url, echo=True, future=True)
    # Drop the database if it exists
    if database_exists(sync_engine.url):
        drop_database(sync_engine.url)
    # Initialize the db:
    create_database(sync_engine.url)
    # Run migrations
    # Define the command to apply the migration
    command = ['alembic', 'upgrade', 'head']
    # Run the command
    subprocess.run(['python', '-m'] + command)
    # Get the path to the fixtures folder of the project
    fixture_dir = os.path.join(str(Path(__file__).parent), "fixtures")
    # Seed the database
    with sync_engine.begin() as conn:
        # Open the file in the root folder
        for file_name in fixture_files:
            with open(os.path.join(fixture_dir, file_name)) as f:
                contents = f.read()
                split_content = contents.split(";")

                for line in split_content:
                    if line.strip() != "":
                        conn.execute(text(line.strip()))
else:
    print("Not in dev environment, skipping seed")
