function notifyUser(msg){alert(msg)}
function closeModal(id){const el=document.getElementById(id);if(el)el.classList.remove('show')}
document.querySelectorAll('[data-tab]').forEach(btn=>btn.addEventListener('click',()=>{
 document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b===btn));
 document.querySelectorAll('#register,#login').forEach(f=>f.classList.toggle('hidden',f.id!==btn.dataset.tab));
}));
const requestedTab=new URLSearchParams(window.location.search).get('tab');
if(requestedTab==='login'){
 const loginTab=document.querySelector('[data-tab="login"]');
 if(loginTab)loginTab.click();
}
document.querySelectorAll('[data-open]').forEach(btn=>btn.addEventListener('click',()=>{
 const kind=btn.dataset.open, modal=document.getElementById('transactionModal');
 if(!modal)return;
 document.getElementById('transactionKind').value=kind;
 document.getElementById('transactionTitle').textContent=kind==='deposit'?'Deposit Funds':'Withdraw Funds';
 document.getElementById('txMessage').textContent='';
 modal.classList.add('show');
}));
document.querySelectorAll('[data-amount]').forEach(btn=>btn.addEventListener('click',()=>document.getElementById('amount').value=btn.dataset.amount));
const txForm=document.getElementById('transactionForm');
if(txForm)txForm.addEventListener('submit',async e=>{
 e.preventDefault();const msg=document.getElementById('txMessage');
 try{const res=await fetch('/transaction',{method:'POST',body:new FormData(txForm)});const data=await res.json();msg.textContent=data.message;if(data.ok){msg.style.color='#078e89';txForm.querySelector('button[type=submit]').textContent='Request Recorded';}else{msg.style.color='#b42318';}}
 catch(err){msg.textContent='Could not save request. Please try again.';msg.style.color='#b42318';}
});
const slides=[['Invest Smart<br>Live Healthy','with PIMCO Investment Platform. Grow your future with informed choices.'],['Health and Future','Explore medical equipment and learn about healthy living.'],['Together for Uganda','Building a healthier future starts with informed choices.']];
let slide=0;setInterval(()=>{const h=document.getElementById('heroTitle');if(!h)return;slide=(slide+1)%slides.length;h.innerHTML=slides[slide][0];},4200);
