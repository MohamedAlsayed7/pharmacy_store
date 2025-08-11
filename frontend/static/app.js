async function loadProducts(){
  const resp = await fetch('../data/medicines.json');
  const meds = await resp.json();
  const container = document.getElementById('products');
  meds.forEach(m => {
    const div = document.createElement('div');
    div.className = 'card';
    div.innerHTML = `
      <img src="${m.image}" alt="${m.name}" />
      <h3>${m.name}</h3>
      <p>${m.description}</p>
      <div class="price">${m.price_egp} EGP</div>
      <div class="actions">
        <input type="number" min="0" value="0" data-id="${m.id}" class="qty" />
        <button data-id="${m.id}" class="addBtn">Add</button>
      </div>
    `;
    container.appendChild(div);
  });
  attachEvents();
}

function attachEvents(){
  document.querySelectorAll('.addBtn').forEach(b => b.addEventListener('click', (e) => {
    const id = e.target.dataset.id;
    const qtyInput = document.querySelector(`input.qty[data-id="${id}"]`);
    const q = parseInt(qtyInput.value) || 0;
    if(q>0) addToCart(id,q);
  }));
  document.getElementById('whatsappBtn').addEventListener('click', sendWhatsApp);
  document.getElementById('submitServerBtn').addEventListener('click', submitServer);
}

let products = [];
let cart = {};
async function ensureProducts(){
  if(products.length===0){
    const resp = await fetch('../data/medicines.json');
    products = await resp.json();
  }
  return products;
}

function addToCart(id, qty){
  ensureProducts().then(() => {
    const p = products.find(x=>x.id===id);
    if(!p) return;
    if(cart[id]) cart[id].qty += qty; else cart[id] = {item:p, qty:qty};
    renderCart();
  });
}

function renderCart(){
  const el = document.getElementById('cartItems');
  el.innerHTML='';
  let total = 0;
  Object.values(cart).forEach(c => {
    const div = document.createElement('div');
    div.innerHTML = `<strong>${c.item.name}</strong> x ${c.qty} — ${ (c.item.price_egp*c.qty).toFixed(2) } EGP`;
    el.appendChild(div);
    total += c.item.price_egp*c.qty;
  });
  document.getElementById('cartTotal').innerText = 'Total: ' + total.toFixed(2) + ' EGP';
}

function buildOrderText(name, phone, address){
  let text = `New order from: ${name}\nPhone: ${phone}\nAddress: ${address}\nItems:\n`;
  let total = 0;
  Object.values(cart).forEach(c => {
    text += `- ${c.item.name} (x${c.qty}) - ${ (c.item.price_egp*c.qty).toFixed(2) } EGP\n`;
    total += c.item.price_egp*c.qty;
  });
  text += `Total: ${total.toFixed(2)} EGP`;
  return encodeURIComponent(text);
}

function sendWhatsApp(){
  const name = document.getElementById('custName').value || 'No name';
  const phone = document.getElementById('custPhone').value || 'No phone';
  const address = document.getElementById('custAddress').value || 'No address';
  const msg = buildOrderText(name, phone, address);
  const phoneNumber = '201069264028'; // your number in international format
  const waLink = `https://wa.me/${phoneNumber}?text=${msg}`;
  window.open(waLink, '_blank');
}

async function submitServer(){
  const name = document.getElementById('custName').value || 'No name';
  const phone = document.getElementById('custPhone').value || 'No phone';
  const address = document.getElementById('custAddress').value || 'No address';
  const items = Object.values(cart).map(c=>({id:c.item.id, name:c.item.name, qty:c.qty, price:c.item.price_egp}));
  if(items.length===0){ alert('Cart is empty'); return; }
  const payload = {name, phone, address, items};
  const resp = await fetch('../backend/api/orders', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  const res = await resp.json();
  document.getElementById('status').innerText = res.message || 'Sent';
  cart = {}; renderCart();
}

loadProducts();
