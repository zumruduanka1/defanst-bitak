async function analyze(){
    let text = document.getElementById("text").value

    let r = await fetch("/analyze", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({text})
    })

    let d = await r.json()

    document.getElementById("result").innerText =
        "Risk: %" + d.score
}

async function load(){
    let r = await fetch("/data")
    let d = await r.json()

    let html = ""

    d.feed.forEach(x=>{
        html += `<div class="item">${x.text} (%${x.score})</div>`
    })

    document.getElementById("feed").innerHTML = html
}

setInterval(load, 4000)
load()