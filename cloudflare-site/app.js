'use strict';
// Examples reproduce the visual reference. None represent verified stock.
const vehicles = [
  {id:'demo-audi',brand:'Audi',model:'Q8',name:'Audi Q8',year:2021,km:45000,price:98000000,category:'suv',image:0},
  {id:'demo-toyota',brand:'Toyota',model:'Fortuner Legender',name:'Fortuner Legender',year:2022,km:32000,price:98000000,category:'suv',image:1},
  {id:'demo-mercedes',brand:'Mercedes',model:'GLA 200',name:'Mercedes GLA 200',year:2021,km:28000,price:98000000,category:'suv',image:2},
  {id:'demo-volkswagen',brand:'Volkswagen',model:'Touareg',name:'VW Touareg',year:2020,km:60000,price:98000000,category:'suv',image:3}
];
const $ = s => document.querySelector(s);
const number = n => new Intl.NumberFormat('fr-FR').format(n);
let category='suv', toastTimer;
let favorites = new Set();
try {const saved=JSON.parse(localStorage.getItem('carokaz-demo-favorites')||'[]');if(Array.isArray(saved))favorites=new Set(saved.filter(id=>vehicles.some(v=>v.id===id)));}catch{}
const heart='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/></svg>';
function render(){
 const brand=$('#brand').value, model=$('#model').value, budget=Number($('#budget').value)||Infinity;
 const matches=vehicles.filter(v=>(!category||v.category===category)&&(!brand||v.brand===brand)&&(!model||v.model===model)&&v.price<=budget);
 $('#vehicle-grid').innerHTML=matches.map(v=>`<article class="vehicle-card"><div class="car-image car-${v.image}" role="img" aria-label="Illustration de démonstration : ${v.name}"></div><button class="favorite" data-favorite="${v.id}" aria-label="Favori : ${v.name}" aria-pressed="${favorites.has(v.id)}">${heart}</button><div class="card-content"><h3>${v.name}</h3><p>Exemple de présentation · stock à confirmer</p><div class="card-bottom"><span class="price">Prix à confirmer</span><button class="detail-button" data-detail="${v.id}" aria-label="Voir la fiche de démonstration ${v.name}">→</button></div></div></article>`).join('');
 $('#results-status').textContent=matches.length?`${matches.length} modèles de démonstration · Prix et kilométrages repris de la maquette, non confirmés.`:'Aucun exemple ne correspond à ces filtres. Le stock réel reste à confirmer.';
 $('#reset').hidden=matches.length>0;
}
function updateModels(){const models=vehicles.filter(v=>!$('#brand').value||v.brand===$('#brand').value);$('#model').replaceChildren(new Option('Modèle',''),...models.map(v=>new Option(v.model,v.model)));}
function setCategory(value){category=value;document.querySelectorAll('[data-category]').forEach(b=>{const on=b.dataset.category===value;b.classList.toggle('selected',on);b.setAttribute('aria-pressed',String(on));});}
function notify(message){$('#toast').textContent=message;$('#toast').classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').classList.remove('visible'),2400);}
$('#brand').addEventListener('change',updateModels);
$('#search-form').addEventListener('submit',e=>{e.preventDefault();render();$('#vehicules').scrollIntoView({behavior:'smooth'});});
document.querySelectorAll('[data-category]').forEach(b=>b.addEventListener('click',()=>{setCategory(b.dataset.category);render();$('#vehicules').scrollIntoView({behavior:'smooth'});}));
function reset(){ $('#search-form').reset();updateModels();setCategory('');render();}
$('#show-all').addEventListener('click',reset);$('#reset').addEventListener('click',reset);
$('#vehicle-grid').addEventListener('click',e=>{
 const fav=e.target.closest('[data-favorite]');if(fav){const id=fav.dataset.favorite;favorites.has(id)?favorites.delete(id):favorites.add(id);try{localStorage.setItem('carokaz-demo-favorites',JSON.stringify([...favorites]));}catch{}fav.setAttribute('aria-pressed',String(favorites.has(id)));notify(favorites.has(id)?'Ajouté à vos favoris sur cet appareil.':'Retiré de vos favoris.');return;}
 const detail=e.target.closest('[data-detail]');if(!detail)return;const v=vehicles.find(v=>v.id===detail.dataset.detail);if(!v)return;
 $('#dialog-content').innerHTML=`<div class="car-image car-${v.image}" role="img" aria-label="Illustration de démonstration ${v.name}"></div><p class="eyebrow">EXEMPLE DE PRÉSENTATION</p><h2 id="dialog-title">${v.name}</h2><p>Présentation de démonstration, sans stock certifié.</p><p class="price">Prix à confirmer</p><p>Les visuels sont illustratifs. Le prix, le kilométrage et la disponibilité de ce véhicule ne sont pas certifiés. Cette fiche présente uniquement le thème du futur site.</p><a class="button gold" href="https://www.facebook.com/carokazmada/" target="_blank" rel="noopener noreferrer">Décrire ma recherche ↗</a>`;$('#vehicle-dialog').showModal();
});
$('.close-dialog').addEventListener('click',()=>$('#vehicle-dialog').close());
$('#vehicle-dialog').addEventListener('click',e=>{if(e.target===$('#vehicle-dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
$('.menu-toggle').addEventListener('click',()=>{const open=$('#navigation').classList.toggle('open');$('.menu-toggle').setAttribute('aria-expanded',String(open));$('.menu-toggle').setAttribute('aria-label',open?'Fermer le menu':'Ouvrir le menu');});
document.querySelectorAll('nav a').forEach(a=>a.addEventListener('click',()=>{$('#navigation').classList.remove('open');$('.menu-toggle').setAttribute('aria-expanded','false');document.querySelectorAll('nav a').forEach(b=>b.classList.toggle('active',b===a));}));
$('.search-shortcut').addEventListener('click',()=>$('#brand').focus());
updateModels();render();
