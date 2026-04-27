# Pushing to GitLab when SSH times out

If `git push gitlab main` hangs or times out over SSH (VPN/firewall often blocks port 22), use **HTTPS with a Personal Access Token**.

## 1. Create a token in GitLab

1. Open https://gitlab.nicholls.edu and sign in (SSO).
2. Top right: your avatar → **Preferences** (or **Edit profile**).
3. Left sidebar: **Access Tokens**.
4. **Token name:** e.g. `Mac PRAMS push`
5. **Expiration:** pick a date (e.g. 1 year).
6. **Scopes:** check **write_repository**.
7. Click **Create personal access token**.
8. **Copy the token** (you won’t see it again).

## 2. Push once using the token

From your project directory (replace `YOUR_GITLAB_USERNAME` and `YOUR_TOKEN`):

```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"

# Use token in URL for this one push (no interactive prompt)
git remote set-url gitlab https://YOUR_GITLAB_USERNAME:YOUR_TOKEN@gitlab.nicholls.edu/chriscastille/prams.git
git push gitlab main

# Remove token from URL afterward (store only the host in the remote)
git remote set-url gitlab https://gitlab.nicholls.edu/chriscastille/prams.git
```

Use your GitLab **username** (e.g. `ccastille1` or `chriscastille`) and the token you copied. The token is only in the URL for that one command; the last line clears it.

## 3. Later pushes

After you’ve pushed once with the token, Git may have cached the credentials. If it asks again:

- **Username:** your GitLab username  
- **Password:** paste the same **token** (not your SSO password)

If you don’t want to re-enter it, use the token-in-URL trick again for one push, or set a credential helper (e.g. macOS Keychain) and enter the token once.
