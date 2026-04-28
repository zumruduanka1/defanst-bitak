const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");
const OpenAI = require("openai");

const app = express();
app.use(cors());
app.use(express.json());

// 🔑 OpenAI (çökme engelli)
let openai = null;
if (process.env.OPENAI_API_KEY) {
  openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
  });
}

// 📧 Mail
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
  if (!openai) {
    return { sonuc: "AI aktif değil (API key yok)", guven: 0 };
  }

  try {
    const res = await openai.chat.completions.create({
      model: "gpt-4.1-mini",
      messages: [
        {
          role: "system",
          content: "Yalan haber analiz et ve JSON ver: {sonuc, guven}"
        },
        { role: "user", content: metin }
      ]
    });

    return JSON.parse(res.choices[0].message.content);
  } catch (e) {
    return { sonuc: "Analiz hatası", guven: 0 };
  }
}

// 📡 SOSYAL VERİ
app.get("/sosyal", (req, res) => {
  res.json([
    { kaynak: "Twitter", text: "Deprem olacak iddiası yayıldı" },
    { kaynak: "Instagram", text: "Yeni teknoloji çıktı" },
    { kaynak: "Facebook", text: "Sahte haber paylaşıldı" }
  ]);
});

// 🔗 ANALİZ API
app.post("/analiz", async (req, res) => {
  const { metin, email } = req.body;

  const sonuc = await analizEt(metin);

  // 📧 Mail gönder (varsa)
  if (transporter && email && email.includes("@")) {
    try {
      await transporter.sendMail({
        from: process.env.EMAIL_USER,
        to: email,
        subject: "Defanst Analiz Sonucu",
        text: `${sonuc.sonuc} (%${sonuc.guven})`
      });
    } catch (e) {
      console.log("Mail hatası:", e.message);
    }
  }

  res.json(sonuc);
});

// 🌐 FRONTEND
app.get("/", (req, res) => {
  res.send(`
  <html>
  <head>
    <title>Defanst</title>
    <style>
      body {
        background: linear-gradient(135deg,#0f172a,#1e293b);
        color: white;
        font-family: Arial;
        text-align: center;
      }
      .card {
        background: #1e293b;
        padding: 20px;
        margin: 40px auto;
        width: 400px;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
      }
      textarea {
        width: 100%;
        height: 100px;
        border-radius: 10px;
        margin-top:10px;
      }
      input {
        width: 100%;
        padding: 8px;
        border-radius: 8px;
        margin-top:10px;
      }
      button {
        margin-top:15px;
        padding:10px;
        width:100%;
        border:none;
        border-radius:10px;
        background:#22c55e;
        color:white;
        font-weight:bold;
      }
      .sonuc {
        margin-top:20px;
        font-size:18px;
      }
      .sosyal {
        margin-top:20px;
        font-size:14px;
        opacity:0.8;
      }
    </style>
  </head>

  <body>

  <div class="card">
    <h2>Yalan Haber Analizi</h2>

    <textarea id="metin" placeholder="Metin gir"></textarea>
    <input id="email" placeholder="Email (opsiyonel)" />

    <button onclick="analiz()">Analiz Et</button>

    <div class="sonuc" id="sonuc"></div>

    <div class="sosyal" id="sosyal"></div>
  </div>

  <script>
  function analiz(){
    fetch('/analiz',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        metin:document.getElementById('metin').value,
        email:document.getElementById('email').value
      })
    })
    .then(r=>r.json())
    .then(d=>{
      document.getElementById('sonuc').innerText =
        d.sonuc + " (%" + d.guven + ")";
    });
  }

  fetch('/sosyal')
  .then(r=>r.json())
  .then(data=>{
    document.getElementById('sosyal').innerText =
      "Kaynaklar: " + data.map(x=>x.kaynak).join(", ");
  });
  </script>

  </body>
  </html>
  `);
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log("Server çalışıyor"));