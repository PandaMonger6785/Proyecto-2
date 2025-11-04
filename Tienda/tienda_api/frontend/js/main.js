/* ==== Utils ==== */
const MXN = new Intl.NumberFormat("es-MX",{style:"currency",currency:"MXN"});
const $  = (s,c=document)=>c.querySelector(s);
const $$ = (s,c=document)=>Array.from(c.querySelectorAll(s));

/* ==== Placeholder img ==== */
const PLACEHOLDER = 'data:image/svg+xml;utf8,'+encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="560">
    <rect width="100%" height="100%" fill="#e5e7eb"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
          font-family="Arial" font-size="24" fill="#9ca3af">Imagen pendiente</text>
  </svg>`
);

/* ===============================
   NAV: dropdowns (Mi cuenta / Carrito)
================================= */
function initNavDropdowns(){
  const items=$$('.has-dd'); if(!items.length) return;
  const closeAll=()=>items.forEach(i=>{
    i.classList.remove('open');
    i.querySelector('.dd-toggle')?.setAttribute('aria-expanded','false');
  });
  items.forEach(item=>{
    const btn=item.querySelector('.dd-toggle'); if(!btn) return;
    btn.addEventListener('click',e=>{
      e.preventDefault();
      const on=item.classList.toggle('open');
      btn.setAttribute('aria-expanded', on?'true':'false');
      items.filter(i=>i!==item).forEach(i=>{
        i.classList.remove('open');
        i.querySelector('.dd-toggle')?.setAttribute('aria-expanded','false');
      });
    });
  });
  document.addEventListener('click',e=>{ if(!e.target.closest('.has-dd')) closeAll(); });
  document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeAll(); });
}

/* ===============================
   Carrito (localStorage)
================================= */
const CART_KEY="cart_items_v1";
const Cart={
  all(){ try{return JSON.parse(localStorage.getItem(CART_KEY))||[]}catch{return[]} },
  save(xs){ localStorage.setItem(CART_KEY, JSON.stringify(xs)); },
  add(it){
    const xs=Cart.all();
    const ix=xs.findIndex(x=>x.sku===it.sku && x.price===it.price);
    if(ix>=0){ xs[ix].qty+=it.qty; xs[ix].subtotal=xs[ix].qty*xs[ix].price; }
    else{ xs.push({...it, subtotal: it.qty*it.price}); }
    Cart.save(xs); Cart.render();
  },
  remove(sku){ Cart.save(Cart.all().filter(x=>x.sku!==sku)); Cart.render(); },
  clear(){ Cart.save([]); Cart.render(); },
  count(){ return Cart.all().reduce((a,b)=>a+b.qty,0); },
  total(){ return Cart.all().reduce((a,b)=>a+b.subtotal,0); },
  render(){
    const list=$('#cartItems'), badge=$('#cartBadge'), total=$('#cartTotal');
    if(!list||!badge||!total) return;
    const items=Cart.all();
    list.innerHTML = items.length ? "" : `<div class="cart-item"><div>No hay productos en el carrito.</div></div>`;
    items.forEach(it=>{
      const row=document.createElement('div'); row.className='cart-item';
      row.innerHTML=`
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
    badge.textContent=Cart.count();
    total.textContent='Total: '+MXN.format(Cart.total());
  }
};
document.addEventListener('click',e=>{
  const btn=e.target.closest('.remove[data-sku]'); if(!btn) return;
  Cart.remove(btn.dataset.sku);
});

/* ===============================
   Modal de cantidad (con fallback)
================================= */
function makeCartModal(){
  const root=$('#qtyModal');
  if(!root){
    // Fallback simple con prompt/confirm si no tienes el modal en el DOM
    return {
      open({name,price,onOk}){
        let qty=prompt(`¿Cuántas unidades de "${name}"?`,"1");
        if(qty===null) return;
        qty=parseInt(qty,10);
        if(isNaN(qty)||qty<=0){alert('Cantidad no válida.');return;}
        const total=price*qty;
        if(confirm(`Unitario: ${MXN.format(price)}\nCantidad: ${qty}\nTotal: ${MXN.format(total)}\n\n¿Agregar al carrito?`)){
          onOk(qty);
        }
      }
    };
  }
  const nameEl=$('#cmName'), unitEl=$('#cmUnit'), qtyEl=$('#cmQty'), totalEl=$('#cmTotal');
  const okBtn=$('#cmConfirm');
  let state={name:'',price:0,onOk:()=>{}};
  const updateTotal=()=>{ const q=Math.max(1, parseInt(qtyEl.value||"1",10)); totalEl.textContent=MXN.format(state.price*q); };
  qtyEl?.addEventListener('input', updateTotal);
  root.addEventListener('click',e=>{ if(e.target.dataset.close) { root.classList.add('hidden'); root.setAttribute('aria-hidden','true'); }});
  okBtn?.addEventListener('click',()=>{
    const q=Math.max(1, parseInt(qtyEl.value||"1",10));
    root.classList.add('hidden'); root.setAttribute('aria-hidden','true');
    state.onOk(q);
  });
  return {
    open({name,price,onOk}){
      state={name,price,onOk};
      nameEl.textContent=name;
      unitEl.textContent=MXN.format(price);
      qtyEl.value=1; updateTotal();
      root.classList.remove('hidden'); root.setAttribute('aria-hidden','false');
    }
  };
}
const CartModal=makeCartModal();

