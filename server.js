const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");
require("dotenv").config();

const app = express();
app.use(cors());
app.use(express.json());

// 📊 Basit analiz (anahtar kelime tabanlı)
function analizEt(metin) {
  const negatif = ["yalan", "sahte", "uydurma", "fake"];
  let skor = 0;

  negatif.forEach(k => {
    if (metin.toLowerCase().includes(k)) skor++;
  });

  if (skor > 0) {
    return { sonuc: "Şüpheli ⚠️", guven: 60 + skor * 10 };
  } else {
    return { sonuc: "Daha güvenilir ✅", guven: 80 };
  }
}

// 📧 Mail gönderici
const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

// API
app.post("/analiz", async (req, res) => {
  const { metin, email } = req.body;

  const sonuc = analizEt(metin);

  // mail gönder
  if (email) {
    await transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: email,
      subject: "Analiz Sonucu",
      text: `Sonuç: ${sonuc.sonuc} | Güven: %${sonuc.guven}`
    });
  }

  res.json(sonuc);
});

// FRONTEND
app.get("/", (req, res) => {
  res.send(`
  <html>
  <head>
    <title>Defanst</title>
    <style>
      body { font-family: Arial; background:#0f172a; color:white; text-align:center; }
      textarea { width:300px; height:100px; }
      button { padding:10px; margin-top:10px; }
    </style>
  </head>
  <body>
    <h1>Yalan Haber Analizi</h1>

    <textarea id="metin" placeholder="Metin gir"></textarea><br>
    <input id="email" placeholder="Email (opsiyonel)"/><br>

    <button onclick="gonder()">Analiz Et</button>

    <h2 id="sonuc"></h2>

    <script>
      function gonder() {
        fetch('/analiz', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({
            metin: document.getElementById('metin').value,
            email: document.getElementById('email').value
          })
        })
        .then(r=>r.json())
        .then(d=>{
          document.getElementById('sonuc').innerText =
            d.sonuc + " (Güven: %" + d.guven + ")";
        });
      }
    </script>
  </body>
  </html>
  `);
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log("Çalışıyor:", PORT));