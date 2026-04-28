const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");
const OpenAI = require("openai");
const { TwitterApi } = require("twitter-api-v2");

const app = express();
app.use(cors());
app.use(express.json());

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

// 🐦 TWITTER API
app.get("/twitter", async (req, res) => {
  if (!twitterClient) {
    return res.json([{ text: "Twitter API yok" }]);
  }

  try {
    const tweets = await twitterClient.v2.search("haber", {
      max_results: 5
    });

    const data = tweets.data.data.map(t => ({
      text: t.text
    }));

    res.json(data);
  } catch {
    res.json([{ text: "Twitter veri alınamadı" }]);
  }
});

// 📊 ANALİZ
app.post("/analiz", async (req, res) => {
  const { metin, email } = req.body;

  const sonuc = await analizEt(metin);

  if (transporter && email && email.includes("@")) {
    try {
      await transporter.sendMail({
        from: process.env.EMAIL_USER,
        to: email,
        subject: "Analiz Sonucu",
        text: `${sonuc.sonuc} (%${sonuc.guven})`
      });
    } catch {}
  }

  res.json(sonuc);
});

// 🌐 UI (SENİN TASARIMA YAKIN)
app.get("/", (req, res) => {
  res.send(`
  <html>
  <head>
  <title>DEFANS PRO</title>
  <style>
  body {
    background:#0b1220;
    color:white;
    font-family:sans-serif;
    text-align:center;
  }
  .box {
    width:500px;
    margin:auto;
    margin-top:50px;
    background:#111827;
    padding:20px;
    border-radius:15px;
  }
  textarea,input {
    width:100%;
    margin-top:10px;
    padding:10px;
    border-radius:8px;
  }
  button {
    margin-top:15px;
    width:100%;
    padding:12px;
    background:linear-gradient(90deg,#4f46e5,#9333ea);
    border:none;
    color:white;
  }
  .bar {
    height:20px;
    background:green;
    margin-top:10px;
  }
  </style>
  </head>

  <body>

  <div class="box">
    <h2>DEFANS PRO</h2>

    <textarea id="metin"></textarea>
    <input id="email" placeholder="email">

    <button onclick="analiz()">Analiz Başlat</button>

    <div id="sonuc"></div>
    <div class="bar" id="bar"></div>

    <div id="twitter"></div>
  </div>

  <script>
  function analiz(){
    fetch('/analiz',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        metin:metin.value,
        email:email.value
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
    twitter.innerText =
      "Twitter: " + d.map(x=>x.text).join(" | ");
  });
  </script>

  </body>
  </html>
  `);
});

app.listen(process.env.PORT || 10000);