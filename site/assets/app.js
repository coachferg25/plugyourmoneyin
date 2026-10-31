(function(){
 var t=document.getElementById('board'); if(!t) return;
 var tb=t.tBodies[0], rows=[].slice.call(tb.rows);
 var q=document.getElementById('q'),fc=document.getElementById('fcat'),fa=document.getElementById('facc'),fp=document.getElementById('fplat'),cnt=document.getElementById('count');
 function apply(){
  var s=q.value.trim().toLowerCase(),n=0;
  rows.forEach(function(r){
   var ok=(!s||r.dataset.name.indexOf(s)>-1)&&(!fc.value||r.dataset.cat===fc.value)&&(!fa.value||r.dataset.access===fa.value);
   if(ok&&fp.value){var c=r.querySelector('td[data-col="'+fp.value+'"]');ok=c&&/yes|partial/.test(c.dataset.sort);}
   r.hidden=!ok; if(ok)n++;
  });
  cnt.textContent=n+' of '+rows.length+' shown';
 }
 [q,fc,fa,fp].forEach(function(el){el.addEventListener('input',apply);});
 var rank={yes:0,partial:1,unknown:2,no:3};
 function val(r,k){
  if(k==='name') return r.cells[0].dataset.sort;
  if(k==='access') return r.cells[4].dataset.sort;
  if(k==='date') return r.cells[6].dataset.sort;
  var i={chatgpt:1,claude:2,grok:3}[k]; return rank[r.cells[i].dataset.sort];
 }
 var dir={};
 t.tHead.addEventListener('click',function(e){
  var b=e.target.closest('button'); if(!b) return;
  var k=b.dataset.key||'name'; dir[k]=dir[k]===1?-1:1;
  rows.sort(function(a,b2){var x=val(a,k),y=val(b2,k);return (x<y?-1:x>y?1:0)*dir[k];});
  rows.forEach(function(r){tb.appendChild(r);});
  [].forEach.call(t.tHead.querySelectorAll('th'),function(th){th.removeAttribute('aria-sort');});
  b.closest('th').setAttribute('aria-sort',dir[k]===1?'ascending':'descending');
 });
 apply();
})();
