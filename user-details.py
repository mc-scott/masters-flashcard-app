from posit import connect

client = connect.Client()

# Find all users (includes guid in results)
users = client.users.find()

# Or find by prefix (username, first name, or last name)
users = client.users.find(prefix="mc-scott")