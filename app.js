const app=document.getElementById('app');
let html='';
let prevS='';
D.forEach((grpData,gi)=>{
const si=grpData.s;
if(si!==prevS){
if(prevS){html+='</div></div>';if(si<='6')html+='<div class="conn"></div>';}
const sl=stageLabels[si];
const cnt=D.filter(g=>g.s===si).reduce((a,g)=>a+g.cs.length,0);
html+=`<div class="stg ${sl.c}" id="stg${si}">
<div class="sh" onclick="tg('stg${si}')">
<div class="sn">${si}</div><div class="sl">${sl.n}</div><div class="st">${sl.t}</div>
<div class="badge">${cnt}</div>
<svg class="chv" viewBox="0 0 16 16"><path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
</div><div class="sb" id="sb-stg${si}">`;
prevS=si;
}
if(grpData.g)html+=`<div class="grp"><div class="gl">${grpData.g}</div>`;
else html+=`<div class="grp">`;
grpData.cs.forEach((co,ci)=>{
const id=`c${gi}_${ci}`;
const certs=co.c&&co.c.length?co.c.map(c=>`<span class="tag">${c}</span>`).join(''):'';
const loc=co.l?` (${co.l})`:'';
const web=co.w?`<a class="lnk" href="${co.w.startsWith('http')?co.w:'https://'+co.w}" target="_blank" rel="noopener">${co.w.replace('https://','').replace('http://','')}</a>`:'';
const sec=co.x?`<div class="sec">Also operates in: ${secLabels[co.x]||co.x}</div>`:'';
html+=`<div class="co"><div class="ch" onclick="tc('${id}')">
<div class="cd"></div><div class="cn">${co.n}${loc}</div>
<svg class="cx" viewBox="0 0 16 16"><path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
</div><div class="det" id="${id}">
<div class="dd">${co.d||'No description available.'}</div>
${certs?'<div class="tags">'+certs+'</div>':''}
${web}${sec}
</div></div>`;
});
html+='</div>';
});
html+='</div></div>';
app.innerHTML=html;

function tg(id){
document.getElementById('sb-'+id).classList.toggle('o');
document.querySelector('#'+id+' .chv').classList.toggle('o');
}
function tc(id){
document.getElementById(id).classList.toggle('o');
const svg=document.querySelector(`[onclick="tc('${id}')"] .cx`);
if(svg)svg.classList.toggle('o');
}
window.tg=tg;
window.tc=tc;
