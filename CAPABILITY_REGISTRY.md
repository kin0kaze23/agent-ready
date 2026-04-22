# Capability Registry — Phase 1

> The structured database of tools, services, and capabilities that AI agents need.
> This is the foundation of agent-ready.

---

## Phase 1 Capabilities

### 1. Vercel CLI
| Field | Value |
|-------|-------|
| **ID** | `vercel_cli` |
| **Plain English** | "The tool that puts your website on the internet" |
| **Detect** | `vercel --version` |
| **Install (Mac)** | `brew install vercel-cli` |
| **Install (Linux/Win)** | `npm install -g vercel` |
| **Account** | https://vercel.com/signup |
| **Auth** | `vercel login` |
| **Setup** | 1. Install 2. Create account 3. Link project |
| **Error patterns** | "command not found: vercel", "Not logged in", "Could not find a project" |
| **Provides** | `deploy_to_vercel`, `create_preview` |
| **Related tasks** | "deploy", "publish website", "push to production" |

### 2. GitHub CLI
| Field | Value |
|-------|-------|
| **ID** | `github_cli` |
| **Plain English** | "The tool that connects your code to GitHub" |
| **Detect** | `gh --version` |
| **Install (Mac)** | `brew install gh` |
| **Install (Linux)** | `sudo apt install gh` |
| **Install (Win)** | `winget install GitHub.cli` |
| **Account** | https://github.com/signup |
| **Auth** | `gh auth login` |
| **Setup** | 1. Install 2. Create account 3. Authenticate |
| **Error patterns** | "command not found: gh", "http error: 401", "could not read Username" |
| **Provides** | `push_to_github`, `create_repository`, `create_pull_request` |
| **Related tasks** | "push to github", "create a repository", "open a pull request" |

### 3. Node.js
| Field | Value |
|-------|-------|
| **ID** | `nodejs` |
| **Plain English** | "The tool that runs JavaScript code on your computer" |
| **Detect** | `node --version` |
| **Install (Mac)** | `brew install node` |
| **Install (Linux)** | `sudo apt install nodejs npm` |
| **Install (Win)** | `winget install OpenJS.NodeJS.LTS` |
| **Setup** | 1. Install Node.js 2. Install dependencies (`npm install`) |
| **Error patterns** | "command not found: node", "command not found: npm", "Cannot find module" |
| **Provides** | `run_javascript`, `install_npm_packages` |
| **Related tasks** | "run the app", "install dependencies", "start the server" |

### 4. Python
| Field | Value |
|-------|-------|
| **ID** | `python` |
| **Plain English** | "The tool that runs Python code on your computer" |
| **Detect** | `python3 --version` |
| **Install (Mac)** | `brew install python` |
| **Install (Linux)** | `sudo apt install python3 python3-pip` |
| **Install (Win)** | `winget install Python.Python.3` |
| **Setup** | 1. Install Python 2. Install dependencies (`pip install -r requirements.txt`) |
| **Error patterns** | "command not found: python3", "command not found: pip", "ModuleNotFoundError" |
| **Provides** | `run_python`, `install_python_packages` |
| **Related tasks** | "run the script", "install requirements", "run the analysis" |

### 5. API Key Configuration
| Field | Value |
|-------|-------|
| **ID** | `api_key_config` |
| **Plain English** | "Adding secret keys so your app can connect to services" |
| **Detect** | Check for missing .env file or required environment variables |
| **Setup** | 1. Explain what's needed 2. Guide to create API key 3. Store in .env 4. Verify |
| **Error patterns** | "API key not found", "Missing required environment variable", "Authentication failed" |
| **Provides** | `authenticate_with_service`, `access_api` |
| **Related tasks** | "connect to [service]", "use the API", "authenticate" |

---

## How to Add New Capabilities

1. Identify the capability from trace-eval error patterns
2. Fill in the structure above with all fields
3. Test detection — verify the detect command works on all platforms
4. Test install — verify the install commands work on all platforms
5. Test error patterns — verify the patterns match real trace-eval output
6. Test setup flow — verify the complete flow works end-to-end

---

## Future Capabilities (Post-Phase 1)

Docker, AWS CLI, Supabase CLI, Railway CLI, Stripe CLI, Doppler CLI, MCP Servers.
Priority determined by trace-eval alpha user data.
