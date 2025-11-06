(function () {
  "use strict";

  // Evitar doble inicialización si el script se carga 2 veces
  if (window.__TX_INIT__) return;
  window.__TX_INIT__ = true;

  // ==== Utils (seguros de colisión) ====
  const MXN = new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" });

  // Si ya existe $, $$ (por ejemplo por otra lib), los reutilizo; si no, los creo locales.
  const $  = window.$  || ((s, c = document) => c.querySelector(s));
  const $$ = window.$$ || ((s, c = document) => Array.from(c.querySelectorAll(s)));

  // ==== Placeholder img (no usa /static/) ====
  const PLACEHOLDER = "data:image/svg+xml;utf8," + encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="560">
      <rect width="100%" height="100%" fill="#e5e7eb"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-family="Segoe UI, Arial" font-size="22" fill="#94a3b8">Sin imagen</text>
    </svg>`
  );

  // ===============================
  // NAV: dropdowns
  // ===============================
  function initNavDropdowns() {
    const items = $$(".has-dd");
    if (!items.length) return;

    const closeAll = () => items.forEach(i => {
      i.classList.remove("open");
      i.querySelector(".dd-toggle")?.setAttribute("aria-expanded", "false");
    });

    items.forEach(item => {
      const btn = item.querySelector(".dd-toggle");
      if (!btn) return;
      btn.addEventListener("click", e => {
        e.preventDefault();
        const on = item.classList.toggle("open");
        btn.setAttribute("aria-expanded", on ? "true" : "false");
        items.filter(x => x !== item).forEach(x => {
          x.classList.remove("open");
          x.querySelector(".dd-toggle")?.setAttribute("aria-expanded", "false");
        });
      });
    });

    document.addEventListener("click", e => { if (!e.target.closest(".has-dd")) closeAll(); });
    document.addEventListener("keydown", e => { if (e.key === "Escape") closeAll(); });
  }

  // ===============================
  // Carrito (localStorage)
  // ===============================
  const CART_KEY = "cart_items_v1";
  const Cart = {
    all()  { try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch { return []; } },
    save(xs) { localStorage.setItem(CART_KEY, JSON.stringify(xs)); },
    add(it) {
      const xs = Cart.all();
      const ix = xs.findIndex(x => x.sku === it.sku && x.price === it.price);
      if (ix >= 0) { xs[ix].qty += it.qty; xs[ix].subtotal = xs[ix].qty * xs[ix].price; }
      else { xs.push({ ...it, subtotal: it.qty * it.price }); }
      Cart.save(xs); Cart.render();
    },
    remove(sku) { Cart.save(Cart.all().filter(x => x.sku !== sku)); Cart.render(); },
    clear() { Cart.save([]); Cart.render(); },
    count() { return Cart.all().reduce((a, b) => a + b.qty, 0); },
    total() { return Cart.all().reduce((a, b) => a + b.subtotal, 0); },
    render() {
      const list  = $("#cartItems"),
            badge = $("#cartBadge"),
            total = $("#cartTotal");
      if (!list || !badge || !total) return;

      const items = Cart.all();
      list.innerHTML = items.length ? "" : `<div class="cart-item"><div>No hay productos en el carrito.</div></div>`;
      items.forEach(it => {
        const row = document.createElement("div"); row.className = "cart-item";
        row.innerHTML = `
          <div>
            <div><strong>${it.name}</strong></div>
            <div class="meta">Cant: ${it.qty} · ${MXN.format(it.price)} c/u</div>
          </div>
          <div style="text-align:right">
            <div><strong>${MXN.format(it.subtotal)}</strong></div>
            <button class="remove" data-sku="${it.sku}">Quitar</button>
          </div>`;
        list.appendChild(row);
      });
      badge.textContent = Cart.count();
      total.textContent = "Total: " + MXN.format(Cart.total());
    }
  };

  document.addEventListener("click", e => {
    const btn = e.target.closest(".remove[data-sku]");
    if (btn) Cart.remove(btn.dataset.sku);
  });

  // ===============================
  // Modal de cantidad (con fallback)
  // ===============================
  function makeCartModal() {
    const root = $("#qtyModal");
    if (!root) {
      // Fallback con prompt/confirm
      return {
        open({ name, price, onOk }) {
          let qty = prompt(`¿Cuántas unidades de "${name}"?`, "1");
          if (qty === null) return;
          qty = parseInt(qty, 10);
          if (isNaN(qty) || qty <= 0) { alert("Cantidad no válida."); return; }
          const total = price * qty;
          if (confirm(
            `Unitario: ${MXN.format(price)}\n` +
            `Cantidad: ${qty}\n` +
            `Total: ${MXN.format(total)}\n\n¿Agregar al carrito?`
          )) onOk(qty);
        }
      };
    }

    const nameEl = $("#cmName"),
          unitEl = $("#cmUnit"),
          qtyEl  = $("#cmQty"),
          totalEl= $("#cmTotal"),
          okBtn  = $("#cmConfirm");

    let state = { name: "", price: 0, onOk: () => {} };

    const updateTotal = () => {
      const q = Math.max(1, parseInt(qtyEl.value || "1", 10));
      totalEl.textContent = MXN.format(state.price * q);
    };

    qtyEl?.addEventListener("input", updateTotal);
    root.addEventListener("click", e => {
      if (e.target.dataset.close) {
        root.classList.add("hidden");
        root.setAttribute("aria-hidden", "true");
      }
    });
    okBtn?.addEventListener("click", () => {
      const q = Math.max(1, parseInt(qtyEl.value || "1", 10));
      root.classList.add("hidden");
      root.setAttribute("aria-hidden", "true");
      state.onOk(q);
    });

    return {
      open({ name, price, onOk }) {
        state = { name, price, onOk };
        nameEl.textContent = name;
        unitEl.textContent = MXN.format(price);
        qtyEl.value = 1; updateTotal();
        root.classList.remove("hidden");
        root.setAttribute("aria-hidden", "false");
      }
    };
  }
  const CartModal = makeCartModal();

  // ===============================
  // Productos desde la API
  // ===============================
  let PRODUCTS = [];

  function normalizeProduct(p) {
    const name = p.name ?? p.nombre ?? "Producto";
    const price = Number(p.price ?? p.precio ?? 0);
    const description = p.description ?? p.descripcion ?? "";
    const category_name =
      p.category_name ??
      p.categoria ??
      (p.category?.name ?? p.category?.nombre ?? "") ?? "";
    const image = p.image ?? p.imagen ?? "";
    const id    = p.id;
    const slug  = p.slug || `SKU-${id}`;
    return { id, slug, name, price, description, category_name, image };
  }

  function cardHTML(p) {
    const img = p.image || PLACEHOLDER;
    const cat = p.category_name || "Producto";
    return `
      <article class="card">
        <span class="badge">${cat}</span>
        <img src="${img}" alt="${p.name}" onerror="this.onerror=null;this.src='${PLACEHOLDER}'">
        <h3>${p.name}</h3>
        <div class="price">${MXN.format(p.price)}</div>
        <p>${p.description || ""}</p>
        <div class="actions">
          <button class="btn btn-primary" data-sku="${p.slug}" data-name="${p.name}" data-price="${p.price}">Agregar</button>
          <button class="btn btn-ghost" data-det="${p.id}">Detalles</button>
        </div>
      </article>
    `;
  }

  function renderGrid(list) {
    const grid = $("#grid");
    if (!grid) return;
    if (!list.length) {
      grid.innerHTML = `<article class="card" style="grid-column:1/-1;text-align:center">
        No hay productos disponibles.
      </article>`;
      return;
    }
    grid.innerHTML = list.map(cardHTML).join("");
  }

  function showGridError(msg, detail = "") {
    const grid = $("#grid");
    if (grid) {
      grid.innerHTML = `<article class="card" style="grid-column:1/-1">
        <strong>${msg}</strong><br><small style="color:#6b7280">${detail}</small>
      </article>`;
    }
    console.error("[HOME]", msg, detail);
  }

  async function loadProducts() {
    const endpoint = "/api/products/?format=json";
    const grid = $("#grid");
    if (grid) grid.innerHTML = `<article class="card" style="grid-column:1/-1">Cargando…</article>`;

    try {
      const r = await fetch(endpoint, { headers: { "Accept": "application/json" } });
      const text = await r.text();
      console.log("[HOME] GET", endpoint, r.status);

      if (text.trim().startsWith("<")) {
        return showGridError("La API devolvió HTML (¿redirección a login?).", endpoint);
      }

      const data = JSON.parse(text);
      const rows = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
      if (!rows.length) {
        return showGridError("No llegaron productos.", "Verifica que existan registros y que is_active=True");
      }

      PRODUCTS = rows.map(normalizeProduct);
      renderGrid(PRODUCTS);
    } catch (err) {
      showGridError("Error cargando productos.", String(err));
    }
  }

  // ==== Filtro de tabs ====
  function filterByCategory(cat) {
    if (!cat) { renderGrid(PRODUCTS); return; }
    if (cat.toLowerCase() === "ofertas") {
      renderGrid(PRODUCTS.filter(p => /oferta|descuento|promo/i.test(p.description || "")));
    } else {
      renderGrid(PRODUCTS.filter(p => (p.category_name || "").toLowerCase() === cat.toLowerCase()));
    }
  }
  $$(".tab").forEach(btn => {
    btn.addEventListener("click", () => {
      $$(".tab").forEach(b => b.setAttribute("aria-selected", "false"));
      btn.setAttribute("aria-selected", "true");
      filterByCategory(btn.dataset.category || "");
    });
  });

  // ==== Búsqueda opcional (#q en header) ====
  $("#q")?.addEventListener("input", e => {
    const t = e.target.value.trim().toLowerCase();
    renderGrid(PRODUCTS.filter(p =>
      (p.name || "").toLowerCase().includes(t) ||
      (p.category_name || "").toLowerCase().includes(t)
    ));
  });

  // ==== Delegación: Agregar / Detalles ====
  document.addEventListener("click", (e) => {
    const add = e.target.closest(".btn-primary[data-sku]");
    if (add) {
      const name  = add.dataset.name || "Producto";
      const price = Number(add.dataset.price || 0);
      CartModal.open({
        name, price,
        onOk(qty) { Cart.add({ sku: add.dataset.sku, name, price, qty }); }
      });
      const old = add.textContent; add.textContent = "✓ Agregado"; add.disabled = true;
      setTimeout(() => { add.textContent = old; add.disabled = false; }, 1000);
      return;
    }
    const detId = e.target.dataset.det;
    if (detId) {
      const p = PRODUCTS.find(x => String(x.id) === String(detId));
      if (!p) return;
      alert(`${p.name}\n\n${p.description || "Sin descripción."}`);
    }
  });

  // ==== Init ====
  document.addEventListener("DOMContentLoaded", () => {
    initNavDropdowns();
    Cart.render();
    loadProducts();
  });

  // Exponer por si quieres usar desde consola
  window.TX = Object.assign(window.TX || {}, { Cart, loadProducts });

})();
