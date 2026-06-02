"""
marginlab.ui.report_component_js
───────────────────────────────────────────────────────────────────────────
The client-side engine for the bespoke report. Pure vanilla JS (no libs).
Builds the DOM from DATA, animates numbers counting up, draws every SVG chart
with the Web Animations API, reveals sections on scroll, and parallaxes the
hero. Returned as a string and injected by report_component.build_report_html.
"""


def build_js() -> str:
    return r"""
const $ = (t, c, h) => { const e = document.createElement(t); if(c) e.className=c; if(h!=null) e.innerHTML=h; return e; };
const NS = 'http://www.w3.org/2000/svg';
const svg = (t, a) => { const e=document.createElementNS(NS,t); for(const k in a) e.setAttribute(k,a[k]); return e; };
const root = document.getElementById('root');
const D = DATA, M = D.meta, H = D.headline, MX = D.mix, S = D.sensitivity, IT = D.items;

/* ---------- helpers ---------- */
function moneyFmt(v){
  const s = M.symbol; const neg = v<0; v=Math.abs(v);
  const str = M.decimals ? v.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})
                         : Math.round(v).toLocaleString();
  return (neg?'−':'')+s+str;
}
function countUp(el, target, opts={}){
  const dur = opts.dur||1600, money=opts.money, pct=opts.pct, sign=opts.sign;
  const start = performance.now(); const from = 0;
  function tick(now){
    let p = Math.min(1,(now-start)/dur);
    p = 1-Math.pow(1-p,4); // easeOutQuart
    const val = from+(target-from)*p;
    let out;
    if(money) out = (sign&&target>=0?'+':'')+moneyFmt(val);
    else if(pct) out = (sign&&target>=0?'+':'')+val.toFixed(1)+'%';
    else out = Math.round(val).toLocaleString();
    el.textContent = out;
    if(p<1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

/* ---------- reveal + parallax ---------- */
const io = new IntersectionObserver((es)=>{
  es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in');
    if(e.target.dataset.anim) ANIM[e.target.dataset.anim] && ANIM[e.target.dataset.anim](e.target);
    io.unobserve(e.target);} });
},{threshold:.18});
function watch(el){ io.observe(el); return el; }
const ANIM = {};

/* ===================================================================
   HERO
=================================================================== */
(function(){
  const hero = $('section','hero');
  const orbit = $('div','hero-orbit');
  [340,520,720].forEach((d,i)=>{ const s=$('span'); 
    s.style.width=s.style.height=d+'px'; s.style.left='50%'; s.style.top='42%';
    s.style.marginLeft=(-d/2)+'px'; s.style.marginTop=(-d/2)+'px';
    s.dataset.depth=(i+1)*6; orbit.appendChild(s); });
  hero.appendChild(orbit);
  hero.appendChild($('div','eyebrow reveal', 'MarginLab · Pricing Analysis'));
  const sub = M.concept||M.location ? [M.concept,M.location].filter(Boolean).join(' · ') : 'Menu profit engineering';
  const h1 = $('h1','reveal d1'); h1.innerHTML = `${esc(M.cafe)}:<br>a menu <em>profit rebalance</em>.`;
  hero.appendChild(h1);
  hero.appendChild($('p','sub reveal d2', esc(sub)));
  const meta = $('div','meta reveal d3');
  meta.appendChild($('div','m',`Items reviewed<b>${M.n_items}</b>`));
  meta.appendChild($('div','m',`Confidence<b>${H.confidence}</b>`));
  meta.appendChild($('div','m',`Changing<b>${H.changes_count}</b>`));
  hero.appendChild(meta);
  const cue=$('div','scroll-cue reveal d4'); cue.appendChild($('div','line')); hero.appendChild(cue);
  root.appendChild(hero);
  requestAnimationFrame(()=>hero.querySelectorAll('.reveal').forEach(r=>r.classList.add('in')));
  // parallax
  window.addEventListener('scroll',()=>{ const y=window.scrollY;
    orbit.querySelectorAll('span').forEach(s=>{ s.style.transform=`translateY(${y/ s.dataset.depth}px)`;});
    if(y<700) hero.style.opacity = Math.max(0,1-y/620);
  },{passive:true});
})();

/* ===================================================================
   THE NUMBER
=================================================================== */
(function(){
  const w=$('section','bignum reveal'); w.dataset.anim='bignum';
  w.appendChild($('div','k','Projected monthly change in profit'));
  const v=$('div','v','0'); v.id='bignum-v'; w.appendChild(v);
  w.appendChild($('div','u',`${M.currency} per month · <b>${(H.lift_pct>=0?'+':'')+H.lift_pct}% on profit</b> · indicative annual <b>${H.monthly_lift_signed}${H.annual_fmt}</b>`));
  root.appendChild(watch(w));
  ANIM.bignum=()=>countUp(document.getElementById('bignum-v'), H.monthly_lift,{money:1,sign:1,dur:2000});
})();

/* ===================================================================
   KPI STRIP
=================================================================== */
(function(){
  secHead('01','The opportunity','Projected monthly impact');
  const g=$('div','kpis reveal'); g.dataset.anim='kpis';
  const cells=[
    {hero:1,k:'Δ profit / month',v:H.monthly_lift,money:1,sign:1,s:`${(H.lift_pct>=0?'+':'')+H.lift_pct}% on current profit`},
    {k:'Baseline profit',v:H.baseline,money:1,s:'from current menu'},
    {k:'Projected profit',v:H.projected,money:1,s:'after rebalance'},
    {k:'Confidence',txt:H.confidence,s:({HIGH:'data-backed',MEDIUM:'pilot first',LOW:'directional'})[H.confidence]},
  ];
  cells.forEach((c,i)=>{
    const cell=$('div','kpi'+(c.hero?' hero-kpi':''));
    cell.appendChild($('div','k',c.k));
    const v=$('div','v'+(c.hero?' it':'')); v.id='kpi-'+i; v.textContent=c.txt||'0'; cell.appendChild(v);
    cell.appendChild($('div','s',c.s));
    g.appendChild(cell);
    if(!c.txt) c._el=()=>countUp(document.getElementById('kpi-'+i),c.v,{money:c.money,sign:c.sign});
  });
  root.appendChild(watch(g));
  ANIM.kpis=()=>cells.forEach(c=>c._el&&c._el());
})();

/* ===================================================================
   MENU ENGINEERING — animated quadrant
=================================================================== */
(function(){
  secHead('02','Menu engineering','Popularity × margin · bubble = monthly profit');
  const box=$('div','chart reveal'); box.dataset.anim='quad';
  const W=900,Hh=440,pad=54;
  const s=svg('svg',{viewBox:`0 0 ${W} ${Hh}`}); box.appendChild(s);
  const maxU=Math.max(...IT.map(i=>i.monthly_units))*1.12;
  const maxM=Math.max(...IT.map(i=>i.margin_pct))*1.15;
  const X=u=>pad+(u/maxU)*(W-pad*2);
  const Y=m=>Hh-pad-(m/maxM)*(Hh-pad*2);
  // grid
  s.appendChild(svg('line',{x1:pad,y1:Hh-pad,x2:W-pad,y2:Hh-pad,class:'svg-axis'}));
  s.appendChild(svg('line',{x1:pad,y1:pad,x2:pad,y2:Hh-pad,class:'svg-axis'}));
  // median dividers (drawn in)
  const mu=X(D.engineering.med_units), mm=Y(D.engineering.med_margin_pct);
  const dv=svg('line',{x1:mu,y1:pad,x2:mu,y2:Hh-pad,class:'svg-grid','stroke-dasharray':'4 5'});
  const dh=svg('line',{x1:pad,y1:mm,x2:W-pad,y2:mm,class:'svg-grid','stroke-dasharray':'4 5'});
  s.appendChild(dv); s.appendChild(dh);
  // axis labels
  const xl=svg('text',{x:W-pad,y:Hh-pad+24,'text-anchor':'end',class:'svg-lab'}); xl.textContent='MONTHLY UNITS →'; s.appendChild(xl);
  const yl=svg('text',{x:pad-8,y:pad-14,'text-anchor':'start',class:'svg-lab'}); yl.textContent='MARGIN % ↑'; s.appendChild(yl);
  const QCOL={Star:'#4F6B52',Plowhorse:'#B8935C',Puzzle:'#2A2E38',Dog:'#A04A3C'};
  const maxP=Math.max(...IT.map(i=>i.base_profit));
  const bubbles=[];
  IT.forEach(it=>{
    const r=14+(it.base_profit/maxP)*40;
    const cx=X(it.monthly_units), cy=Y(it.margin_pct);
    const c=svg('circle',{cx,cy,r:0,fill:QCOL[it.quadrant]||'#6B7280','fill-opacity':.82,
      stroke:'#FBF9F5','stroke-width':2});
    s.appendChild(c);
    const t=svg('text',{x:cx,y:cy-r-7,'text-anchor':'middle',class:'svg-nm',opacity:0}); t.textContent=it.name;
    s.appendChild(t);
    bubbles.push({c,t,r});
  });
  root.appendChild(watch(box));
  // legend
  const lg=$('div','legend');
  [['Star','#4F6B52','high vol · high margin'],['Plowhorse','#B8935C','high vol · low margin'],
   ['Puzzle','#2A2E38','low vol · high margin'],['Dog','#A04A3C','low vol · low margin']].forEach(([n,c,d])=>{
    const li=$('div','li'); const dot=$('span','dot'); dot.style.background=c; li.appendChild(dot);
    li.appendChild(document.createTextNode(n)); lg.appendChild(li);
  });
  box.appendChild(lg);
  ANIM.quad=()=>{
    [dv,dh].forEach(l=>{ const len=l.getTotalLength(); l.style.strokeDasharray=len; l.style.strokeDashoffset=len;
      l.animate([{strokeDashoffset:len},{strokeDashoffset:0}],{duration:900,easing:'cubic-bezier(.19,1,.22,1)',fill:'forwards'});});
    bubbles.forEach((b,i)=>{
      b.c.animate([{r:0},{r:b.r}],{duration:900,delay:120+i*90,easing:'cubic-bezier(.34,1.56,.64,1)',fill:'forwards'});
      b.t.animate([{opacity:0},{opacity:1}],{duration:500,delay:360+i*90,fill:'forwards'});
    });
  };
})();

/* ===================================================================
   WHY THESE MOVES — cards
=================================================================== */
(function(){
  secHead('03','Why these moves','The logic');
  const g=$('div','cards');
  const cards=[
    ['It\'s a rebalance, not a hike', `<b>${MX.n_raise} up · ${MX.n_cut} down · ${MX.n_hold} held.</b> Margin shifts toward items that can carry it, while everyday favourites stay sharp to protect footfall.`],
    ['Where the gain concentrates', `Most of the lift comes from <b>${esc(H.best_item)}</b> — a strong item currently leaving margin on the table relative to its demand.`],
    ['Still inside the local market', `<b>${MX.below} below · ${MX.within} within · ${MX.above} above</b> nearby pricing. Moves keep you in a believable range, not out ahead of your street.`],
    ['Built to be reversible', `Roll out the top three first, watch for two weeks, revert anything that slips. Nothing here is a one-way door.`],
  ];
  cards.forEach((c,i)=>{ const card=$('div','card reveal d'+(i+1));
    card.appendChild($('div','h',c[0])); card.appendChild($('div','b',c[1]));
    g.appendChild(watch(card)); });
  root.appendChild(g);
})();

/* ===================================================================
   BEFORE → AFTER — animated bars
=================================================================== */
(function(){
  secHead('04','Before → after','Per item');
  const wrap=$('div','baf reveal'); wrap.dataset.anim='baf';
  const maxP=Math.max(...IT.map(i=>Math.max(i.price_from,i.price_to)));
  const rows=[];
  IT.forEach(it=>{
    const row=$('div','row');
    const nm=$('div','nm',`${esc(it.name)}<small>${it.quadrant} · ${esc(it.market)}</small>`);
    const track=$('div','track');
    const wNow=Math.max(3,(it.price_from/maxP)*100), wTo=Math.max(3,(it.price_to/maxP)*100);
    const act=it.action.toLowerCase();
    const bNow=$('div','bar now'); bNow.style.width='0%';
    const bTo=$('div',`bar to ${act}`); bTo.style.width='0%';
    const plNow=$('div','pl',it.price_from_fmt); plNow.style.left='0';
    const plTo=$('div','pl to',it.price_to_fmt);
    track.appendChild(bNow);track.appendChild(bTo);track.appendChild(plNow);track.appendChild(plTo);
    const dp=it.delta_pct, cls=dp>0?'up':(dp<0?'dn':'fl');
    const delta=$('div','delta',`<div class="p ${cls}">${dp>0?'+':''}${dp}%</div><div class="pf">${it.delta_profit_mo>=0?'+':''}${it.delta_profit_fmt}/mo</div>`);
    row.appendChild(nm);row.appendChild(track);row.appendChild(delta);
    wrap.appendChild(row);
    rows.push({bNow,bTo,plNow,plTo,wNow,wTo});
  });
  root.appendChild(watch(wrap));
  ANIM.baf=()=>rows.forEach((r,i)=>{
    r.bNow.animate([{width:'0%'},{width:r.wNow+'%'}],{duration:1000,delay:i*70,easing:'cubic-bezier(.19,1,.22,1)',fill:'forwards'});
    r.bTo.animate([{width:'0%'},{width:r.wTo+'%'}],{duration:1000,delay:140+i*70,easing:'cubic-bezier(.19,1,.22,1)',fill:'forwards'});
    setTimeout(()=>{r.plNow.style.left=`calc(${r.wNow}% + 8px)`;r.plTo.style.left=`calc(${r.wTo}% + 8px)`;
      r.plNow.style.transition=r.plTo.style.transition='left 1s cubic-bezier(.19,1,.22,1)';},i*70);
  });
})();

/* ===================================================================
   PROFIT CONTRIBUTION — waterfall drawing in
=================================================================== */
(function(){
  const movers=IT.filter(i=>Math.abs(i.delta_profit_mo)>0.01).sort((a,b)=>b.delta_profit_mo-a.delta_profit_mo);
  if(!movers.length) return;
  secHead('05','Profit bridge','How the lift builds, item by item');
  const box=$('div','chart reveal'); box.dataset.anim='wf';
  const W=900,Hh=380,pad=46,bw=Math.min(70,(W-pad*2)/(movers.length+1)-14);
  const s=svg('svg',{viewBox:`0 0 ${W} ${Hh}`}); box.appendChild(s);
  const total=movers.reduce((a,b)=>a+b.delta_profit_mo,0);
  const maxCum=Math.max(total,...cum(movers))*1.15||1;
  function cum(arr){let c=0;return arr.map(x=>(c+=x.delta_profit_mo));}
  const Y=v=>Hh-pad-(v/maxCum)*(Hh-pad*2);
  const zeroY=Y(0);
  s.appendChild(svg('line',{x1:pad,y1:zeroY,x2:W-pad,y2:zeroY,class:'svg-axis'}));
  let cumv=0; const bars=[];
  movers.forEach((it,i)=>{
    const x=pad+i*((W-pad*2)/(movers.length+1))+8;
    const y0=Y(cumv), y1=Y(cumv+it.delta_profit_mo);
    const top=Math.min(y0,y1), h=Math.abs(y1-y0);
    const rect=svg('rect',{x,y:zeroY,width:bw,height:0,rx:3,fill:it.delta_profit_mo>=0?'#B8935C':'#A04A3C'});
    s.appendChild(rect);
    const lab=svg('text',{x:x+bw/2,y:top-8,'text-anchor':'middle',class:'svg-val',opacity:0});
    lab.textContent=(it.delta_profit_mo>=0?'+':'−')+moneyFmt(Math.abs(it.delta_profit_mo)).replace('−','');
    s.appendChild(lab);
    const nm=svg('text',{x:x+bw/2,y:Hh-pad+18,'text-anchor':'middle',class:'svg-lab'});
    nm.textContent=it.name.length>9?it.name.slice(0,9)+'…':it.name; s.appendChild(nm);
    bars.push({rect,lab,top,h,y1});
    cumv+=it.delta_profit_mo;
  });
  // total bar
  const xt=pad+movers.length*((W-pad*2)/(movers.length+1))+8;
  const yt=Y(total);
  const rt=svg('rect',{x:xt,y:zeroY,width:bw,height:0,rx:3,fill:'#13151A'}); s.appendChild(rt);
  const ltot=svg('text',{x:xt+bw/2,y:yt-8,'text-anchor':'middle',class:'svg-val',opacity:0,'font-weight':600});
  ltot.textContent='+'+moneyFmt(Math.abs(total)).replace('−',''); s.appendChild(ltot);
  const ntot=svg('text',{x:xt+bw/2,y:Hh-pad+18,'text-anchor':'middle',class:'svg-lab'}); ntot.textContent='Net / mo'; s.appendChild(ntot);
  root.appendChild(watch(box));
  ANIM.wf=()=>{
    bars.forEach((b,i)=>{ b.rect.animate([{y:zeroY,height:0},{y:b.top,height:b.h}],
      {duration:760,delay:i*120,easing:'cubic-bezier(.19,1,.22,1)',fill:'forwards'});
      b.lab.animate([{opacity:0},{opacity:1}],{duration:400,delay:i*120+500,fill:'forwards'});});
    const d=bars.length*120;
    rt.animate([{y:zeroY,height:0},{y:Math.min(zeroY,yt),height:Math.abs(zeroY-yt)}],
      {duration:900,delay:d,easing:'cubic-bezier(.34,1.56,.64,1)',fill:'forwards'});
    ltot.animate([{opacity:0},{opacity:1}],{duration:500,delay:d+600,fill:'forwards'});
  };
})();

/* ===================================================================
   CONFIDENCE RANGE — line + dots slide in
=================================================================== */
(function(){
  secHead('06','Confidence range','Stress test · conservative → optimistic');
  const box=$('div','chart reveal'); box.dataset.anim='sens';
  const W=900,Hh=200,pad=80;
  const s=svg('svg',{viewBox:`0 0 ${W} ${Hh}`}); box.appendChild(s);
  const pts=[['Conservative',S.conservative],['Baseline',S.baseline],['Optimistic',S.optimistic]];
  const xs=pts.map(p=>p[1]); const lo=Math.min(...xs),hi=Math.max(...xs),span=(hi-lo)||1;
  const X=v=>pad+((v-lo)/span)*(W-pad*2);
  const midY=Hh/2;
  const line=svg('line',{x1:X(lo),y1:midY,x2:X(lo),y2:midY,stroke:'#E8D9BE','stroke-width':3,'stroke-linecap':'round'});
  s.appendChild(line);
  const dots=[];
  pts.forEach(([lab,val])=>{
    const big=lab==='Baseline'; const x=X(val);
    const dot=svg('circle',{cx:x,cy:midY,r:0,fill:big?'#13151A':'#B8935C',stroke:'#FBF9F5','stroke-width':2});
    s.appendChild(dot);
    const t1=svg('text',{x,y:big?midY-26:midY+34,'text-anchor':'middle',class:'svg-lab',opacity:0}); t1.textContent=lab.toUpperCase();
    const t2=svg('text',{x,y:big?midY-44:midY+52,'text-anchor':'middle',class:'svg-nm',opacity:0});
    t2.textContent=(val>=0?'+':'−')+moneyFmt(Math.abs(val)).replace('−','');
    s.appendChild(t1);s.appendChild(t2);
    dots.push({dot,t1,t2,x,r:big?11:7});
  });
  root.appendChild(watch(box));
  const note=$('div','card reveal d1'); note.style.marginTop='18px';note.style.borderLeftColor=S.robust==='Yes'?'#4F6B52':'#A04A3C';
  note.appendChild($('div','h',`Robust across scenarios? ${S.robust}`));
  note.appendChild($('div','b',`The recommendation ${S.robust==='Yes'?'<b>remains positive</b> across all three scenarios':'<b>is not positive</b> in every scenario — review before rollout'}. Conservative assumes customers are 20% more price-sensitive than estimated; optimistic, 20% less.`));
  root.appendChild(watch(note));
  ANIM.sens=()=>{
    line.animate([{x2:X(lo)},{x2:X(hi)}],{duration:900,easing:'cubic-bezier(.19,1,.22,1)',fill:'forwards'});
    dots.forEach((d,i)=>{ d.dot.animate([{r:0},{r:d.r}],{duration:600,delay:300+i*150,easing:'cubic-bezier(.34,1.56,.64,1)',fill:'forwards'});
      d.t1.animate([{opacity:0},{opacity:1}],{duration:400,delay:500+i*150,fill:'forwards'});
      d.t2.animate([{opacity:0},{opacity:1}],{duration:400,delay:560+i*150,fill:'forwards'});});
  };
})();

/* ===================================================================
   LIMITATIONS
=================================================================== */
(function(){
  secHead('07','What this can\'t see','The reason to walk through it together');
  const box=$('div','lims reveal'); box.dataset.anim='';
  const lims=[
    ['Switching between your own items','when one drink moves, some customers shift to another. Each item is priced on its own.'],
    ['The basket effect','a coffee price change can move pastry attach-rate too; the model sees only the coffee.'],
    ['Time-of-day & weekday mix','a 7am and a 3pm order are different products, averaged into one number here.'],
  ];
  lims.forEach((l,i)=>{ const li=$('div','li');
    li.appendChild($('div','no',(i+1)));
    li.appendChild($('div','tx',`<h4>${l[0]}</h4><p>${l[1]}</p>`));
    box.appendChild(li); });
  root.appendChild(watch(box));
  const hook=$('div','hook reveal d1');
  hook.innerHTML=`These three gaps are why pricing isn't a spreadsheet. On a <b>60-minute walkthrough</b> we read this against how your café actually trades — and turn the directional numbers into a confident 30-day plan.`;
  root.appendChild(watch(hook));
  root.appendChild($('div','footer','MARGINLAB · MENU PROFIT ENGINEERING FOR INDEPENDENT CAFÉS<br>PROJECTIONS ARE ESTIMATES BASED ON THE DATA PROVIDED · ACTUAL RESULTS VARY · CHANGES IMPLEMENTED GRADUALLY AND MONITORED'));
})();

/* ---------- section heading helper ---------- */
function secHead(n,title,right){
  const sec=$('div','sec reveal');
  sec.appendChild($('div','n',n));
  sec.appendChild($('h2',null,title));
  sec.appendChild($('div','r',right||''));
  root.appendChild(watch(sec));
}
function esc(s){ return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

/* report height -> parent (for iframe autosize) */
function postH(){ const h=document.body.scrollHeight; window.parent.postMessage({type:'ml-report-height',height:h},'*'); }
new ResizeObserver(postH).observe(document.body);
setTimeout(postH,400); setTimeout(postH,1500);
"""
