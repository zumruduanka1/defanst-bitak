const express = require("express");
const cors = require("cors");
const OpenAI = require("openai");
const nodemailer = require("nodemailer");
const { TwitterApi } = require("twitter-api-v2");
const fetch = require("node-fetch");

const app = express();
app.use(cors());
app.use(express.json());

const MY_EMAIL = process.env.MY_EMAIL;
const SECOND_EMAIL = process.env.SECOND_EMAIL;

// 🔑 AI
const openai = process.env.OPENAI_API_KEY
  ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
  : null;

// 🐦 TWITTER
const twitterClient = process.env.TWITTER_BEARER
  ? new TwitterApi(process.env.TWITTER_BEARER)
  : null;

// 📧 MAIL
const transporter =
  process.env.EMAIL_USER && process.env.EMAIL_PASS
    ? nodemailer.createTransport({
        service: "gmail",
        auth: {
          user: process.env.EMAIL_USER,
          pass: process.env.EMAIL_PASS
        }
      })
    : null;

// 📦 GEÇMİŞ (memory)
let history = [];

// 🧠 ANALİZ (GELİŞMİŞ)
async function analizEt(text) {
  if (!openai) return { skor: 50, durum: "Belirsiz" };

  try {
    const res = await openai.chat.completions.create({
      model: "gpt-4.1-mini",
      messages: [
        {
          role: "system",
          content:
            "Metni dezenformasyon açısından analiz et. JSON dön: {skor:0-100, durum:'Güvenli|Şüpheli|Riskli'}"
        },
        { role: "user", content: text }
      ]
    });

    return JSON.parse(res.choices[0].message.content);
  } catch {
    return { skor: 50, durum: "Hata" };
  }
}

// 🌍 FEED
app.get("/feed", async (req, res) => {
  let items = [];

  // Twitter
  try {
    if (twitterClient) {
      const t = await twitterClient.v2.search("gündem", { max_results: 3 });
      items.push(...t.data.data.map(x => ({ text: x.text, source: "Twitter" })));
    }
  } catch {}

  // Reddit fallback
  try {
    const r = await fetch("https://www.reddit.com/r/worldnews.json");
    const j = await r.json();
    items.push(
      ...j.data.children.slice(0, 3).map(x => ({
        text: x.data.title,
        source: "Reddit"
      }))
    );
  } catch {}

  // analiz
  let final = [];
  for (let i of items) {
    const a = await analizEt(i.text);
    final.push({ ...i, ...a });
  }

  res.json(final);
});

// 📊 ANALİZ + HISTORY + MAIL
app.post("/analiz", async (req, res) => {
  const { metin } = req.body;

  const sonuc = await analizEt(metin);

  // history ekle
  history.unshift({
    text: metin,
    ...sonuc,
    date: new Date().toLocaleString()
  });

  history = history.slice(0, 10);

  // mail
  if (transporter) {
    try {
      await transporter.sendMail({
        from: process.env.EMAIL_USER,
        to: [MY_EMAIL, SECOND_EMAIL].filter(Boolean),
        subject: "Analiz Sonucu",
        text: `${sonuc.durum} (%${sonuc.skor})`
      });
    } catch {}
  }

  res.json(sonuc);
});

// 📜 HISTORY API
app.get("/history", (req, res) => {
  res.json(history);
});

// 🌐 UI
app.get("/", (req, res) => {
  res.send(`
  <html>
  <head>
  <title>DEFANS PRO</title>
  <style>
  body {background:#0b1220;color:white;font-family:sans-serif;}
  .box {width:700px;margin:auto;margin-top:40px;}
  textarea {width:100%;padding:10px;border-radius:8px;}
  button {margin-top:10px;width:100%;padding:12px;background:linear-gradient(90deg,#4f46e5,#9333ea);color:white;border:none;}
  .bar {height:20px;margin-top:10px;background:green;}
  .item {background:#111827;margin-top:10px;padding:10px;border-radius:10px;}
  </style>
  </head>

  <body>

  <div class="box">
    <h2>DEFANS PRO</h2>

    <textarea id="metin"></textarea>
    <button onclick="analiz()">Analiz</button>

    <div id="sonuc"></div>
    <div class="bar" id="bar"></div>

    <h3>Sosyal Medya</h3>
    <div id="feed"></div>

    <h3>Geçmiş Analizler</h3>
    <div id="history"></div>
  </div>

  <script>
  function analiz(){
    fetch('/analiz',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({metin:metin.value})
    })
    .then(r=>r.json())
    .then(d=>{
      sonuc.innerText = d.durum + " (%" + d.skor + ")";
      bar.style.width = d.skor + "%";
      loadHistory();
    });
  }

  function loadFeed(){
    fetch('/feed')
    .then(r=>r.json())
    .then(data=>{
      feed.innerHTML = data.map(x => \`
        <div class="item">
        <b>\${x.source}</b><br>
        \${x.text}<br>
        Risk: %\${x.skor} - \${x.durum}
        </div>\`).join("");
    });
  }

  function loadHistory(){
    fetch('/history')
    .then(r=>r.json())
    .then(data=>{
      history.innerHTML = data.map(x => \`
        <div class="item">
        \${x.text}<br>
        %\${x.skor} - \${x.durum}<br>
        <small>\${x.date}</small>
        </div>\`).join("");
    });
  }

  loadFeed();
  loadHistory();
  </script>

  </body>
  </html>
  `);
});

app.listen(process.env.PORT || 10000);