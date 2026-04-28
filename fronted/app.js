function analiz(){
  fetch("http://localhost:10000/analiz",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      metin:document.getElementById("metin").value
    })
  })
  .then(r=>r.json())
  .then(d=>{
    document.getElementById("sonuc").innerText =
      d.sonuc + " (%" + d.guven + ")";
    yukle();
  });
}

function yukle(){
  fetch("http://localhost:10000/analizler")
  .then(r=>r.json())
  .then(data=>{
    document.getElementById("liste").innerText =
      data.map(x=>x.sonuc + " " + x.guven).join("\n");
  });
}

yukle();