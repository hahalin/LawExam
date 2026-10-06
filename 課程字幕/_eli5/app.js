/* ELI5 課程頁共用腳本：全部展開/收合、「我懂了」存 localStorage、進度條 */
(function(){
  var lesson = document.body.dataset.lesson || location.pathname;
  var key = 'eli5:' + lesson;
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch(e){}

  function save(){ try { localStorage.setItem(key, JSON.stringify(saved)); } catch(e){} }
  function refresh(){
    var n = cards.filter(function(c){ return c.classList.contains('done'); }).length;
    var t = document.querySelector('.progress .txt');
    var b = document.querySelector('.progress .bar i');
    if (t) t.textContent = '懂了 ' + n + ' / ' + cards.length;
    if (b) b.style.width = (cards.length ? n / cards.length * 100 : 0) + '%';
  }

  cards.forEach(function(card){
    var id = card.id;
    var box = card.querySelector('input[type=checkbox]');
    if (!box) return;
    if (saved[id]) { box.checked = true; card.classList.add('done'); }
    box.addEventListener('change', function(){
      card.classList.toggle('done', box.checked);
      if (box.checked) saved[id] = 1; else delete saved[id];
      save(); refresh();
    });
  });

  function setAll(open){
    document.querySelectorAll('.card details').forEach(function(d){ d.open = open; });
  }
  var ex = document.getElementById('expand-all'); if (ex) ex.addEventListener('click', function(){ setAll(true); });
  var co = document.getElementById('collapse-all'); if (co) co.addEventListener('click', function(){ setAll(false); });
  var rs = document.getElementById('reset-done'); if (rs) rs.addEventListener('click', function(){
    saved = {}; save();
    cards.forEach(function(c){ c.classList.remove('done'); var b=c.querySelector('input[type=checkbox]'); if(b) b.checked=false; });
    refresh();
  });

  refresh();
})();
