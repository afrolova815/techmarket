function getCookie(name){var value='; ' + document.cookie;var parts=value.split('; ' + name + '=');if(parts.length===2){return parts.pop().split(';').shift();}}
document.addEventListener('DOMContentLoaded',function(){
  const csrfToken=getCookie('csrftoken');
  function computeTotal(){
    var sum = 0;
    document.querySelectorAll('.item-sum').forEach(function(el){
      var v = parseFloat(el.textContent.replace(',','.'));
      if(!isNaN(v)){ sum += v; }
    });
    return sum;
  }
  (function ensureTotalBlock(){
    var totalElInit = document.getElementById('order-total-amount');
    var inlineGroup = document.querySelector('#orderitem_set-group') || document.querySelector('.inline-group');
    if(inlineGroup){
      var wrap = document.querySelector('.order-total-wrapper');
      if(!wrap){
        wrap = document.createElement('div');
        wrap.className = 'order-total-wrapper';
        var label = document.createElement('span');
        label.className = 'order-total-label';
        label.textContent = 'Итоговая сумма: ';
        wrap.appendChild(label);
        var totalNode = totalElInit || document.createElement('div');
        if(!totalNode.id){ totalNode.id = 'order-total-amount'; }
        var currentTotal = computeTotal();
        totalNode.textContent = currentTotal.toFixed(2);
        wrap.appendChild(totalNode);
        var anchor = document.querySelector('.order-add-item-block') || inlineGroup;
        anchor.parentNode.insertBefore(wrap, anchor.nextSibling);
      } else {
        var totalNode = document.getElementById('order-total-amount');
        if(totalNode){ totalNode.textContent = computeTotal().toFixed(2); }
      }
    }
  })();
  function postUpdateQuantity(itemId, qty){
    var p = window.location.pathname;
    var m = p.match(/^(\/admin\/[^\/]+\/order)\//);
    var base = m ? m[1] : '/admin/catalog/order';
    var form = new FormData();
    form.append('quantity', String(qty));
    return fetch(base + '/update-item/' + itemId + '/', { method:'POST', headers:{'X-CSRFToken':csrfToken}, body: form }).then(function(r){ return r.json() });
  }
  function showConfirm(itemId){
    const overlay=document.createElement('div');
    overlay.style.position='fixed';overlay.style.inset='0';overlay.style.background='rgba(0,0,0,0.3)';overlay.style.zIndex='9999';
    const modal=document.createElement('div');
    modal.style.maxWidth='420px';modal.style.margin='10% auto';modal.style.background='#fff';modal.style.border='1px solid #e2e8f0';modal.style.borderRadius='8px';modal.style.padding='16px';
    const title=document.createElement('h3');title.textContent='Подтверждение удаления';title.style.margin='0 0 8px 0';
    const text=document.createElement('p');text.textContent='Вы действительно хотите удалить товар из заказа?';
    const actions=document.createElement('div');actions.style.display='flex';actions.style.justifyContent='flex-end';actions.style.gap='8px';actions.style.marginTop='12px';
    const cancel=document.createElement('button');cancel.textContent='Отмена';cancel.style.padding='8px 12px';
    const del=document.createElement('button');del.textContent='Удалить';del.style.padding='8px 12px';del.style.background='#e53e3e';del.style.color='#fff';del.style.border='none';del.style.borderRadius='4px';
    cancel.addEventListener('click',function(){document.body.removeChild(overlay)});
    del.addEventListener('click',function(){
      var p = window.location.pathname;
      var m = p.match(/^(\/admin\/[^\/]+\/order)\//);
      var base = m ? m[1] : '/admin/catalog/order';
      fetch(base + '/delete-item/' + itemId + '/',{
        method:'POST',
        headers:{'X-CSRFToken':csrfToken}
      }).then(function(r){return r.json()}).then(function(data){
        if(data && data.success){ window.location.reload() } else { alert('Ошибка удаления') }
      }).catch(function(){ alert('Ошибка сети') })
    });
    actions.appendChild(cancel);actions.appendChild(del);
    modal.appendChild(title);modal.appendChild(text);modal.appendChild(actions);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
  }
  document.querySelectorAll('.inline-delete-btn').forEach(function(btn){
    btn.addEventListener('click',function(){
      const itemId=this.getAttribute('data-item-id');
      showConfirm(itemId);
    })
  });

  document.querySelectorAll('.inline-qty').forEach(function(wrap){
    var itemId = wrap.getAttribute('data-item-id');
    var input = wrap.querySelector('.inline-qty-input');
    function trySave(){
      var qty = parseInt(input.value, 10);
      if(!qty || qty < 1){ alert('Количество должно быть >= 1'); return; }
      postUpdateQuantity(itemId, qty).then(function(data){
        if(data && data.success){
          var sumEl = document.querySelector('.item-sum[data-item-id="' + itemId + '"]');
          if(sumEl){ sumEl.textContent = data.item_sum; }
          var totalEl = document.getElementById('order-total-amount');
          if(totalEl){ totalEl.textContent = data.order_total; }
          else {
            // fallback recompute if server didn't return element
            var wrap = document.querySelector('.order-total-wrapper');
            if(!wrap){
              ensureTotalBlock && ensureTotalBlock();
            } else {
              var totalNode = document.getElementById('order-total-amount');
              if(totalNode){ totalNode.textContent = computeTotal().toFixed(2); }
            }
          }
        } else {
          alert('Ошибка сохранения');
        }
      }).catch(function(){ alert('Ошибка сети') });
    }
    input.addEventListener('change', trySave);
    input.addEventListener('blur', trySave);
    input.addEventListener('keydown', function(e){ if(e.key==='Enter'){ e.preventDefault(); trySave(); } });
  });
});
