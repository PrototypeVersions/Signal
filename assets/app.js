(() => {
  'use strict';
  const state = JSON.parse(document.getElementById('signal-data').textContent);
  const { edition, prefix } = state;
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
    if($('.more-section'))$('.more-section').hidden=filter==='frontiers'||!$('.more-section .more-item');
    const lead=$('.lead-story');
    if(lead)lead.hidden=filter!=='all'&&lead.dataset.section!==filter;
    if($('.atlas'))$('.atlas').hidden=filter==='frontiers';
  }));
  $$('.navlinks a').forEach(link=>link.addEventListener('click',()=>{if(location.pathname===new URL(link.href).pathname && (link.hash==='#frontiers'||link.hash==='#ai-frontier'||link.hash==='#regions'))$('[data-filter=all]')?.click();}));
  $$('[data-mode]').forEach(button=>button.addEventListener('click',()=>{
    $$('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    document.body.classList.toggle('quick',button.dataset.mode==='quick');
  }));
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
  // Catch me up: choose how long you were away; stories are grouped by thread, biggest first.
  const VISIT_KEY='signal:lastVisit';
  const readVisit=()=>{try{return Number(localStorage.getItem(VISIT_KEY))||0;}catch{return 0;}};
  const writeVisit=()=>{try{localStorage.setItem(VISIT_KEY,String(Date.now()));}catch{}};
  const lastVisit=readVisit();
  const awayDays=lastVisit?Math.floor((Date.now()-lastVisit)/86400000):null;
  writeVisit();
  const RANGES=[1,3,7,14,30];
  let choice=awayDays==null?'7':String(RANGES.find(n=>n>=Math.max(1,awayDays))||30);
  const welcomeText=awayDays>=2?`Welcome back. You were last here ${awayDays} days ago.`:'';
  const banner=$('#welcome-back');
  if(banner&&welcomeText&&!location.pathname.includes('/editions/')){banner.hidden=false;banner.querySelector('span').textContent=welcomeText;}
  if(welcomeText){const w=$('#catchup-welcome');w.hidden=false;w.textContent=welcomeText+' Here is what changed.';}
  const dayDiff=(a,b)=>Math.round((new Date(a+'T12:00:00Z')-new Date(b+'T12:00:00Z'))/86400000);
  const WEIGHT={world:3,still:2,ai:2,frontiers:2,more:1};
  const sectionName=s=>s==='ai'||s==='frontiers'?'Frontiers':s==='more'?'More that changed':s==='still'?'Still matters':'World';
  function groupThreads(list,latestDate){
    const groups=new Map();
    list.forEach(ed=>ed.stories.forEach(s=>{
      if(!groups.has(s.h))groups.set(s.h,{h:s.h,items:[],score:0});
      const g=groups.get(s.h);g.items.push({date:ed.date,story:s});
      g.score+=(WEIGHT[s.s]||1)+(s.l?4:0)+(ed.date===latestDate?1:0);
    }));
    const w=i=>(WEIGHT[i.story.s]||1)+(i.story.l?4:0);
    groups.forEach(g=>g.items.sort((a,b)=>a.date===b.date?w(a)-w(b):(a.date<b.date?-1:1)));
    return [...groups.values()].sort((a,b)=>b.score-a.score||(b.items.at(-1).date>a.items.at(-1).date?1:-1));
  }
  function threadCard(g,primer){
    const last=g.items.at(-1),s=last.story,n=g.items.length;
    const earlier=g.items.slice(0,-1).reverse();
    const older=earlier.length?`<details class="cu-earlier"><summary>${earlier.length} more report${earlier.length>1?'s':''}</summary>${earlier.map(i=>`<p><small>${escape(pretty(i.date))}</small> <strong>${escape(i.story.t)}.</strong> ${escape(i.story.w)}</p>`).join('')}</details>`:'';
    const meta=primer?sectionName(s.s):`${sectionName(s.s)} · ${n} report${n>1?'s':''}`;
    const lead=primer&&s.hs?`<p class="cu-summary">${escape(s.hs)}</p>`:'';
    return `<article class="cu-thread"><span class="eyebrow">${escape(meta)}</span><h3><a href="${prefix}threads/${encodeURIComponent(g.h)}/">${escape(s.ht)} ↗</a></h3>${lead}<p class="cu-latest"><small>${escape(pretty(last.date))}</small> <a href="${prefix}stories/${encodeURIComponent(s.id)}/">${escape(s.t)}</a>. ${escape(s.u||s.w)}</p>${older}</article>`;
  }
  let dataPromise, request=0;
  async function catchup(){
    const ticket=++request,target=$('#catchup-results');
    $$('[data-days]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.days===choice)));
    target.innerHTML='<p>Gathering the stories…</p>';
    try{
      dataPromise ||= fetch(prefix+'data/catchup.json').then(r=>{if(!r.ok)throw Error('Unavailable');return r.json();});
      const data=await dataPromise;if(ticket!==request)return;
      const latestDate=data.latest;
      if(choice==='new'){
        const list=data.editions.filter(x=>dayDiff(latestDate,x.date)<14);
        const top=groupThreads(list,latestDate).slice(0,6);
        target.innerHTML='<p class="cu-intro">New here? These are the biggest stories we’re following. Each one opens a timeline of everything we’ve reported on it.</p>'+top.map(g=>threadCard(g,true)).join('');
        return;
      }
      const days=Number(choice);
      const list=data.editions.filter(x=>dayDiff(latestDate,x.date)<days);
      if(!list.length){target.innerHTML='<h3>You’re up to date.</h3><p>Nothing new has been published in that time.</p>';return;}
      const groups=groupThreads(list,latestDate),shown=groups.slice(0,10),rest=groups.slice(10);
      const young=dayDiff(latestDate,data.first)+1<days?` The Signal began on ${escape(pretty(data.first))}, so this covers everything so far.`:'';
      const intro=`<p class="cu-intro">${list.length} edition${list.length>1?'s':''} · ${groups.length} stor${groups.length>1?'ies':'y'}, biggest first.${young}</p>`;
      const more=rest.length?`<details class="cu-more"><summary>${rest.length} more stor${rest.length>1?'ies':'y'}</summary>${rest.map(g=>threadCard(g,false)).join('')}</details>`:'';
      target.innerHTML=intro+shown.map(g=>threadCard(g,false)).join('')+more;
    }catch{dataPromise=null;target.innerHTML=`<p>The catch-up view could not load. <a href="${prefix}archive/"><u>Browse the archive instead →</u></a></p>`;}
  }
  $$('[data-days]').forEach(b=>b.addEventListener('click',()=>{choice=b.dataset.days;catchup();}));

  // Regions: the numbered map markers and the chips below it select a region panel.
  const regionLinks=$$('[data-region]');
  function selectRegion(slug,reveal){
    regionLinks.forEach(link=>{
      const active=link.dataset.region===slug;
      link.classList.toggle('is-active',active);
      if(active)link.setAttribute('aria-current','true');else link.removeAttribute('aria-current');
    });
    $$('[data-panel]').forEach(panel=>panel.hidden=panel.dataset.panel!==slug);
    const panel=document.getElementById('region-panel-'+slug);
    if(reveal&&panel&&matchMedia('(max-width:760px)').matches)panel.scrollIntoView({behavior:'smooth',block:'start'});
  }
  regionLinks.forEach(link=>link.addEventListener('click',event=>{event.preventDefault();selectRegion(link.dataset.region,true);}));
  if(regionLinks.length)selectRegion(regionLinks[0].dataset.region,false);
  // Listen: each edition is read aloud as one recording with a chapter per story.
  const player=$('#player'), listenButtons=$$('[data-listen]');
  if(player&&listenButtons.length){
    const audio=player.querySelector('audio'), seek=player.querySelector('.pl-seek'), playBtn=player.querySelector('.pl-play');
    const list=player.querySelector('.pl-chapters'), listBtn=player.querySelector('.pl-list'), rateBtn=player.querySelector('.pl-rate');
    const POS_KEY='signal:listen:'+edition.date, RATE_KEY='signal:listen:rate', RATES=[1,1.15,1.3,1.5,0.9];
    const store={get:k=>{try{return localStorage.getItem(k);}catch{return null;}},set:(k,v)=>{try{localStorage.setItem(k,v);}catch{}},del:k=>{try{localStorage.removeItem(k);}catch{}}};
    const clock=s=>{s=Math.max(0,Math.floor(s||0));const h=Math.floor(s/3600),m=Math.floor(s%3600/60),r=String(s%60).padStart(2,'0');return h?`${h}:${String(m).padStart(2,'0')}:${r}`:`${m}:${r}`;};
    let manifest=null,current=-1,seeking=false,lastSave=0;
    const chapterAt=t=>{let i=0;manifest.chapters.forEach((c,j)=>{if(c.t<=t+.25)i=j;});return i;};
    function setRate(r){audio.playbackRate=r;rateBtn.textContent=(r===1?'1':String(r))+'×';store.set(RATE_KEY,String(r));}
    function showChapter(i){
      if(i===current)return;current=i;const c=manifest.chapters[i];
      player.querySelector('.pl-section').textContent=c.section;
      player.querySelector('.pl-title').textContent=c.title;
      list.querySelectorAll('button').forEach((b,j)=>b.classList.toggle('is-now',j===i));
      if('mediaSession' in navigator){try{navigator.mediaSession.metadata=new MediaMetadata({title:c.title,artist:'The Signal',album:`Edition ${manifest.number} · ${pretty(edition.date)}`,artwork:[{src:new URL(prefix+'assets/og-image.png',location.href).href,sizes:'1200x630',type:'image/png'}]});}catch{}}
    }
    function render(){
      const d=audio.duration||manifest.duration,t=audio.currentTime;
      if(!seeking)seek.value=d?Math.round(t/d*1000):0;
      seek.style.setProperty('--p',(d?t/d*100:0)+'%');
      player.querySelector('.pl-time').textContent=`${clock(t)} / ${clock(d)}`;
      showChapter(chapterAt(t));
    }
    function open(){player.hidden=false;document.body.classList.add('has-player');}
    function start(at){
      open();
      if(!audio.getAttribute('src')){audio.src=prefix+'audio/'+manifest.src;audio.preload='auto';}
      if(at!=null){if(audio.readyState>=1)audio.currentTime=at;else audio.addEventListener('loadedmetadata',()=>{audio.currentTime=at;render();},{once:true});}
      audio.play().catch(()=>{});
    }
    audio.addEventListener('play',()=>{player.classList.add('is-playing');playBtn.setAttribute('aria-label','Pause');});
    audio.addEventListener('pause',()=>{player.classList.remove('is-playing');playBtn.setAttribute('aria-label','Play');store.set(POS_KEY,String(audio.currentTime));});
    audio.addEventListener('timeupdate',()=>{render();if(Date.now()-lastSave>5000){lastSave=Date.now();store.set(POS_KEY,String(audio.currentTime));}});
    audio.addEventListener('ended',()=>{store.del(POS_KEY);player.classList.remove('is-playing');});
    audio.addEventListener('error',()=>{if(audio.getAttribute('src'))toast('The recording could not be played. Please try again later.');});
    playBtn.addEventListener('click',()=>{if(!audio.getAttribute('src'))return start(null);audio.paused?audio.play().catch(()=>{}):audio.pause();});
    player.querySelector('.pl-back').addEventListener('click',()=>{audio.currentTime=Math.max(0,audio.currentTime-15);render();});
    player.querySelector('.pl-fwd').addEventListener('click',()=>{audio.currentTime=Math.min((audio.duration||manifest.duration)-1,audio.currentTime+30);render();});
    rateBtn.addEventListener('click',()=>setRate(RATES[(RATES.indexOf(audio.playbackRate)+1)%RATES.length]||1));
    listBtn.addEventListener('click',()=>{list.hidden=!list.hidden;listBtn.setAttribute('aria-expanded',String(!list.hidden));if(!list.hidden)list.querySelector('.is-now')?.scrollIntoView({block:'nearest'});});
    player.querySelector('.pl-close').addEventListener('click',()=>{audio.pause();player.hidden=true;list.hidden=true;listBtn.setAttribute('aria-expanded','false');document.body.classList.remove('has-player');});
    seek.addEventListener('input',()=>{seeking=true;const d=audio.duration||manifest.duration;seek.style.setProperty('--p',seek.value/10+'%');player.querySelector('.pl-time').textContent=`${clock(seek.value/1000*d)} / ${clock(d)}`;});
    seek.addEventListener('change',()=>{seeking=false;const d=audio.duration||manifest.duration;if(!audio.getAttribute('src'))start(seek.value/1000*d);else audio.currentTime=seek.value/1000*d;render();});
    if('mediaSession' in navigator){
      const ms=(a,f)=>{try{navigator.mediaSession.setActionHandler(a,f);}catch{}};
      ms('play',()=>audio.play());ms('pause',()=>audio.pause());
      ms('seekbackward',()=>{audio.currentTime=Math.max(0,audio.currentTime-15);});
      ms('seekforward',()=>{audio.currentTime+=30;});
      ms('previoustrack',()=>{const i=chapterAt(audio.currentTime);const c=manifest.chapters[i];audio.currentTime=audio.currentTime-c.t>4||i===0?c.t:manifest.chapters[i-1].t;});
      ms('nexttrack',()=>{const n=manifest.chapters[chapterAt(audio.currentTime)+1];if(n)audio.currentTime=n.t;});
    }
    fetch(prefix+'audio/'+edition.date+'.json').then(r=>{if(!r.ok)throw Error('No recording');return r.json();}).then(m=>{
      manifest=m;
      const minutes=Math.max(1,Math.round(m.duration/60));
      let section='';
      list.innerHTML=m.chapters.map((c,i)=>{const head=c.section!==section&&c.id!=='intro'&&c.id!=='watch'?`<li class="pl-head">${escape(c.section)}</li>`:'';section=c.section;return `${head}<li><button data-t="${c.t}"><span>${escape(c.title)}</span><time>${clock(c.t)}</time></button></li>`;}).join('');
      list.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{const at=Number(b.dataset.t);if(!audio.getAttribute('src'))start(at);else{audio.currentTime=at;audio.play().catch(()=>{});}render();}));
      setRate(Number(store.get(RATE_KEY))||1);
      player.querySelector('.pl-time').textContent=`0:00 / ${clock(m.duration)}`;
      showChapter(0);
      listenButtons.forEach(b=>{
        const ch=b.dataset.chapter&&m.chapters.find(c=>c.id===b.dataset.chapter);
        if(b.dataset.chapter&&!ch)return;
        b.hidden=false;
        b.querySelector('.listen-time').textContent=ch?`at ${clock(ch.t)}`:`${minutes} min`;
        b.addEventListener('click',()=>{
          if(ch)return start(ch.t);
          const saved=Number(store.get(POS_KEY));
          if(audio.getAttribute('src'))return audio.paused?audio.play().catch(()=>{}):open();
          if(saved>10&&saved<m.duration-15){start(saved);toast(`Picking up where you left off, at ${clock(saved)}.`);}else start(0);
        });
      });
    }).catch(()=>{});
  }
})();
