# Deploying Gatanan on Alibaba Cloud

This guide runs the Gatanan backend (`backend/app/main.py`) on an Alibaba Cloud
compute instance. Once it is running, the backend genuinely executes on Alibaba
Cloud and calls Qwen Cloud, which is exactly what the hackathon's proof of
deployment asks for.

You need two things for the submission:
1. A link to a code file in the repo that uses the Qwen Cloud base URL. That is
   already true: see `backend/app/config.py` (`dashscope_base_url =
   https://dashscope-intl.aliyuncs.com/compatible-mode/v1`) and `backend/app/llm.py`.
2. A screenshot of your Alibaba Cloud console showing the instance **Running**.
   The steps below produce that.

The easiest path is **Simple Application Server**. ECS works the same way; notes
for it are at the end.

---

## 1. Create the server

1. In the Alibaba Cloud console, open **Simple Application Server**.
2. Click **Create Server**.
3. Region: **Singapore** (matches the Qwen Cloud International endpoint).
4. Image: **Ubuntu 22.04** (or any recent Ubuntu / OpenCloudOS Linux image).
5. Plan: the smallest / free-trial option is fine.
6. Create it, and wait until its status shows **Running**.
7. Note the server's **Public IP address**.

## 2. Open the port

The backend serves on port 8000, so the firewall must allow it.

1. Open your server, go to the **Firewall** tab.
2. Add a rule: allow **TCP**, port **8000**.

## 3. Connect to the server

Click **Connect** on your server to open the browser terminal (logs you in as
`root`). No SSH keys needed.

## 4. Install and run the backend

Paste these into the terminal, one block at a time. Replace the repo URL with
your own if different, and paste your real key where shown.

```bash
# system packages
apt update && apt install -y python3-pip git

# get the code
git clone https://github.com/Aisha-Aliyu/gatanan.git
cd gatanan/backend

# python dependencies
pip3 install -r requirements.txt

# your Qwen Cloud key (this stays on the server, never committed)
echo 'DASHSCOPE_API_KEY=sk-REPLACE_WITH_YOUR_KEY' > .env

# start the backend, kept running in the background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

Give it a few seconds, then confirm it started:

```bash
curl http://localhost:8000/
```

You should see JSON that includes `"status": "running"` and the Qwen Cloud
endpoint.

## 5. Verify from your browser

Open these in any browser, using your server's public IP:

- `http://YOUR_PUBLIC_IP:8000/` shows the backend is live and names the Qwen
  Cloud endpoint it calls.
- `http://YOUR_PUBLIC_IP:8000/docs` is the interactive API. Open the `/plan`
  endpoint, click **Try it out**, paste a folktale into `tale_text`, and run it.
  You will get back a full Story Bible and Shot List generated live by Qwen
  Cloud, running on your Alibaba Cloud server. This is excellent footage for the
  demo video.

## 6. Take the proof screenshot

In the Alibaba Cloud console, open the **Simple Application Server** list (or the
server's overview page) so your instance and its **Running** status are visible.
Take a screenshot. That image is your proof of deployment for the submission
form. A second screenshot of the browser showing the `/` response is a good
extra.

---

## Using ECS instead

The flow is identical with two differences:
- Instead of the Firewall tab, open port 8000 in the instance's **Security
  Group** (add an inbound rule: TCP, 8000, source `0.0.0.0/0`).
- Connect with the **VNC / Workbench** terminal in the console, or by SSH.

Everything from step 4 onward is the same, and the proof screenshot is the ECS
instance list showing status **Running**.

---

## Notes

- Your API key lives only in the server's `.env` file. It is never committed;
  the repository `.gitignore` already excludes `.env`.
- To stop the server: `pkill -f uvicorn`. To see logs: `cat server.log`.
- The image-generation step is run separately with `run_day3.py` to control
  cost; the deployed API covers the multi-agent planning pipeline.
