# 🧠 ungithub

**AI-powered codebase insight explorer** — just replace `github.com` with `ungithub.com` to unlock instant, smart analysis of any public repository.

> Example:  
> 🔗 `https://github.com/vercel/next.js`  
> becomes  
> 🔍 `https://ungithub.com/vercel/next.js`


## 🚀 What is ungithub?

**ungithub** helps you deeply understand any open-source project with the help of AI. Whether you're onboarding to a new codebase or just exploring, simply paste a GitHub URL (or replace `github` with `ungithub`) and get:

- 🔍 Auto-summarized repo insights
- 🧠 AI-generated explanations of files, folders, and logic
- 🧩 Embedding-based search across the entire repo
- 📎 Ask questions about the code like ChatGPT — but repo-specific

---

## 🛠️ Tech Stack

| Layer        | Tech                          |
|-------------|-------------------------------|
| Backend      | Python, FastAPI               |
| AI & Embedding | OpenAI / Gemini, LangChain, SentenceTransformers |
| Database     | MongoDB Atlas (Vector Search) |
| Frontend (optional) | Next.js, Tailwind CSS          |
| Hosting      | Vercel (frontend), Render/Fly.io (backend) |
| Repo Cloning | GitHub API / git              |

---

## 🧰 Features (Phase-wise)

### ✅ Phase 1 (Setup)
- [x] GitHub repo + project setup
- [ ] FastAPI backend scaffolded
- [ ] MongoDB Atlas w/ Vector Search
- [ ] OpenAI API integration setup

### 🔄 Phase 2 (Core Engine)
- [ ] Clone and parse GitHub repos
- [ ] Generate file-level and repo-level embeddings
- [ ] Store and search using MongoDB Vector Search
- [ ] Add natural language Q&A over codebase

### 🎯 Phase 3 (Frontend & UX)
- [ ] Build UI to enter repo URLs / browse insights
- [ ] Add file tree explorer + smart search bar
- [ ] Show AI summaries and explanations
- [ ] Shareable insight links (e.g., `ungithub.com/org/repo#env-setup`)

---

## 📦 Local Development

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### 🌐 Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

## 🌍 Deployment

- **Frontend:** Vercel (https://ungithub.com)
- **Backend:** Render / Fly.io / Railway
- **Database:** MongoDB Atlas with Vector Search enabled

## 🧠 Inspiration

Most devs struggle with onboarding into large codebases. We want to make codebases self-explanatory — like a smart dev mentor embedded into the repo itself.

## 🤝 Contributing

PRs are welcome! Feel free to fork this repo and open issues for bugs or features.

## 📄 License

MIT License

## 🙌 Built For

AI in Action Hackathon (Google x MongoDB x GitLab)

---