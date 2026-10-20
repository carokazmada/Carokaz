'use strict';
// Le catalogue public contient uniquement du stock confirmé.
const vehicles = [];
const $ = s => document.querySelector(s);
const number = n => new Intl.NumberFormat('fr-FR').format(n);
let category='suv', toastTimer;
function render(){
 const brand=$('#brand').value, model=$('#model').value, budget=Number($('#budget').value)||Infinity;
 const matches=vehicles.filter(v=>(!category||v.category===category)&&(!brand||v.brand===brand)&&(!model||v.model===model)&&v.price<=budget);
 $('#vehicle-grid').replaceChildren();
 $('#results-status').textContent=matches.length?`${matches.length} véhicules`:'Le catalogue en ligne est en cours de mise à jour. Contactez-nous pour connaître les véhicules disponibles.';
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
const menuToggle = $('.menu-toggle');
function setMenuOpen(open) {
 $('#navigation').classList.toggle('open', open);
 menuToggle.setAttribute('aria-expanded', String(open));
 menuToggle.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
}
menuToggle.addEventListener('click', () => setMenuOpen(menuToggle.getAttribute('aria-expanded') !== 'true'));
document.querySelectorAll('nav a').forEach(a => a.addEventListener('click', () => {
 setMenuOpen(false);
 document.querySelectorAll('nav a').forEach(b => b.classList.toggle('active', b === a));
}));
document.addEventListener('keydown', e => {
 if (e.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
  setMenuOpen(false);
  menuToggle.focus();
 }
});
$('.search-shortcut').addEventListener('click',()=>$('#brand').focus());
updateModels();render();
