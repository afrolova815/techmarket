function getCookie(name){var value='; ' + document.cookie;var parts=value.split('; ' + name + '=');if(parts.length===2){return parts.pop().split(';').shift();}}
document.addEventListener('DOMContentLoaded',function(){
  const csrfToken=getCookie('csrftoken');
  function postUpdateDiscount(productId, percent){
    var p = window.location.pathname;
    var m = p.match(/^(\/admin\/[^\/]+\/product)\//);
    var base = m ? m[1] : '/admin/catalog/product';
    var form = new FormData();
    form.append('percent', String(percent));
    return fetch(base + '/update-discount/' + productId + '/', { method:'POST', headers:{'X-CSRFToken':csrfToken}, body: form }).then(function(r){ return r.json() });
  }
  document.querySelectorAll('.discount-editor').forEach(function(wrap){
    var productId = wrap.getAttribute('data-product-id');
    var input = wrap.querySelector('.discount-input');
    function trySave(){
      var val = parseInt(input.value, 10);
      if(isNaN(val) || val < 0){ val = 0; }
      if(val > 99){ val = 99; }
      postUpdateDiscount(productId, val).then(function(data){
        if(data && data.success){
          var row = wrap.closest('tr');
          if(row){
            var priceCell = row.querySelector('td.field-price');
            var oldPriceCell = row.querySelector('td.field-old_price');
            if(priceCell && data.price){
              var priceInput = priceCell.querySelector('input');
              if(priceInput){ priceInput.value = data.price; }
              else { priceCell.textContent = data.price; }
            }
            if(oldPriceCell){
              oldPriceCell.textContent = data.old_price || '';
            }
          }
        } else { alert('Ошибка сохранения'); }
      }).catch(function(){ alert('Ошибка сети'); });
    }
    input.addEventListener('change', trySave);
    input.addEventListener('blur', trySave);
    input.addEventListener('keydown', function(e){ if(e.key==='Enter'){ e.preventDefault(); trySave(); } });
  });
});
