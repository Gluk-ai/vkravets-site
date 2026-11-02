(function(){
  var d=document.documentElement;
  var top=document.querySelector(".top");
  var onScroll=function(){top.classList.toggle("scrolled",scrollY>8)}; onScroll(); addEventListener("scroll",onScroll,{passive:true});
  if(!d.classList.contains("js")) return;
  var els=[].slice.call(document.querySelectorAll(".rv"));
  els.forEach(function(el){ if(el.getBoundingClientRect().top<innerHeight) el.classList.add("in"); });
  var io=new IntersectionObserver(function(es){es.forEach(function(e){ if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target);} });},{rootMargin:"0px 0px -8% 0px"});
  els.forEach(function(el){ if(!el.classList.contains("in")) io.observe(el); });
})();
(function(){
  var btn=document.querySelector(".lang-btn"), menu=document.getElementById("lang-menu");
  if(!btn||!menu) return;
  var items=[].slice.call(menu.querySelectorAll(".lang-item"));
  function open(focusFirst){ menu.hidden=false; btn.setAttribute("aria-expanded","true"); if(focusFirst) (menu.querySelector('[aria-current="true"]')||items[0]).focus(); }
  function close(refocus){ menu.hidden=true; btn.setAttribute("aria-expanded","false"); if(refocus) btn.focus(); }
  btn.addEventListener("click",function(){ menu.hidden?open(false):close(false); });
  btn.addEventListener("keydown",function(e){ if(e.key==="ArrowDown"||e.key==="Enter"||e.key===" "){ e.preventDefault(); open(true); } });
  menu.addEventListener("keydown",function(e){
    var i=items.indexOf(document.activeElement);
    if(e.key==="ArrowDown"){e.preventDefault();items[(i+1)%items.length].focus();}
    else if(e.key==="ArrowUp"){e.preventDefault();items[(i-1+items.length)%items.length].focus();}
    else if(e.key==="Escape"){e.preventDefault();close(true);}
    else if(e.key==="Tab"){close(false);}
  });
  document.addEventListener("click",function(e){ if(!menu.hidden&&!e.target.closest(".lang")) close(false); });
  // keep the reader on the same section after switching (/#skills -> /ua/#skills)
  items.forEach(function(a){ a.addEventListener("click",function(e){
    if(a.getAttribute("aria-current")==="true"){ e.preventDefault(); close(true); return; }
    if(location.hash){ e.preventDefault(); location.assign(a.getAttribute("href")+location.hash); }
  }); });
})();
