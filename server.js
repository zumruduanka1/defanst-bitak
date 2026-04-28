const express = require("express");
const cors = require("cors");
const OpenAI = require("openai");
const nodemailer = require("nodemailer");
const Parser = require("rss-parser");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static("public"));

const parser = new Parser();

// AI
let openai = null;
if (process.env.OPENAI_API_KEY) {
  openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
}

// MAIL
let transporter = null;
if (process.env.EMAIL_USER) {
  transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    }
  });
}

// 🧠 ANALİZ + DOĞRULAMA
async function analizEt(metin) {
  if (!openai) return { sonuc: "AI yok", guven: 50 };

  try {
    const res = await openai.chat.completions.create({
      model: "gpt-4.1-mini",
      messages: [
        {
          role: "system",
          content: "Metni analiz et, yalan haber mi değil mi, JSON ver: {sonuc, guven}"
        },
        { role: "user", content: metin }
      ]
    });

    return JSON.parse(res.choices[0].message.content);
  } catch {
    return { sonuc: "Analiz hatası", guven: 0 };
  }
}

// 🐦 TWITTER (NITTER SCRAPING)
app.get("/twitter", async (req, res) => {
  try {
    const feed = await parser.parseURL("https://nitter.net/twitter/rss");
    res.json(feed.items.slice(0, 5));
  } catch {
    res.json([{ title: "Twitter veri alınamadı" }]);
  }
});

// 📰 HABER (GERÇEK)
app.get("/haber", async (req, res) => {
  try {
    const feed = await parser.parseURL("https://www.trthaber.com/rss/tum-haberler.rss");
    res.json(feed.items.slice(0, 5));
  } catch {
    res.json([{ title: "Haber alınamadı" }]);
  }
});

// ANALİZ API
app.post("/analiz", async (req, res) => {
  const { metin, email } = req.body;

  const sonuc = await analizEt(metin);

  if (transporter && email) {
    try {
      await transporter.sendMail({
        from: process.env.EMAIL_USER,
        to: email,
        subject: "Analiz Sonucu",
        text: JSON.stringify(sonuc)
      });
    } catch {}
  }

  res.json(sonuc);
});

app.listen(process.env.PORT || 10000);