(function () {
  const modal = document.getElementById('productModal');
  if (!modal) return;

  const mImg = modal.querySelector('#mImg');
  const mName = modal.querySelector('#mName');
  const mPrice = modal.querySelector('#mPrice');
  const mCategory = modal.querySelector('#mCategory');
  const mDesc = modal.querySelector('#mDesc');

  function openModal(data) {
    mName.textContent = data.name || '';
    mPrice.textContent = data.price || '';
    mCategory.textContent = data.category ? `Categoría: ${data.category}` : '';
    mDesc.textContent = data.desc || '';

    if (data.image) {
      mImg.src = data.image;
      mImg.alt = data.name || 'Producto';
    } else {
      mImg.src = 'data:image/svg+xml;utf8,' + encodeURIComponent(
        `<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600">
          <rect width="100%" height="100%" fill="#e5e7eb"/>
          <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
                font-family="Arial" font-size="26" fill="#9ca3af">Imagen pendiente</text>
        </svg>`
      );
      mImg.alt = 'Imagen pendiente';
    }

    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  // Delegación: abrir desde cualquier botón .details-btn
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.details-btn');
    if (btn) {
      openModal({
        name: btn.dataset.name,
        price: btn.dataset.price,
        image: btn.dataset.image,
        desc: btn.dataset.desc,
        category: btn.dataset.category,
      });
    }
    if (e.target.dataset.close) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('open')) closeModal();
  });
})();
