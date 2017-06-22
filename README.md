# Bucket Protection

A simple app to add OAuth-based authentication in front of an S3 bucket-based static website.

## Usage

1. Check out from GitHub

   ```
   git co https://github.com/iandees/bucket-protection.git
   ```

1. Create virtual environment and install dependencies

   ```
   cd bucket-protection
   virtualenv --python=python3 venv
   venv/bin/activate
   pip install -r requirements.txt
   ```

1. [Set up at least one OAuth provider](#oauth-config)

1. Run the app

   ```
   S3_BUCKET=secret-bucket FLASK_DEBUG=True FLASK_APP=wsgi.py flask run
   ```

1. Test it by loading a secret S3 object via your newly-running app. Load a URL in your browser like `http://127.0.0.1:8000/my/secret/object` (corresponding to `s3://secret-bucket/my/secret/object`). The first time you will be redirected to `http://127.0.0.1:8000/login` and asked to login. After a successful login you will be redirected back to the secret object.

## OAuth Config

The app currently supports authenticating with Slack, Facebook, and Google.

### Setting up Slack

1. Create an OAuth application by going to the [Slack API Apps Page](https://api.slack.com/apps) and clicking the "Create New App" button in the upper right.
1. In the "App Name" text box, enter a meaningful name. Your users will see this when they authenticate. In the "Development Slack Team", select the team you want to associate this app with.
1. Note the Client ID and Client Secret that Slack gives you. You'll pass these into bucket-protection as environment variables later.
1. In the "OAuth & Permissions" page for your app, look for the "Redirect URLs" section and add "https://<your app here>/callback/slack". Also, add the `identity.basic` scope in the "Permission Scopes" section and save changes.

You're done! When you launch the app with `flask run` above, make sure you include `SLACK_APP_ID=<your app Client ID>` and `SLACK_APP_SECRET=<your app Client Secret>` environment variables amongst the others (before `S3_BUCKET=...`).
