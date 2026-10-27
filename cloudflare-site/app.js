'use strict';
// Carokaz Mada — vitrine statique. Les modèles proviennent uniquement de
// /catalogue.json (données validées). Aucun prix n'est affiché tant qu'il
// n'est pas certifié ; chaque fiche invite à confirmer avec Carokaz Mada.
const $ = s => document.querySelector(s);
const CONTACT = 'https://www.facebook.com/carokazmada/';
let vehicles = [];
let category = 'suv';

function card(vehicle) {
  const article = document.createElement('article');
  article.className = 'vehicle-card';

  const image = document.createElement('div');
  image.className = 'car-image';
  image.setAttribute('role', 'img');
  image.setAttribute('aria-label', vehicle.marque + ' ' + vehicle.modele);

  const content = document.createElement('div');
  content.className = 'card-content';

  const title = document.createElement('h3');
  title.textContent = vehicle.marque + ' ' + vehicle.modele;

  const meta = document.createElement('p');
  const parts = [];
  if (vehicle.annee) parts.push(String(vehicle.annee));
  if (vehicle.categorie) parts.push(vehicle.categorie);
  meta.textContent = parts.join(' · ') || 'Modèle importé';

  const bottom = document.createElement('div');
  bottom.className = 'card-bottom';

  const price = document.createElement('span');
  price.className = 'price';
  price.textContent = 'Prix sur demande';

  const link = document.createElement('a');
  link.className = 'button outline';
  link.href = CONTACT;
  link.rel = 'noopener noreferrer';
  link.target = '_blank';
  link.textContent = 'Confirmer';

  bottom.append(price, link);
  content.append(title, meta, bottom);
  article.append(image, content);
  return article;
}

function render() {
  const brand = $('#brand').value;
  const model = $('#model').value;
  const minYear = Number($('#annee').value) || 0;
  const matches = vehicles.filter(v =>
    (!category || v.categorie === category) &&
    (!brand || v.marque === brand) &&
    (!model || v.modele === model) &&
    (!minYear || (v.annee && v.annee >= minYear)));

  $('#vehicle-grid').replaceChildren(...matches.map(card));
  const status = $('#results-status');
  if (matches.length) {
    status.textContent = matches.length + (matches.length > 1 ? ' modèles disponibles' : ' modèle disponible') +
      ' — prix et disponibilité à confirmer avec Carokaz Mada.';
  } else {
    status.textContent = 'Aucun modèle ne correspond à votre recherche. Contactez-nous : nous pouvons sourcer votre véhicule.';
  }
  $('#reset').hidden = !(brand || model || category || minYear);
}

function fillSelect(select, values, placeholder) {
  const current = select.value;
  const options = [new Option(placeholder, '')].concat(values.map(v => new Option(v, v)));
  select.replaceChildren(...options);
  if (values.includes(current)) select.value = current;
}

function updateModels() {
  const brand = $('#brand').value;
  const models = [...new Set(vehicles.filter(v => !brand || v.marque === brand).map(v => v.modele))].sort((a, b) => a.localeCompare(b, 'fr'));
  fillSelect($('#model'), models, 'Modèle');
}

function setCategory(value) {
  category = value;
  document.querySelectorAll('[data-category]').forEach(b => {
    const on = b.dataset.category === value;
    b.classList.toggle('selected', on);
    b.setAttribute('aria-pressed', String(on));
  });
}

function reset() {
  $('#search-form').reset();
  setCategory('');
  updateModels();
  render();
}

function setMenuOpen(open) {
  const toggle = $('.menu-toggle');
  $('#navigation').classList.toggle('open', open);
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
}

function init() {
  const brands = [...new Set(vehicles.map(v => v.marque))].sort((a, b) => a.localeCompare(b, 'fr'));
  fillSelect($('#brand'), brands, 'Marque');
  const years = [...new Set(vehicles.map(v => v.annee).filter(Boolean))].sort((a, b) => b - a);
  fillSelect($('#annee'), years.map(String), 'Année');
  updateModels();

  $('#brand').addEventListener('change', () => { updateModels(); render(); });
  $('#model').addEventListener('change', render);
  $('#annee').addEventListener('change', render);
  $('#search-form').addEventListener('submit', e => {
    e.preventDefault();
    render();
    $('#vehicules').scrollIntoView({ behavior: 'smooth' });
  });
  document.querySelectorAll('[data-category]').forEach(b => b.addEventListener('click', () => {
    setCategory(b.dataset.category === category ? '' : b.dataset.category);
    render();
    $('#vehicules').scrollIntoView({ behavior: 'smooth' });
  }));
  $('#show-all').addEventListener('click', reset);
  $('#reset').addEventListener('click', reset);

  const menuToggle = $('.menu-toggle');
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
  $('.search-shortcut').addEventListener('click', () => $('#brand').focus());
}

fetch('/catalogue.json', { headers: { Accept: 'application/json' } })
  .then(r => r.ok ? r.json() : Promise.reject(new Error('catalogue indisponible')))
  .then(data => {
    vehicles = Array.isArray(data.vehicules) ? data.vehicules : [];
    init();
    render();
  })
  .catch(() => {
    const status = $('#results-status');
    if (status) status.textContent = 'Le catalogue est momentanément indisponible. Appelez le 038 84 241 38 ou écrivez-nous sur Facebook.';
  });