/* ===============================
   Productos desde la API
================================= */
let PRODUCTS = [];

function cardHTML(p){
  const img = p.image || PLACEHOLDER;            // ← NO antepongas /static/
  const cat = p.category_name || p.category || 'Producto';
  const price = Number(p.price || 0);
  return `
    <article class="card">
      <span class="badge">${cat}</span>
      <img src="${img}" alt="${p.name}" onerror="this.src='${PLACEHOLDER}'">
      <h3>${p.name}</h3>
      <div class="price">${MXN.format(price)}</div>
      <p>${p.description || ''}</p>
      <div class="actions">
        <button class="btn btn-primary" data-sku="${p.slug}" data-name="${p.name}" data-price="${price}">Agregar al carrito</button>
        <button class="btn btn-ghost" data-det="${p.id}">Detalles</button>
      </div>
    </article>
  `;
}

function renderGrid(list){
  const grid = $('#grid');
  if(!grid) return;
  if(!list.length){
    grid.innerHTML = `<article class="card" style="grid-column:1/-1;text-align:center">No hay productos disponibles.</article>`;
    return;
  }
  grid.innerHTML = list.map(cardHTML).join('');
}

async function loadProducts(){
  const endpoint = "/api/products/";  // tu router DRF
  const grid = $('#grid');
  if(grid) grid.innerHTML = "Cargando productos…";
  try{
    const r = await fetch(endpoint, {headers:{'Accept':'application/json'}});
    if(!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    // DRF por defecto devuelve lista; si usas paginación, ajusta a data.results
    PRODUCTS = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
    renderGrid(PRODUCTS);
  }catch(err){
    console.error('Error cargando productos:', err);
    if(grid) grid.innerHTML = `
      <article class="card" style="grid-column:1/-1">
        No se pudieron cargar los productos desde <code>${endpoint}</code>.
      </article>`;
  }
}

/* ==== Filtro de tabs (Todos/Ofertas) ==== */
function filterByCategory(cat){
  if(!cat){ renderGrid(PRODUCTS); return; }
  if(cat.toLowerCase()==='ofertas'){
    renderGrid(PRODUCTS.filter(p => /oferta|descuento|promo/i.test(p.description||'')));
  }else{
    renderGrid(PRODUCTS.filter(p => (p.category_name||'').toLowerCase()===cat.toLowerCase()));
  }
}
$$('.tab').forEach(btn=>{
  btn.addEventListener('click',()=>{
    $$('.tab').forEach(b=>b.setAttribute('aria-selected','false'));
    btn.setAttribute('aria-selected','true');
    filterByCategory(btn.dataset.category||'');
  });
});

/* ==== Búsqueda (usa #q que ya existe en tu header) ==== */
$('#q')?.addEventListener('input', e=>{
  const t = e.target.value.trim().toLowerCase();
  const base = PRODUCTS;
  renderGrid(base.filter(p =>
    (p.name||'').toLowerCase().includes(t) ||
    (p.category_name||'').toLowerCase().includes(t)
  ));
});

/* ==== Delegación: Agregar al carrito y detalles ==== */
document.addEventListener('click',(e)=>{
  // Agregar
  const add=e.target.closest('.btn-primary[data-sku]');
  if(add){
    const name = add.dataset.name || 'Producto';
    const price = Number(add.dataset.price || 0);
    CartModal.open({
      name, price,
      onOk(qty){ Cart.add({ sku: add.dataset.sku, name, price, qty }); }
    });
    const old=add.textContent; add.textContent='✓ Agregado'; add.disabled=true;
    setTimeout(()=>{ add.textContent=old; add.disabled=false; },1000);
    return;
  }
  // Detalles (si tienes modal de detalles)
  const detId = e.target.dataset.det;
  if(detId){
    const p = PRODUCTS.find(x=>String(x.id)===String(detId));
    if(!p) return;
    alert(`${p.name}\n\n${p.description||'Sin descripción.'}`);
  }
});

/* ==== Init ==== */
document.addEventListener('DOMContentLoaded', ()=>{
  initNavDropdowns();
  Cart.render();
  loadProducts();
});
