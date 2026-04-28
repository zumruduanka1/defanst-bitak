const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");
const OpenAI = require("openai");
const { TwitterApi } = require("twitter-api-v2");

const app = express();
app.use(cors());
app.use(express.json());

// 🔑 ENV
const MY_EMAIL = process.env.MY_EMAIL;
const SECOND_EMAIL = process.env.SECOND_EMAIL;

// 🔑 OPENAI
let openai = null;
if (process.env.OPENAI_API_KEY) {
  openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
}

// 🐦 TWITTER
let twitterClient = null;
if (process.env.TWITTER_BEARER) {
  twitterClient = new TwitterApi(process.env.TWITTER_BEARER);
}

// 📧 MAIL
let transporter = null;
if (process.env.EMAIL_USER && process.env.EMAIL_PASS) {
  transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    }
  });
}

// 🧠 ANALİZ
async function analizEt(metin) {
  if (!openai) return { sonuc: "AI aktif değil", guven: 50 };

  try {
    const res = await openai.chat.completions.create({
      model: "gpt-4.1-mini",
      messages: [
        { role: "system", content: "Yalan haber analiz et JSON ver: {sonuc, guven}" },
        { role: "user", content: metin }
      ]
    });

    return JSON.parse(res.choices[0].message.content);
  } catch {
    return { sonuc: "Analiz hatası", guven: 0 };
  }
}

// 🐦 TWITTER
app.get("/twitter", async (req, res) => {
  try {
    if (twitterClient) {
      const tweets = await twitterClient.v2.search("gündem", {
        max_results: 5
      });

      return res.json(tweets.data.data.map(t => ({ text: t.text })));
    }
  } catch {}

  res.json([
    { text: "Gündemde yanlış bilgi yayılıyor" },
    { text: "Dezenformasyon artıyor" }
  ]);
});

// 📰 HABER
app.get("/haber", async (req, res) => {
  try {
    const data = await fetch("https://api.rss2json.com/v1/api.json?rss_url=https://www.trthaber.com/rss/tum-haberler.rss");
    const json = await data.json();

    return res.json(json.items.slice(0,5).map(x => ({ title: x.title })));
  } catch {}

  res.json([{ title: "Haber alınamadı" }]);
});

// 📊 ANALİZ + MAİL (2 SABİT MAİL)
app.post("/analiz", async (req, res) => {
  const { metin } = req.body;

  const sonuc = await analizEt(metin);

  if (transporter) {
    try {
      await transporter.sendMail({
        from: process.env.EMAIL_USER,
        to: [MY_EMAIL, SECOND_EMAIL].filter(Boolean),
        subject: "Analiz Sonucu",
        text: `${sonuc.sonuc} (%${sonuc.guven})`
      });
    } catch (e) {
      console.log("Mail hata:", e.message);
    }
  }

  res.json(sonuc);
});

// 🌐 UI
app.get("/", (req, res) => {
  res.send(`
  <html>
  <head>
  <title>DEFANS PRO</title>
  <style>
  body {background:#0b1220;color:white;font-family:sans-serif;}
  .box {width:500px;margin:auto;margin-top:50px;background:#111827;padding:20px;border-radius:15px;}
  textarea {width:100%;margin-top:10px;padding:10px;border-radius:8px;}
  button {margin-top:15px;width:100%;padding:12px;background:linear-gradient(90deg,#4f46e5,#9333ea);color:white;border:none;}
  .bar {height:20px;background:green;margin-top:10px;}
  </style>
  </head>

  <body>

  <div class="box">
    <h2>DEFANS PRO</h2>

    <textarea id="metin" placeholder="Metni gir..."></textarea>

    <button onclick="analiz()">Analiz Başlat</button>

    <div id="sonuc"></div>
    <div class="bar" id="bar"></div>

    <div id="twitter"></div>
    <div id="haber"></div>
  </div>

  <script>
  function analiz(){
    fetch('/analiz',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        metin:metin.value
      })
    })
    .then(r=>r.json())
    .then(d=>{
      sonuc.innerText = d.sonuc + " (%" + d.guven + ")";
      bar.style.width = d.guven + "%";
    });
  }

  fetch('/twitter')
  .then(r=>r.json())
  .then(d=>{
    twitter.innerText = "Twitter: " + d.map(x=>x.text).join(" | ");
  });

  fetch('/haber')
  .then(r=>r.json())
  .then(d=>{
    haber.innerText = "Haber: " + d.map(x=>x.title).join(" | ");
  });
  </script>

  </body>
  </html>
  `);
});

app.listen(process.env.PORT || 10000, () => {
  console.log("Server çalışıyor");
});