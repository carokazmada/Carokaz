document.documentElement.classList.remove('no-js');

document.addEventListener('click', (event) => {
  const toggle = event.target.closest('[data-menu-toggle]');
  if (!toggle) return;
  const menu = document.querySelector('[data-mobile-menu]');
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  menu.hidden = !open;
});

document.addEventListener('change', (event) => {
  if (!event.target.matches('[data-product-select]')) return;
  const option = event.target.selectedOptions[0];
  const form = event.target.closest('[data-product]');
  form.querySelector('[name="id"]').value = option.value;
  form.querySelector('[data-price]').textContent = option.dataset.price;
  const button = form.querySelector('[type="submit"]');
  button.disabled = option.dataset.available !== 'true';
  button.textContent = option.dataset.available === 'true' ? 'Ajouter au panier' : 'Épuisé';
});
