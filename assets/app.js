(() => {
  'use strict';
  const state = JSON.parse(document.getElementById('signal-data').textContent);
  const { edition, editions, prefix } = state;
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pretty = value => new Date(value + 'T12:00:00Z').toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric',timeZone:'UTC'});
  const toast = text => { const box = $('.toast'); box.textContent=text;box.hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>box.hidden=true,3500); };
  let lastFocus;
  function openDialog(dialog) { lastFocus=document.activeElement; dialog.showModal(); dialog.scrollTop=0; dialog.querySelector('.close').focus(); }
  $$('dialog').forEach(dialog => {
    dialog.querySelector('.close').addEventListener('click',()=>dialog.close());
    dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
    dialog.addEventListener('close',()=>lastFocus?.focus());
  });
  $$('[data-dialog]').forEach(button=>button.addEventListener('click',()=>{openDialog(document.getElementById(button.dataset.dialog)); if(button.dataset.dialog==='catchup-dialog')catchup();}));
  $$('[data-story]').forEach(button=>button.addEventListener('click',()=>{
    const story=edition.stories.find(s=>s.id===button.dataset.story);
    $('#story-dialog-content').innerHTML=`<div class="eyebrow">${escape(story.region)} / ${escape(story.category)}</div><h2 id="story-dialog-title">${escape(story.title)}</h2><p class="source-note">Event: ${escape(story.eventDate)} · Edition ${escape(edition.date)}</p><p>${escape(story.body)}</p><h3>What changed</h3><p>${escape(story.whatChanged)}</p><h3>Why it matters <small style="font:10px var(--mono)">/ Our assessment</small></h3><p>${escape(story.whyMatters)}</p><h3>What remains uncertain</h3><p>${escape(story.uncertainty)}</p><h3>Watch next</h3><p>${escape(story.watchNext)}</p><h3>Sources & evidence</h3>${story.sources.map(s=>`<div class="evidence"><a href="${escape(s.url)}" target="_blank" rel="noopener noreferrer">${escape(s.title)} ↗</a><small>${escape(s.publisher)} · ${escape(s.publishedAt)} · ${escape(s.kind)}</small></div>`).join('')}<div class="dialog-actions"><a class="button" href="${prefix}stories/${story.id}/">Follow this story →</a><a class="textlink" href="https://github.com/PrototypeVersions/Signal/issues/new?title=${encodeURIComponent('Correction: '+story.title)}" target="_blank" rel="noopener noreferrer">Suggest a correction ↗</a></div>`;
    openDialog($('#story-dialog'));
  }));
  $$('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
    $$('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    const filter=button.dataset.filter;
    $('.world-grid').hidden=filter==='ai';
    $('#ai-frontier').hidden=filter==='world';
  }));
  $$('.navlinks a').forEach(link=>link.addEventListener('click',()=>{if(location.pathname===new URL(link.href).pathname && link.hash==='#ai-frontier')$('[data-filter=all]')?.click();}));
  $$('[data-mode]').forEach(button=>button.addEventListener('click',()=>{
    $$('.navlinks a').forEach(link=>link.addEventListener('click',()=>{if(location.pathname===new URL(link.href).pathname && link.hash==='#ai-frontier')$('[data-filter=all]')?.click();}));
  $$('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    document.body.classList.toggle('quick',button.dataset.mode==='quick');
  }));
  try {document.body.classList.toggle('dark',localStorage.getItem('signal-theme')==='dark');}catch{}
  $('.theme').addEventListener('click',()=>{const dark=document.body.classList.toggle('dark');try{localStorage.setItem('signal-theme',dark?'dark':'light');}catch{}drawGlobe();});
  $('#share-edition')?.addEventListener('click',async()=>{
    const url=new URL(`${prefix}editions/${edition.date}/`,location.href).href;
    try {await navigator.clipboard.writeText(url);toast('Edition link copied.');}
    catch {toast('Copy this edition’s link from your address bar.');}
  });
  const progress=()=>{const max=document.documentElement.scrollHeight-innerHeight;$('.progress').style.width=(max>0?Math.min(100,scrollY/max*100):0)+'%';};
  addEventListener('scroll',progress,{passive:true});addEventListener('resize',progress);progress();
  const note=$('#stale-note');
  if(note && !location.pathname.includes('/editions/')){
    const age=Date.now()-new Date(edition.cutoff).getTime();
    if(age>40*3600000){note.hidden=false;note.textContent=`The latest published edition is ${pretty(edition.date)}. This page is an edition, not a live news feed.`;}
  }
  let historyPromise;
  let request=0;
  async function catchup(){
    const ticket=++request;const selected=$('#since-date').value;const target=$('#catchup-results');
    target.innerHTML='<p>Gathering the thread…</p>';
    try{
      historyPromise ||= fetch(prefix+'data/history.json').then(r=>{if(!r.ok)throw Error('Unavailable');return r.json();});
      const history=await historyPromise;if(ticket!==request)return;
      const pending=history.filter(x=>selected==='all'||x.date>selected);
      if(!pending.length){target.innerHTML='<h3>You’re up to date.</h3><p>There are no published editions after the one you selected. Come back for the next edition.</p>';return;}
      const grouped=new Map();
      pending.forEach(x=>x.stories.forEach(s=>{if(!grouped.has(s.id))grouped.set(s.id,[]);grouped.get(s.id).push({date:x.date,story:s});}));
      target.innerHTML=`<p>${editions.length===1?'This is Signal’s first edition. The history begins here.':`${pending.length} edition${pending.length>1?'s':''} since your last read.`}</p>`+[...grouped.values()].map(items=>{const last=items.at(-1);return `<div class="evidence"><h3><a href="${prefix}stories/${last.story.id}/">${escape(last.story.title)} ↗</a></h3>${items.map(i=>`<small>${escape(pretty(i.date))}</small><p>${escape(i.story.whatChanged)}</p>`).join('')}</div>`;}).join('');
    }catch{historyPromise=null;target.innerHTML=`<p>The catch-up view could not load. <a href="${prefix}archive/"><u>Browse the edition archive instead →</u></a></p>`;}
  }
  $('#since-date').addEventListener('change',catchup);

  // Hand-drawn geographic silhouettes: an editorial illustration, not a data map.
  const land=[
    [[-168,70],[-145,70],[-125,60],[-110,69],[-80,74],[-53,53],[-68,44],[-81,25],[-99,18],[-112,29],[-126,49],[-151,60]],
    [[-81,12],[-68,11],[-48,-1],[-35,-10],[-47,-27],[-67,-55],[-75,-45],[-70,-18]],
    [[-54,60],[-45,59],[-20,78],[-41,84],[-62,78]],
    [[-17,36],[1,36],[12,38],[32,30],[43,12],[51,10],[39,-13],[31,-31],[18,-35],[12,-18],[4,5],[-15,12]],
    [[-10,36],[-9,44],[5,49],[9,58],[28,71],[45,69],[60,57],[92,76],[123,73],[175,60],[150,48],[139,35],[123,25],[108,5],[97,10],[81,8],[72,24],[51,27],[42,12],[33,30],[23,39]],
    [[112,-11],[129,-12],[137,-10],[154,-24],[146,-39],[130,-33],[114,-34]],
    [[47,-13],[50,-17],[47,-25],[44,-22]], [[130,31],[140,44],[146,45],[141,35]],
    [[-8,50],[-6,59],[1,58],[2,51]], [[165,-34],[176,-40],[172,-46],[166,-45]]
  ];
  function inside(lon,lat,poly){let hit=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const[a,b]=poly[i],[c,d]=poly[j];if((b>lat)!==(d>lat)&&lon<(c-a)*(lat-b)/(d-b)+a)hit=!hit;}return hit;}
  const dots=[];for(let lat=-60;lat<=80;lat+=3.1)for(let lon=-180;lon<180;lon+=3.1/Math.max(.35,Math.cos(lat*Math.PI/180)))if(land.some(p=>inside(lon,lat,p)))dots.push([lon,lat]);
  const canvas=$('#globe');let angle=-12,frame,previous=0;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  function drawGlobe(){
    if(!canvas)return;const box=canvas.getBoundingClientRect();if(!box.width)return;
    const dpr=Math.min(devicePixelRatio||1,2);canvas.width=box.width*dpr;canvas.height=box.height*dpr;
    const c=canvas.getContext('2d');c.scale(dpr,dpr);const w=box.width,h=box.height,r=Math.min(w*.33,h*.41),cx=w*.51,cy=h*.49;
    const dark=document.body.classList.contains('dark'),ink=dark?'#e8e7db':'#242a2a',fine=dark?'#555d58':'#b3b6a9';
    c.strokeStyle=fine;c.lineWidth=.65;c.beginPath();c.ellipse(cx,cy,r*1.34,r*.40,-.43,0,Math.PI*2);c.stroke();
    c.fillStyle=dark?'#252a2c':'#e9e9dc';c.beginPath();c.arc(cx,cy,r,0,Math.PI*2);c.fill();c.strokeStyle=fine;c.stroke();
    const project=(lon,lat)=>{const a=(lon+angle)*Math.PI/180,b=lat*Math.PI/180;return[cx+r*Math.cos(b)*Math.sin(a),cy-r*Math.sin(b),Math.cos(b)*Math.cos(a)];};
    c.save();c.beginPath();c.arc(cx,cy,r,0,Math.PI*2);c.clip();
    c.globalAlpha=.5;c.strokeStyle=fine;c.lineWidth=.6;
    for(let lat=-60;lat<=60;lat+=30){c.beginPath();let started=false;for(let lon=-180;lon<=180;lon+=2){let[x,y,z]=project(lon,lat);if(z>0){started?c.lineTo(x,y):c.moveTo(x,y);started=true;}else started=false;}c.stroke();}
    for(let lon=-180;lon<180;lon+=30){c.beginPath();let started=false;for(let lat=-90;lat<=90;lat+=2){let[x,y,z]=project(lon,lat);if(z>0){started?c.lineTo(x,y):c.moveTo(x,y);started=true;}else started=false;}c.stroke();}
    c.globalAlpha=1;dots.forEach(([lon,lat])=>{const[x,y,z]=project(lon,lat);if(z>0){c.globalAlpha=.45+.55*z;c.fillStyle=ink;c.beginPath();c.arc(x,y,1.05+.25*z,0,Math.PI*2);c.fill();}});c.restore();
    c.strokeStyle='#c4bb16';c.lineWidth=1.15;c.beginPath();c.ellipse(cx,cy,r*1.34,r*.40,-.43,0,Math.PI);c.stroke();
    const orbit=-.73,ox=cx+r*1.27*Math.cos(orbit),oy=cy+r*.7*Math.sin(orbit);c.fillStyle='#f4ed46';c.beginPath();c.arc(ox,oy,9,0,Math.PI*2);c.fill();c.strokeStyle=ink;c.lineWidth=1;c.stroke();c.fillStyle=ink;c.beginPath();c.arc(ox,oy,2,0,Math.PI*2);c.fill();
    c.strokeStyle=fine;c.lineWidth=.6;[[cx-r*1.43,cy],[cx+r*1.43,cy],[cx,cy-r*1.2]].forEach(([x,y])=>{c.beginPath();c.moveTo(x-4,y);c.lineTo(x+4,y);c.moveTo(x,y-4);c.lineTo(x,y+4);c.stroke();});
  }
  function animate(time){if(time-previous>65){angle+=.07;drawGlobe();previous=time;}if(!reduced.matches&&!document.hidden)frame=requestAnimationFrame(animate);}
  if(canvas){drawGlobe();if(!reduced.matches)frame=requestAnimationFrame(animate);addEventListener('resize',drawGlobe);document.addEventListener('visibilitychange',()=>{cancelAnimationFrame(frame);if(!document.hidden&&!reduced.matches)frame=requestAnimationFrame(animate);});reduced.addEventListener('change',()=>{cancelAnimationFrame(frame);drawGlobe();if(!reduced.matches)frame=requestAnimationFrame(animate);});}
})();
