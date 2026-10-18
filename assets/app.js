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
  $$('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
    $$('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    const filter=button.dataset.filter;
    $('.world-grid-section').hidden=filter==='frontiers'||!$('.world-grid-section .story-card');
    $('#frontiers').hidden=filter==='world'||!$('#frontiers .story-card');
    const lead=$('.lead-story');
    if(lead)lead.hidden=filter!=='all'&&lead.dataset.section!==filter;
    if($('.atlas'))$('.atlas').hidden=filter==='frontiers';
  }));
  $$('.navlinks a').forEach(link=>link.addEventListener('click',()=>{if(location.pathname===new URL(link.href).pathname && (link.hash==='#frontiers'||link.hash==='#ai-frontier'))$('[data-filter=all]')?.click();}));
  $$('[data-mode]').forEach(button=>button.addEventListener('click',()=>{
    $$('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    document.body.classList.toggle('quick',button.dataset.mode==='quick');
  }));
  try {document.body.classList.toggle('light',localStorage.getItem('signal-night-theme')==='light');}catch{}
  function themeLabel(){const label=document.body.classList.contains('light')?'Switch to night theme':'Switch to light theme';$('.theme').setAttribute('aria-label',label);$('.theme').title=label;}
  themeLabel();
  $('.theme').addEventListener('click',()=>{const light=document.body.classList.toggle('light');try{localStorage.setItem('signal-night-theme',light?'light':'night');}catch{}themeLabel();});
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
      target.innerHTML=`<p>${editions.length===1?'This is The Signal’s first edition. The history begins here.':`${pending.length} edition${pending.length>1?'s':''} since your last read.`}</p>`+[...grouped.values()].map(items=>{const last=items.at(-1);return `<div class="evidence"><h3><a href="${prefix}stories/${last.story.id}/">${escape(last.story.title)} ↗</a></h3>${items.map(i=>`<small>${escape(pretty(i.date))}</small><p>${escape(i.story.whatChanged)}</p>`).join('')}</div>`;}).join('');
    }catch{historyPromise=null;target.innerHTML=`<p>The catch-up view could not load. <a href="${prefix}archive/"><u>Browse the edition archive instead →</u></a></p>`;}
  }
  $('#since-date').addEventListener('change',catchup);

  // The map is an alternate, keyboard-accessible way into the same reporting.
  const pins=$$('[data-atlas-id]');
  function selectLocation(id){
    const story=edition.stories.find(s=>s.id===id);
    if(!story)return;
    pins.forEach(pin=>{
      const active=pin.dataset.atlasId===id;
      pin.classList.toggle('is-active',active);
      if(active)pin.setAttribute('aria-current','true');else pin.removeAttribute('aria-current');
    });
    $('#atlas-region').textContent=story.region;
    $('#atlas-title').textContent=story.title;
    $('#atlas-change').textContent=story.whatChanged;
    $('.atlas-read').href=prefix+'stories/'+story.id+'/';
  }
  pins.forEach(pin=>pin.addEventListener('click',event=>{event.preventDefault();selectLocation(pin.dataset.atlasId);}));
  if(pins.length)selectLocation(pins[0].dataset.atlasId);
})();
